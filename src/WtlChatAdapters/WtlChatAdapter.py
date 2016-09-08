#!/usr/bin/env python3
from threading import Thread

class WtlChatAdapter(Thread):

    def __init__(self, adapter_name):
        Thread.__init__(self)
        self.adapter_name = adapter_name
