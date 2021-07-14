#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# use your JLU account to access VPN
USE_VPNS    = True
JLU_EMAIL   = 'zhaoyy2119'
PASSWORD    = 'PASSWORD'
# bot could be created by @BotFather via Telegram
BOT_TOKEN   = '1089092646:<redacted>'
# add your bot as channel administrator with post privilege
BOT_CHANNEL = '@JLUAnnouncements'
# fetch from which OA news channel
OA_CHANNEL  = '179577'
CATCH_UP    = True # for auto catch-up
CENSOR_WORD = ['先进技术研究院']
# other settings
INTERVAL    = 10*60
TIMEOUT     = 10
MAX_LENGTH  = 1000
DEBUG       = 0#+1

import re
import requests
from lxml import etree
from html import escape
from time import sleep
import logging
from logging import debug, info, warning, error, critical
class FloodException(Exception): pass

logging.basicConfig(level=logging.INFO-10*DEBUG, format='%(asctime)s %(levelname)s %(message)s')
warning('Started.')

try:
	with open('.reachee','r') as f:
		posted = eval(f.read())
	if not isinstance(posted, list): raise Exception
except:
	error('No last post record found!')
	posted = []
if USE_VPNS:
	baseURL = 'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96'
else:
	baseURL = 'https://oa.jlu.edu.cn'
probing = CATCH_UP
page = 1

while True:
	info('Checking for updates...')
	try: 
		s = requests.Session()
		
		if USE_VPNS: s.post('https://vpns.jlu.edu.cn/do-login?local_login=true', data={
			'auth_type': 'local',
			'username': JLU_EMAIL,
			'password': PASSWORD
		}, timeout=TIMEOUT)

		r = s.get(f'{baseURL}/defaultroot/PortalInformation!jldxList.action?channelId={OA_CHANNEL}&startPage={page}', timeout=TIMEOUT)
		posts = etree.HTML(r.text).xpath('//a[@class="font14"]/@href')
		posts = list(map((lambda x : int(re.search(r'id=(\d+)',x)[1])), posts))
		posts = [x for x in posts if x not in posted]
		debug(posts)

		if probing:
			if posts:
				info(f'[Probing] page {page} have news, getting earlier...')
				page = page+1
			else:
				info(f'[Probing] no news on page {page}, stop probing and get back.')
				page = max(1, page-1)
				probing = False
			continue

		if page>1 and not posts:
			info(f'[Catch-Up] Finished with page {page}, moving forward...')
			page = page-1
			continue

		for pid in posts[::-1]:
			info(f'New post: {pid}')
			r = s.get(f'{baseURL}/defaultroot/PortalInformation!getInformation.action?id={pid}', timeout=TIMEOUT)
			
			dom = etree.HTML(r.text)
			title = dom.xpath('//div[@class="content_t"]/text()')[0]
			time = dom.xpath('//div[@class="content_time"]/text()')[0].strip()
			dept = dom.xpath('//div[@class="content_time"]/span/text()')[0]
			contentA = '\n'.join(dom.xpath('//div[contains(@class,"content_font")]/text()'))
			contentB = '\n'.join([ ''.join(p.xpath('.//text()')) for p in dom.xpath('//div[contains(@class,"content_font")]//p') ])
			content = (contentB if len(contentA) < len(contentB) else contentA).strip()
			if any(i in content for i in CENSOR_WORD): content = ''
			# fixes email addresses and links
			content = re.sub(r'([!-~]+\@[!-~]+)', ' \\1 ', content)
			content = re.sub(r'(https?://[!-~]+)', '\\1 ', content)
			linkLAN = f'<a href="https://oa.jlu.edu.cn/defaultroot/PortalInformation!getInformation.action?id={pid}">校内链接</a>'
			linkVPN = f'<a href="https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96/defaultroot/PortalInformation!getInformation.action?id={pid}">VPN链接</a>'
			html = f'<b>{escape(title)}</b>\n{time} #{dept}\n{linkLAN}  {linkVPN}\n\n{escape(content)}'
			if len(html) > MAX_LENGTH: html = html[:MAX_LENGTH] + '...'
			info(f'Title: {title}')
			debug(f'Content: {content}')

			r = requests.post('https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage', json={
				'chat_id': BOT_CHANNEL,
				'text': html,
				'parse_mode': 'HTML',
				'disable_web_page_preview': True
			}, timeout=TIMEOUT)
			debug(r.text)
			if not r.json()['ok']:
				if r.json()['error_code'] == 429:
					raise FloodException()
				else:
					raise Exception('Telegram API Error.')

			posted.append(pid)
			try:
				with open('.reachee','w') as f:
					f.write(repr(posted))
			except:
				error('Unable to write record file!')
	except FloodException:
		warning('Telegram API hit rate limit!')
		sleep(60)
		continue
	except Exception as e:
		error('Unexpected error happened.')
		error(repr(e))
		sleep(60)
		continue
	if page==1:	sleep(INTERVAL)
