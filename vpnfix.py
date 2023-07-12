#!/usr/bin/env python3

from pyrogram import Client, enums, types

app = Client(
    'JLUNewsBot',
    0, '<redacted>',
    bot_token='<redacted>',
    no_updates=True, sleep_threshold=24*60*60,
)
OLD_PREFIXES = [
    'https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96/',  # wrdvpnisthebest!
    'https://webvpn.jlu.edu.cn/https/77726476706e69737468656265737421fff60f962b2526557a1dc7af96/',
    'https://vpn.jlu.edu.cn/https/6a6c7576706e6973746865676f6f64215ebd458ea69e85a6228e6380fc/',  # jluvpnisthegood!
]
NEW_PREFIX = 'https://vpn.jlu.edu.cn/https/44696469646131313237446964696461a579b2620fdde512c84ea96fd9/'  # Didida1127Didida
CHANNEL_ID = 'JLUNews'
MESSAGES = range(13190, 0, -1)
LINK_TEXT = ['VPN链接', 'VPNS', 'VPN']


async def main():
    async with app:
        for msgid in MESSAGES:
            msg: types.Message = await app.get_messages(CHANNEL_ID, msgid)
            if msg.empty or msg.service or msg.forward_date:
                continue
            print(f'processing message {msgid}')
            #print(msg)
            need_fix = False
            if not msg.entities:
                print(msg)
            for entity in msg.entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    if msg.text[entity.offset:entity.offset+entity.length] not in LINK_TEXT:
                        continue
                    for prefix in OLD_PREFIXES:
                        if entity.url.startswith(prefix):
                            entity.url = NEW_PREFIX + entity.url.removeprefix(prefix)
                            need_fix = True
            if need_fix:
                await app.edit_message_text(
                    CHANNEL_ID,
                    msgid, msg.text, entities=msg.entities,
                    disable_web_page_preview=True
                )
                print(f'message {msgid} fixed')


app.run(main())
