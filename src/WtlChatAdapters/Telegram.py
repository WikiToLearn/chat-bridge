#!/usr/bin/env python3
from WtlChatAdapters.WtlChatAdapter import WtlChatAdapter
import time

import telegram
from telegram.error import NetworkError, Unauthorized

class Telegram(WtlChatAdapter):

    def __init__(self, adapter_name,event_emitter, token):
        WtlChatAdapter.__init__(self,adapter_name,event_emitter)
        self.bot = telegram.Bot(token)

        try:
            self.update_id = self.bot.getUpdates()[0].update_id
        except IndexError:
            self.update_id = None


    def run(self):
        while self.running:
            try:
                for update in self.bot.getUpdates(offset=self.update_id, timeout=10):
                    self.update_id = update.update_id + 1

                    if update.message:
                        chat_id = update.message.chat_id
                        message_event = {"adapter_name":self.adapter_name}
                        message_event['channel_id'] = "{}".format(chat_id)
                        message_event['text'] = update.message.text
                        if len(update.message.from_user.username) > 0:
                            message_event['from'] = update.message.from_user.username
                        else:
                            message_event['from'] = update.message.from_user.id
                        self.event_emitter.emit('message',message_event)
            except NetworkError:
                time.sleep(1)
            except Unauthorized:
                update_id += 1
            time.sleep(1)
        self.stop()

    def send_msg(self,channel_id,msg):
        self.bot.sendMessage(chat_id=channel_id, text=msg)
