#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import atexit
import logging as log
from time import sleep
from html import escape
from datetime import date
import requests

def flush(config):
    # prepare config
    c = {'token': '', 'chat': '', 'caption': '\'通知摘要\''}
    c.update(config)
    if not c['token'] or not c['chat']:
        raise Exception('[Telegram Summary] missing parameter')

    c['_buffer'] = f'<b>{date.today().strftime("%Y%m%d")} {eval(c["caption"])}</b>\n\n' + c['_buffer']
    while True:
        try:
            r = requests.post('https://api.telegram.org/bot'+c['token']+'/sendMessage', json={
                'chat_id': c['chat'],
                'text': c['_buffer'],
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }, timeout=5)
            log.debug(f'[Telegram Summary] response: {r.text}')
            if not r.json()['ok']: raise Exception(r.json()['error_code'])
            break
        except requests.exceptions.RequestException as e:
            log.info('[Telegram Summary] network error')
            log.info(repr(e))
            sleep(5)
        except Exception as e:
            log.error('[Telegram Summary] unknown error')
            log.error(repr(e))
            sleep(60)

def send(config, post):
    # check key words
    if any((x in post['title']) for x in config.get('skip', [])):
        log.info('[Telegram Summary] skip word hit')
        return

    # form message
    html = f'<b>{escape(post["title"])}</b> [<a href="{post["linkLAN"]}">OA</a> / <a href="{post["linkVPN"]}">VPN</a>]\n<i>{post["time"][5:]} {post["dept"]}</i>\n\n'
    log.debug(f'[Telegram Summary] html: {html}')

    # save buffer
    if '_buffer' not in config: atexit.register(flush, config)
    config['_buffer'] = config.get('_buffer', '') + html
