#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import logging as log
from time import sleep
from html import escape
import requests

class FloodException(Exception): pass

def send(config, post):
    # prepare config
    c = {'token': '', 'chat': '', 'maxlength': 1000, 'skip': [], 'censor': []}
    c.update(config)
    if not c['token'] or not c['chat']:
        raise Exception('[Telegram] missing parameter')
    
    # check key words
    if any((x in post['content']) for x in c['skip']):
        log.info('[Telegram] skip word hit')
        return
    if any((x in post['content']) for x in c['censor']):
        log.info('[Telegram] censor word hit')
        post['content'] = ''

    # fixes email addresses and links
    post['content'] = re.sub(r'([!-~]+\@[!-~]+)', ' \\1 ', post['content'])
    post['content'] = re.sub(r'(https?://[!-~]+)', '\\1 ', post['content'])

    # form message
    html = f'<b>{escape(post["title"])}</b>\n'
    html += f'{post["time"]} #{post["dept"]}\n'
    html += f'<a href="{post["linkLAN"]}">校内链接</a>  <a href="{post["linkVPN"]}">VPN链接</a>\n\n'
    html += f'{escape(post["content"])}'
    if len(html) > c['maxlength']: html = html[:c['maxlength']] + '...'
    log.debug(f'[Telegram] html: {html}')

    # call HTTP API
    while True:
        try:
            r = requests.post('https://api.telegram.org/bot'+c['token']+'/sendMessage', json={
                'chat_id': c['chat'],
                'text': html,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }, timeout=5)
            log.debug(f'[Telegram] response: {r.text}')
            if not r.json()['ok']:
                if r.json()['error_code'] == 429:
                    raise FloodException()
                else:
                    raise Exception(r.json()['error_code'])
            break
        except FloodException:
            log.warning('[Telegram] hit rate limit!')
            sleep(30)
        except requests.exceptions.RequestException as e:
            log.info('[Telegram] network error')
            log.info(repr(e))
            sleep(5)
        except Exception as e:
            log.error('[Telegram] unknown error')
            log.error(repr(e))
            sleep(60)
