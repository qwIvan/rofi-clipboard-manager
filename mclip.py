#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import struct
import subprocess
import pyperclip
from sys import argv


# Settings
CLIP_LIMIT = 50             # number of clipboard history
HISTORY_FILE = os.environ['HOME'] + '/.clipboard-history.bin'
CLIP_FILE = os.environ['HOME'] + '/.clipboard'
STRING_LIMIT = 100
HELP = '''./mclip.py menu|daemon'''
PASTE = '''keydown Control_L
key v
keyup Control_L
'''                         # your paste key
DAEMON_DELAY = 1


class ClipboardManager():
    def __init__(self):
        open(HISTORY_FILE, "a+").close()

    def daemon(self):
        clips = self.read()
        while True:
            clip = pyperclip.paste()
            if clip and (not clips or clip != clips[0]):
                if clip in clips:
                    clips.remove(clip)
                clips.insert(0, clip)
                self.write(clips[0:CLIP_LIMIT])
            time.sleep(DAEMON_DELAY)

    def menu(self):
        with open(CLIP_FILE, "w+") as file:
            file.write('')

        clips = self.read()
        for index, clip in enumerate(clips):
            clip = clip.replace('\n', ' ')
            print '{}: {}'.format(index, clip[0:STRING_LIMIT])

    def copy(self, select):
        clips = self.read()
        if select:
            index = int(select[0:select.index(':')])
            with open(CLIP_FILE, "w+") as file:
                file.write(clips[index])

    def paste(self):
        with open(CLIP_FILE, "r") as file:
            copy = file.read()

        if copy:
            pyperclip.copy(copy)
            p = subprocess.Popen(['xte'], stdin=subprocess.PIPE)
            p.communicate(input=PASTE)

    def read(self):
        result = []
        with open(HISTORY_FILE, "rb") as file:
            bytes_read = file.read(4)
            while bytes_read:
                chunksize = struct.unpack('>i', bytes_read)[0]
                bytes_read = file.read(chunksize)
                result.append(str(bytes_read))
                bytes_read = file.read(4)
        return result

    def write(self, items):
        with open(HISTORY_FILE, 'wb') as file:
            for item in items:
                file.write("{0}{1}".format(struct.pack('>i', len(item)), item))


if __name__ == "__main__":
    cm = ClipboardManager()

    if len(argv) <= 1:
        print(HELP)
    elif argv[1] == 'menu':
        if len(argv) > 2:
            cm.copy(argv[2])
        else:
            cm.menu()
    elif argv[1] == 'daemon':
        cm.daemon()
    elif argv[1] == 'paste':
        cm.paste()
    else:
        print(HELP)
    exit(0)