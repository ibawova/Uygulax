# -*- coding: utf-8 -*-
import json, requests, os, time, urllib.parse, vavoosigner
from scrapers.modules import source_utils
import resolveurl as resolver
from base64 import b64encode, b64decode 

SESSION = None

def getSession():
	if SESSION is None:
		import requests
		globals()['SESSION'] = requests.session()
	return SESSION


def callApi(action, params, method='GET', headers=None, **kwargs):
	if not headers:
		headers = dict()
	headers['auth-token'] = vavoosigner.getAuthSignature()
	resp = getSession().request(method, ("https://www2.vjackson.info/ccapi/" + action), params=params, headers=headers, **kwargs)
	resp.raise_for_status()
	return resp.json()

def check_302(url):
	try:
		while True:
			host = urllib.parse.urlparse(url).netloc
			headers_dict = {'Host': host}
			r = requests.head(url, allow_redirects=False, headers=headers_dict, timeout=7)
			#print (r.status_code)
			if 300 <= r.status_code <= 400:
				url = r.headers['Location']
			elif 403 == r.status_code:
				return url
			elif 400 <= r.status_code:
				return
			elif 200 == r.status_code:
				return url
			else:
				break
		return
	except:
		return


def callApi2(action, params, **kwargs):
	res = callApi(action, params)
	while True:
		if type(res) is not dict or 'id' not in res or 'data' not in res:
			return res
		import requests
		session = requests.session()
		data = res['data']
		if type(data) is dict and data.get('type') == 'fetch':
			params = data['params']
			body = params.get('body')
			headers = params.get('headers')
			resp = session.request(params.get('method', 'GET').upper(), data['url'], headers={k:v[0] if type(v) in (list, tuple) else v for k, v in list(headers.items())} if headers else None, data=b64decode(body).decode() if body else None, allow_redirects=params.get('redirect', 'follow') == 'follow')
			headers = dict(resp.headers)
			resData = {'status': resp.status_code, 
			   'url': resp.url, 
			   'headers': headers, 
			   'data': b64encode(resp.content).decode("utf-8").replace('\n', '') if data['body'] else None}
			res = callApi('res', {'id': res['id']}, method='POST', json=resData)
		elif type(data) is dict and data.get('error'):
			raise ValueError(data['error'])
		else:
			return data

	return

class source:
	def __init__(self):
		self.priority = 1
		self.language = ['de']
		self.domains = ['vjackson.info']
		self.base_link = 'https://www2.vavoo.to/ccapi/links'
		
	def run(self, titles, year, season=0, episode=0, imdb='', hostDict=None):
		sources = []
		headers = ({'auth-token': vavoosigner.getAuthSignature()})
		if season == 0:
			id = "movie."+str(requests.get(('https://api.themoviedb.org/3/find/{}?api_key=0b529d296545c2545a68db5cb903cd94&external_source=imdb_id').format(imdb)).json()["movie_results"][0]["id"])
		else:
			id = "series."+str(requests.get(('https://api.themoviedb.org/3/find/{}?api_key=0b529d296545c2545a68db5cb903cd94&external_source=imdb_id').format(imdb)).json()["tv_results"][0]["id"])+"."+str(season)+"."+str(episode)+".de"
		params={"id":id}
		links=requests.get(self.base_link,params=params, headers=headers).json()
		
		for link in links:
			hoster = link['url']
			if "720p" in link['name']:
				quality = "720p"
			elif "1080p" in link['name']:
				quality = "1080p"
			else:
				quality = "SD"
			#valid, host = source_utils.is_host_valid(hoster, hostDict)
			#if not valid: continue 
			sources.append({'source': urllib.parse.urlparse(hoster).netloc , 'quality': quality, 'language': 'de', 'url': hoster, 'direct': True, 'debridonly': False})

		return sources
		
		
	def resolve(self, url):
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
		try:
			res = callApi2('open', {'link': url})
			url = check_302(res[0]['url'])
			return url  #+ '|User-Agent=' + user_agent
		except:
			return check_302(url)  #url + '|User-Agent=' + user_agent