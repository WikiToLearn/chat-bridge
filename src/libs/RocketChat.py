#!/usr/bin/env python3
import requests
from datetime import datetime
import time

class RocketChat():

    def __init__(self, baseurl, username, password):
        self.baseurl = baseurl
        self.base_api_url = "{}api/v1/".format(self.baseurl)
        self.username = username

        #info_request = requests.get("{}info".format(self.base_api_url))
        #self.info = info_request.json()

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
        if 'success' in api_response and not api_response['success']:
            raise Exception(api_response['error'])
        return api_response

    def make_api_post(self,uri,api_data):
        url = "{}{}".format(self.base_api_url,uri)
        api_request = requests.post(url, headers=self.auth_headers,data=api_data)
        api_response = api_request.json()
        if 'success' in api_response and not api_response['success']:
            raise Exception(api_response['error'])
        return api_response

    def make_api_post_json(self,uri,api_json):
        url = "{}{}".format(self.base_api_url,uri)
        api_request = requests.post(url, headers=self.auth_headers,json=api_json)
        api_response = api_request.json()
        if 'success' in api_response and not api_response['success']:
            raise Exception(api_response['error'])
        return api_response

    def logout(self):
        api_response=self.make_api_get("logout")
        return api_response

    def me(self):
        api_response=self.make_api_get("me")
        return api_response

    def channels_list(self):
        api_response = self.make_api_get("channels.list")
        return api_response['channels']

    def channels_list_joined(self):
        api_response = self.make_api_get("channels.list.joined")
        return api_response['channels']

    def channels_history(self,roomId,oldest=None,count=None):
        query_args = ""
        if oldest != None:
            query_args = query_args + "&oldest={}".format(oldest)
        if count != None:
            query_args = query_args + "&count={}".format(count)
        api_response = self.make_api_get("channels.history?roomId={}{}".format(roomId,query_args))
        return api_response['messages']

    def channels_info(self,roomId):
        api_response = self.make_api_get("channels.info?roomId={}".format(roomId))
        return api_response['channel']

    def chat_postMessage(self,roomId,text):
        info = self.channels_info(roomId)
        msg = {}
        msg['text'] = text
        msg['channel'] = "#" + info['name']
        r = self.make_api_post_json("chat.postMessage",msg)
        return r
