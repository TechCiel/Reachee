#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Please create reachee.json from reachee-example.json
or specifie config file in command line like

python3 reachee.py /path/to/config.json
'''
CONFIG = 'reachee.json'

import re
import json
import logging as log
from sys import argv
from time import sleep
from importlib import import_module
import requests
import bs4

# 0 load config
if len(argv)<2: argv.append(CONFIG)
c = {
	'daemon': True,
	'debug': False,
	'interval': 300,
	'channel': 179577,
	'senders': {}
}
c.update(json.load(open(argv[1])))

# 0 set logging
log.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s',
	level=(log.DEBUG if c['debug'] else log.INFO)
)
log.debug(f'Config: {c}')

# 0 load post record
try:
	with open('.reachee','r') as f:
		posted = eval(f.read())
	if not isinstance(posted, list): raise Exception
except:
	log.error('Posted records not found!')
	posted = []

# 0 set variables
baseLAN = 'https://oa.jlu.edu.cn/defaultroot'
baseVPN = 'https://vpn.jlu.edu.cn/https/6a6c7576706e6973746865676f6f64215ebd458ea69e85a6228e6380fc/defaultroot'
baseURL = baseVPN if ('vpns' in c) else baseLAN
probing = 1 if posted else 0
page = 1

# 0 main loop
log.warning('Started')
while True:
	try: 
		log.info(f'Checking page {page}...')
		s = requests.Session()
		
		# 1 login to vpns if required
		if 'vpns' in c: s.post('https://vpn.jlu.edu.cn/do-login', data={
			'auth_type': 'local',
			'username': c['vpns']['account'],
			'password': c['vpns']['password']
		}, timeout=5)

		# 1 fetch channel posts list
		r = s.get(f'{baseURL}/PortalInformation!jldxList.action?channelId={c["channel"]}&startPage={page}', timeout=5)
		# 1 match all links
		posts = bs4.BeautifulSoup(r.content, 'html.parser').find_all(name='a', class_='font14')
		# 1 extract post id
		posts = list(map((lambda x : int(re.search(r'id=(\d+)',x['href'])[1])), posts))
		posts.reverse()
		# 1 reorder posted records
		posted = [x for x in posted if x not in posts] + [x for x in posted if x in posts]
		# 1 filter posts against posted records
		posts = [x for x in posts if x not in posted]
		log.debug(f'Posts: {posts}')

		# 1 probing logic
		if probing and posts:
			if page<10:
				log.info(f'[Probing] page {page} have news, getting earlier...')
				page = page+1
				continue
			else:
				log.info(f'[Probing] reached maximum probing page(10)')
		probing = False

		# 1 process posts
		for pid in posts:
			log.info(f'New Post: {pid}')
			# 2 fetch post content
			r = s.get(f'{baseURL}/PortalInformation!getInformation.action?id={pid}', timeout=5)
			# 2 extract post text
			dom = bs4.BeautifulSoup(r.content, 'html.parser').find(class_='content')
			log.debug(f'DOM: {dom}')
			title = dom.find(class_='content_t').text
			log.info(f'Title: {title}')
			time = dom.find(class_='content_time').contents[0].strip()
			dept = dom.find(class_='content_time').find('span').text
			def innerText(tag):
				if not isinstance(tag, bs4.element.Tag): return str(tag)
				result = ''.join([ innerText(x) for x in tag.contents ])
				if tag.name in ['p', 'br', 'div']: result = f'\n{result}\n'
				return re.sub(r'(\s*\n\s*)+', '\n', result)
			content = innerText(dom.find(class_='content_font')).strip()
			# 2 dispatch to senders
			for (name, configs) in c['senders'].items():
				for config in configs:
					import_module(f'sender.{name}').send(config, {
						'pid': pid,
						'title': title,
						'time': time,
						'dept': dept,
						'content': content,
						'linkLAN': f'{baseLAN}/PortalInformation!getInformation.action?id={pid}',
						'linkVPN': f'{baseVPN}/PortalInformation!getInformation.action?id={pid}'
					})
			# 2 save post record
			posted = (posted+[pid])[-100:]
			try:
				with open('.reachee','w') as f:
					f.write(repr(posted))
			except:
				log.error('Unable to write record file!')
		
		# 1 catch-up logic
		if page>1:
			log.info(f'[Catch-Up] finished with page {page}, moving on...')
			page = page-1
		else:
			if not c['daemon']: exit(0)
			sleep(c['interval'])

	except requests.exceptions.RequestException as e:
		log.info('Network error')
		log.info(repr(e))
		sleep(5)
	except Exception as e:
		log.error('Unexpected error')
		log.error(repr(e))
		sleep(60)
