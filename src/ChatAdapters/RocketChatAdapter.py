#!/usr/bin/env python3
from libs.RocketChat import RocketChat
from ChatAdapters.ChatAdapter import ChatAdapter
import requests
import time

class RocketChatAdapter(ChatAdapter):

    def __init__(self, adapter_name, event_emitter, baseurl, username, password):
        self.rocketchat = RocketChat(baseurl, username, password)
        ChatAdapter.__init__(self,adapter_name,event_emitter)

    def run(self):
        channels_ids = []
        for room in self.rocketchat.channels_list():
            print(room)
            channels_ids.append(room['_id'])
        channels_last_message_id = {}
        for channel_id in channels_ids:
            messages = self.rocketchat.channels_history(channel_id,count=1)
            if len(messages) > 0:
                channels_last_message_id[channel_id] = messages[0]['_id']

        while self.running:
            try:
                time.sleep(1)
                for channel_id in channels_ids:
                    messages = self.rocketchat.channels_history(channel_id,count=1)
                    for message in messages:
                        if channels_last_message_id[channel_id] != message['_id']:
                            if message['u']['username'] != self.rocketchat.username:
                                message_event = {"adapter_name":self.adapter_name}
                                message_event['channel_id'] = channel_id
                                message_event['from'] = message['u']['username']
                                message_event['text'] = ""
                                if 'attachments' in message:
                                    for attachment in message['attachments']:
                                        if 'text' in attachment and 'author_name' in attachment and 'ts' in attachment and 'author_icon' in attachment:
                                            message_event['text'] = message_event['text'] + "Reply to: '{}' from {}\n".format(attachment['text'],attachment['author_name'])
                                        else:
                                            #{'title': '', 'title_link_download': True, 'title_link': ''} sent file
                                            #{'image_url': '', 'title_link': '', 'title_link_download': True, 'image_dimensions': {'width': 2432, 'height': 3286}, 'title': '', 'image_type': 'image/jpeg', 'image_size': 100} # sent image

                                            message_event['text'] = message_event['text'] + "Sent an attachment (not supported yet)\n"
                                message_event['text'] = message_event['text'] + message['msg']
                                self.event_emitter.emit('message',message_event)
                            channels_last_message_id[channel_id] = message['_id']
            except Exception as e:
                print(e)

        api_logout = requests.get("{}logout".format(
            self.base_api_url), headers=self.auth_headers)
        api_logout_response = api_logout.json()
        if api_logout_response['status'] != "success":
            raise Exception("RocketChat logout status: {} ({})".format(api_logout_response['status'],api_logout_response['message']))
        self.stop()

    def send_msg(self,channel_id,msg):
        self.rocketchat.chat_postMessage(channel_id,msg)
