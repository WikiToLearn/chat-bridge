#!/usr/bin/env python3
from ChatAdapters.ChatAdapter import ChatAdapter
import requests
import time

class RocketChat(ChatAdapter):

    def __init__(self, adapter_name, event_emitter, baseurl, username, password):
        ChatAdapter.__init__(self,adapter_name,event_emitter)
        self.baseurl = baseurl
        self.base_api_url = "{}api/".format(self.baseurl)
        self.username = username

        api_version = requests.get("{}version".format(self.base_api_url))
        api_version_response = api_version.json()
        supported_api_version = "0.1"
        supported_rocketchat_version = "0.5"
        if api_version_response['status'] != "success" or \
                api_version_response['versions']['api'] != supported_api_version or \
                api_version_response['versions']['rocketchat'] != supported_rocketchat_version:
            raise Exception("RocketChat wrong version (API {}!={} or RocketChat {}!={})".format(
                api_version_response['versions']['api'],
                supported_api_version,
                api_version_response['versions']['rocketchat'],
                supported_rocketchat_version
            ))

        login_data = {}
        login_data['username'] = username
        login_data['password'] = password
        api_login = requests.post("{}login".format(self.base_api_url),
                                  data=login_data)
        api_login_response = api_login.json()

        if api_login_response['status'] == "success":
            self.auth_headers = {}
            self.auth_headers['X-Auth-Token'] = api_login_response['data']['authToken']
            self.auth_headers['X-User-Id'] = api_login_response['data']['userId']
        else:
            raise Exception("RocketChat login status: {} ({})".format(api_login_response['status'],api_login_response['message']))

    def make_api_get(self,uri):
        url = "{}{}".format(self.base_api_url,uri)
        api_request = requests.get(url, headers=self.auth_headers)
        api_response = api_request.json()
        return api_response

    def make_api_post(self,uri,api_data):
        url = "{}{}".format(self.base_api_url,uri)
        api_request = requests.post(url, headers=self.auth_headers,data=api_data)
        api_response = api_request.json()
        return api_response

    def make_api_post_json(self,uri,api_json):
        url = "{}{}".format(self.base_api_url,uri)
        api_request = requests.post(url, headers=self.auth_headers,json=api_json)
        api_response = api_request.json()
        return api_response

    def public_rooms(self):
        api_publicRooms_response = self.make_api_get("publicRooms")
        return api_publicRooms_response['rooms']

    def joined_rooms(self):
        api_publicRooms_response = self.make_api_get("joinedRooms")
        return api_publicRooms_response['rooms']

    def rooms_join(self,room_id):
        api_rooms__id_join_response = self.make_api_post("rooms/{}/join".format(room_id),{})

    def rooms_leave(self,room_id):
        api_rooms__id_join_response = self.make_api_post("rooms/{}/leave".format(room_id),{})

    def rooms_messages(self,room_id,skip=0,limit=50):
        api_rooms__id_messages_response = self.make_api_get("rooms/{}/messages?skip={}&limit={}".format(room_id,skip,limit))
        return api_rooms__id_messages_response['messages']

    def rooms_send(self,room_id,msg):
        api_rooms__id_send_json = {}
        api_rooms__id_send_json['msg'] = msg
        api_rooms__id_send_response = self.make_api_post_json("rooms/{}/send".format(room_id),api_rooms__id_send_json)

    def run(self):
        channels_ids = []
        for room in self.joined_rooms():
            channels_ids.append(room['_id'])
        channels_last_message_id = {}
        for channel_id in channels_ids:
            messages = self.rooms_messages(channel_id,0,1)
            if len(messages) > 0:
                channels_last_message_id[channel_id] = messages[0]['_id']

        while self.running:
            try:
                time.sleep(1)
                for channel_id in channels_ids:
                    messages = self.rooms_messages(channel_id,0,1)
                    for message in messages:
                        if channels_last_message_id[channel_id] != message['_id']:
                            if message['u']['username'] != self.username:
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
        self.rooms_send(channel_id,msg)
