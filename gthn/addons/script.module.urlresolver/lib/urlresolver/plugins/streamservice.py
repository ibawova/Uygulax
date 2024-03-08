"""
streamservice urlresolver plugin
Copyright (C) 2012 Lynx187

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re, os
from threading import Thread
from urlresolver import common
from urlresolver.lib import kodi
from urlresolver.resolver import UrlResolver


class StreamserviceResolver(UrlResolver):
    name = "streamservice"
    domains = ["best.streamservice.online", "fast.streamservice.online"]
    pattern = '(?://|\.)((?:best|fast)\.streamservice\.online).*?id=(.*?)$'
    items = []
    __url = domains[1]


    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        self.__url = "https://%s" % host
        chunk_links = self.__get_chunk_links(media_id)
        target_file = kodi.translate_path(os.path.join(kodi.get_profile(), 'pl_streamservice.m3u8'))

        data = '#EXTM3U\n'
        data += '#EXT-X-VERSION:3\n'
        data += '#EXT-X-MEDIA-SEQUENCE:0\n'
        #data += '#EXT-X-ALLOW-CACHE:YES\n' # Kodi always uses 8 seconds buffer for hls streams
        #data += '#EXT-X-TARGETDURATION:8\n' 
        
        for entry in chunk_links:
            data += '#EXTINF:%s,\n' % entry['length']
            data += entry['url'] + '\n'
        
        data += '#EXT-X-ENDLIST'
    
        sw = open(target_file, 'w+') 
        sw.write(data)
        sw.close()
        
        return target_file

    def get_host_and_id(self, url):
        r = re.findall(self.pattern, url)[0]
        if r:
            return (r[0], r[1])
        else:
            return False

    def get_url(self, host, media_id):
        return '%s/public/dist/index.html?id=%s' % (host, media_id)
    
    def __get_chunk_links(self, media_id):
        chunk_data_url = '%s/getChunksData?m3u8File=%s.m3u8' % (self.__url, media_id)
        chunk_data = self.net.http_GET(chunk_data_url).content
        result = re.compile(r'(.*?txt)(.*?)\n', re.MULTILINE).findall(chunk_data)
        
        self.items = []

        if not result:
            return self.items

        time_data = self.__get_time_data(media_id)
        
        threads = []
        
        for chunk_url, time_ids in result:
            process = Thread(target=self._getChunkWorker, args=[chunk_url, time_ids, time_data])
            process.start()
            threads.append(process)
        
        for process in threads:
            process.join()
        
        return sorted(self.items, key=lambda x: x['id'])

    def _getChunkWorker(self, chunk_url, time_ids, time_data):
            try: 
                chunk_id = re.search('(\d+)\.txt', chunk_url).group(1)
            except:
                return
            
            time_parts = re.findall('(\d+)\-\d+\-\d+', time_ids)
            length = 0
            
            for time_id in time_parts:
                length += time_data[time_id]
            
            chunk_url = '%s/getChunkLink?chunkFile=%s' % (self.__url, chunk_url)
            stream_url = self.net.http_GET(chunk_url).content

            item = {}
            item['id'] = int(chunk_id)
            item['url'] = stream_url 
            item['length'] = length 
            self.items.append(item)


    def __get_time_data(self, media_id):
        m3u8_url = '%s/hls/%s/%s.m3u8' % (self.__url, media_id, media_id)
        m3u8_data = self.net.http_GET(m3u8_url).content
        result = re.compile(r'#EXTINF:([^,]+),.*?\n.*?(\d+)\.jpg').findall(m3u8_data)
        items = {}

        if not result:
            return items

        for t, i in result:
            items[i] = float(t)
        
        return items
