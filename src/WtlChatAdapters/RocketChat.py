#!/usr/bin/env python3
from WtlChatAdapters.WtlChatAdapter import WtlChatAdapter
import requests


class RocketChat(WtlChatAdapter):

    def __init__(self, adapter_name, baseurl, username, password):
        WtlChatAdapter.__init__(self,adapter_name)
        self.baseurl = baseurl
        self.base_api_url = "{}api/".format(self.baseurl)

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

    def rooms_join(self,room_id):
        api_rooms__id_join_response = self.make_api_post("rooms/{}/join".format(room_id),{})
        print(api_rooms__id_join_response)

    def rooms_leave(self,room_id):
        api_rooms__id_join_response = self.make_api_post("rooms/{}/leave".format(room_id),{})
        print(api_rooms__id_join_response)

    def rooms_messages(self,room_id):
        api_rooms__id_messages_response = self.make_api_get("rooms/{}/messages".format(room_id))
        return api_rooms__id_messages_response['messages']

    def rooms_send(self,room_id,msg):
        api_rooms__id_send_json = {}
        api_rooms__id_send_json['msg'] = msg
        api_rooms__id_send_response = self.make_api_post_json("rooms/{}/send".format(room_id),api_rooms__id_send_json)
        print(api_rooms__id_send_response)

    def run(self):
        api_logout = requests.get("{}logout".format(
            self.base_api_url), headers=self.auth_headers)
        api_logout_response = api_logout.json()
        if api_logout_response['status'] != "success":
            raise Exception("RocketChat logout status: {} ({})".format(api_logout_response['status'],api_logout_response['message']))
