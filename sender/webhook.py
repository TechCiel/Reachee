#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging as log
from time import sleep
import requests

def send(config, post):
    c = {'url': ''}
    c.update(config)
    if not c['url']:
        raise Exception('[Webhook] missing parameter')

    while True:
        try:
            if c.get('json', False):
                r = requests.post(c['url'], json=post, timeout=10)
            else:
                r = requests.post(c['url'], data=post, timeout=10)
            log.debug(f'[Webhook] response: {r.text}')
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.info('[Webhook] network error')
            log.info(repr(e))
            sleep(5)
        except Exception as e:
            log.error('[Webhook] Unknown Error')
            log.error(repr(e))
            sleep(60)
