#!/usr/bin/env python3
from threading import Thread
import time

class WtlChatAdapter(Thread):

    def __init__(self, adapter_name, event_emitter):
        Thread.__init__(self)
        self.running = True
        self.adapter_name = adapter_name
        self.event_emitter = event_emitter

    def stop(self):
        self.running = False
