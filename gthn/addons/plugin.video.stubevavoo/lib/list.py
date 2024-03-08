    # uncompyle6 version 3.6.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Sep 30 2020, 13:38:04) 
# [GCC 7.5.0]
# Embedded file name: ./lib/lists.py
# Compiled at: 2019-03-11 05:02:19
import utils, xbmc, urllib2, os
ACTIONS = {'kids': 'Kinder', 
   'erotic': 'Erotik', 
   'mediathek': 'Mediatheken'}

def kids(params):
    iconBase = 'special://home/addons/' + utils.addonID + '/resources/kids/'
    utils.addDir('Kinderfilme', 'plugin://plugin.video.vavooto/?action=indexMovie&genre=Familie,Kinder,Jugend,Trickfilm&type=movie', 'DefaultMovies.png')
    utils.addDir('Kinderserien', 'plugin://plugin.video.vavooto/?action=indexSerie&genre=Familie,Kinder,Kinderserie,Jugend,Trickfilm&type=serie', 'DefaultTVShows.png')
    utils.addDir('Nickelodeon', 'plugin://plugin.video.nick_de/?mode=listShows&page=1&url=http%3a%2f%2fwww.nick.de%2fvideos', xbmc.translatePath(iconBase + 'iconNick.png'))
    utils.addDir('Nick Junior', 'plugin://plugin.video.nick_de/?mode=nickJrMain', xbmc.translatePath(iconBase + 'iconNick.png'))
    utils.addDir('KIKA+', 'plugin://plugin.video.kika_de', xbmc.translatePath(iconBase + 'iconKIKA.png'))
    utils.addDir('Sesamstra\xc3\x9fe', 'plugin://plugin.video.sesamstrasse_de', xbmc.translatePath(iconBase + 'iconSS.png'))


def erotic(params):

    def url(plugin, u):
        fields = ('title', 'director', 'genre', 'type', 'icon', 'url')
        params = ('&').join(k + ':' + u[k] for k in fields)
        params = urllib2.quote(params.encode('ascii', 'ignore'))
        utils.addDir(u['title'], 'plugin://' + plugin + '/?url=' + params, u['special_icon'])

    addonpath = os.path.split(os.path.dirname(__file__))[0]
    url('plugin.video.videodevil', {'title': 'Ah', 
       'director': 'VideoDevil', 
       'genre': 'Ah', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/ahme.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/ahme.png', 
       'url': 'ahme.com.cfg'})
    url('plugin.video.videodevil', {'title': 'EPORNER', 
       'director': 'VideoDevil', 
       'genre': 'EPORNER', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/eporner.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/eporner.png', 
       'url': 'eporner.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Faapy', 
       'director': 'VideoDevil', 
       'genre': 'faapy.com', 
       'type': 'rss', 
       'icon': 'http://faapy.com/images_new/logo.png', 
       'special_icon': 'http://faapy.com/images_new/logo.png', 
       'url': 'faapy.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Fapdu', 
       'director': 'VideoDevil', 
       'genre': 'fapdu', 
       'type': 'rss', 
       'icon': 'http://cdn-w.fapdu.com/FapDu/fo1-01.png', 
       'special_icon': 'http://cdn-w.fapdu.com/FapDu/fo1-01.png', 
       'url': 'fapdu.com.cfg'})
    url('plugin.video.videodevil', {'title': 'GirlfriendVideos', 
       'director': 'VideoDevil', 
       'genre': 'GirlfriendVideos', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/gfvideos.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/gfvideos.png', 
       'url': 'gfvideos.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Hentaigasm', 
       'director': 'VideoDevil', 
       'genre': 'hentaigasm', 
       'type': 'rss', 
       'icon': 'http://hentaigasm.com/wp-content/themes/detube/images/logo.png', 
       'special_icon': 'http://hentaigasm.com/wp-content/themes/detube/images/logo.png', 
       'url': 'hentaigasm.com.cfg'})
    url('plugin.video.videodevil', {'title': 'MadThumbs', 
       'director': 'VideoDevil', 
       'genre': 'madthumbs', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/madthumbs.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/madthumbs.png', 
       'url': 'madthumbs.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Motherless', 
       'director': 'VideoDevil', 
       'genre': 'Motherless', 
       'type': 'rss', 
       'icon': 'http://motherless.com/images/logo8888.gif', 
       'special_icon': 'http://motherless.com/images/logo8888.gif', 
       'url': 'motherless.com.cfg'})
    url('plugin.video.videodevil', {'title': 'MovieFap', 
       'director': 'VideoDevil', 
       'genre': 'MovieFap', 
       'type': 'rss', 
       'icon': 'http://www.moviefap.com/images/logo.gif', 
       'special_icon': 'http://www.moviefap.com/images/logo.gif', 
       'url': 'moviefap.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Pornburst.xxx', 
       'director': 'VideoDevil', 
       'genre': 'Pornbust.xxx', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/pornburst.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/pornburst.png', 
       'url': 'pornburst.xxx.cfg'})
    url('plugin.video.videodevil', {'title': 'Porn.com', 
       'director': 'VideoDevil', 
       'genre': 'Porn.com', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/porn.com-logo.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/porn.com-logo.png', 
       'url': 'porn.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Pornhd', 
       'director': 'VideoDevil', 
       'genre': 'pornhd', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/pornhdlogo.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/pornhdlogo.png', 
       'url': 'pornhd.com.cfg'})
    url('plugin.video.videodevil', {'title': 'Pornhub', 
       'director': 'VideoDevil', 
       'genre': 'Pornhub', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/pornhub.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/pornhub.png', 
       'url': 'pornhub.com.cfg'})
    url('plugin.video.videodevil', {'title': 'SpankWire', 
       'director': 'VideoDevil', 
       'genre': 'SpankWire', 
       'type': 'rss', 
       'icon': addonpath + '/plugin.video.videodevil/resources/images/spankwire.png', 
       'special_icon': 'special://home/addons/plugin.video.videodevil/resources/images/spankwire.png', 
       'url': 'spankwire.com.cfg'})


def mediathek(params):
    iconBase = 'special://home/addons/'
    utils.addDir('ARD Mediathek', 'plugin://plugin.video.ardmediathek_de', iconBase + utils.addonID + '/resources/ardmediathek.png')
    utils.addDir('ATV.at', 'plugin://plugin.video.atv_at', iconBase + 'plugin.video.atv_at/icon.png')
    utils.addDir('Arte.tv', 'plugin://plugin.video.arte_tv', iconBase + 'plugin.video.arte_tv/icon.png')
    utils.addDir('Doku5.com', 'plugin://plugin.video.doku5.com', iconBase + 'plugin.video.doku5.com/icon.png')
    utils.addDir('3Sat', 'plugin://plugin.video.mediathek/?type=3Sat', iconBase + 'plugin.video.mediathek/resources/logos/png/3Sat.png')
    utils.addDir('KI.KA', 'plugin://plugin.video.mediathek/?type=KI.KA', iconBase + 'plugin.video.mediathek/resources/logos/png/KI.KA-Plus.png')
    utils.addDir('ORF', 'plugin://plugin.video.mediathek/?type=ORF', iconBase + 'plugin.video.mediathek/resources/logos/png/ORF.png')
    utils.addDir('Servus TV', 'plugin://plugin.video.servustv_com', iconBase + utils.addonID + '/resources/mediatheken/iconSTV.png')
