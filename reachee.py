#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# use your JLU account to access VPN
JLU_EMAIL   = 'zhaoyy2119'
PASSWORD    = 'PASSWORD'
# bot could be created by @BotFather via Telegram
BOT_TOKEN   = '1089092646:<redacted>'
# add your bot as channel administrator with post privilege
BOT_CHANNEL = '@JLUAnnouncements'
# fetch from which OA news channel
OA_CHANNEL  = '179577'#&startPage=2'
CENSOR_WORD = ['先进技术研究院']
# other settings
INTERVAL    = 10*60
MAX_LENGTH  = 1000
DEBUG       = 0#+1

import re
import requests
from lxml import etree
from time import sleep
import logging
from logging import debug, info, warning, error, critical

logging.basicConfig(level=logging.INFO-10*DEBUG, format='%(asctime)s %(levelname)s %(message)s')
warning('Started.')

try:
	with open('.reachee','r') as f:
		posted = eval(f.read())
	if not isinstance(posted, list): raise Exception
except:
	error('No last post record found!')
	posted = []

while True:
	info('Checking for updates...')
	try: 
		s = requests.Session()
		# vpns.jlu.edu.cn doesn't send intermediate CA certificate, workaround
		s.verify = 'ca.crt'
		
		postPayload = {
			'auth_type': 'local',
			'username': JLU_EMAIL,
			'password': PASSWORD
		}
		r = s.post('https://vpns.jlu.edu.cn/do-login?local_login=true', data=postPayload)

		r = s.get('https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96/defaultroot/PortalInformation!jldxList.action?channelId='+OA_CHANNEL)
		posts = etree.HTML(r.text).xpath('//a[@class="font14"]/@href')
		posts = list(map((lambda x : int(re.search(r'id=(\d+)',x)[1])), posts))
		debug(posts)

		for pid in posts[::-1]:
			if pid in posted: continue
			info(f'New post: {pid}')
			r = s.get(f'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96/defaultroot/PortalInformation!getInformation.action?id={pid}')
			
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
			html = f'<b>{title}</b>\n{time} #{dept}\n{linkLAN}  {linkVPN}\n\n{__import__("html").escape(content)}'
			if len(html) > MAX_LENGTH: html = html[:MAX_LENGTH] + '...'
			info(f'Title: {title}')
			debug(f'Content: {content}')

			postPayload = {
				'chat_id': BOT_CHANNEL,
				'text': html,
				'parse_mode': 'HTML',
				'disable_web_page_preview': True
			}
			r = requests.post('https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage', json=postPayload)
			debug(r.text)
			if not r.json()['ok']: raise Exception('Telegram API Error.')

			posted.append(pid)
			try:
				with open('.reachee','w') as f:
					f.write(repr(posted))
			except:
				error('Unable to write record file!')
	except Exception as e:
		error('Unexpected error happened.')
		error(repr(e))
	sleep(INTERVAL)
