#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
###-----------|  MATRIX CHAT CLIENT  |------------###
python matrix chat using matrix-python-sdk and curses

hacked by rbckman
-----------------------------------------------------
"""

import curses
import sys
import os
import logging
import configparser
import argparse
import getpass
from hashlib import sha224
from datetime import datetime
import code
import time
from matrix_client.client import MatrixClient
from matrix_client.errors import E2EUnknownDevices
from os.path import expanduser


###----------|  CONFIG STUFF STARTS  |----------###


def argparser():
    parser = argparse.ArgumentParser(description='Matrix Chat using matri-python-sdk and curses', epilog='development at https://github.com/rbckman/matrixchat')
    parser.add_argument('-c', '--configfile', help='config file, defaults to ~/.matrixchat/config.ini')
    args = parser.parse_args()
    if args.configfile:
        return args.configfile
    else:
        return ''


def getconfig(configfile):
    global logs
    home = expanduser("~")
    if configfile == '':
        configfile = home +'/.matrixchat/config.ini'
    else:
        print('using config file: ' + configfile)
    configdir = os.path.dirname(configfile)
    debug = configdir + '/debug.log'
    if not os.path.isdir(configdir):
        os.makedirs(configdir)
    config = configparser.ConfigParser()
    if config.read(configfile):
        host = config.sections()[0]
        user = config[host]['user']
        logs = config[host]['logs']
        password = config[host]['password']
    else:
        host = input('Enter host name (https://mymatrixserver.net:8448): ')
        user = input('Enter whole username (@rob:mymatrixserver.net): ')
        logs = input("Where to keep logs? no input defaults to: '~/matrixchat/logs/': ")
        if logs == '':
            logs = home + '/.matrixchat/logs/'
        if not os.path.isdir(logs):
            os.makedirs(logs)
        password = getpass.getpass()
        save = input('Save to config file and autologin next time? (y)es or (n)o:')
        if save == 'y':
            config[host] = {}
            config[host]['user'] = user
            config[host]['password'] = password
            config[host]['logs'] = logs
            with open(configfile,'w') as f:
                config.write(f)
    return host, user, password, logs, debug


###-------|  CUZ EVERYONE LIKES CURSES  |------###


def startcurses():
    screen = curses.initscr()
    curses.cbreak()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    screen.clear()
    screen.keypad(True)
    screen.nodelay(True)
    screen.timeout(1000)
    return screen

def stopcurses(screen):
    curses.nocbreak()
    screen.keypad(False)
    curses.endwin()


###-------| THE BASIC FUNCTIONS  |-------------###


def writetolog(newmessage, room_id):
    with open(logs + room_id + '.log', 'a') as out:
        out.write(newmessage + '\n')


def on_message(room, event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            newmessage = ("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            ts = int(event['origin_server_ts'])/1000
            msgtime = datetime.fromtimestamp(ts).strftime('%d/%m-%H:%M')
            buddy = " {0}".format(event['sender'])
            buddy = buddy.split(':')[0]
            msg =  " {0}".format(event['content']['body'])
            newmessage = msgtime + buddy + ':' + msg
    else:
        newmessage = (event['type'])
    room.update_aliases()
    for i in room.aliases:
        room_id = i
        break
    writetolog(newmessage, room_id) 


def connect(host, user_id, password):
    global client
    try:
        client = MatrixClient(host, encryption=True, restore_device_id=True)
        client.login(username=user_id, password=password)
        device_id = client.device_id
        fingerprint = client.get_fingerprint()
        assert client.device_id == device_id
        client.start_listener_thread(timeout_ms=30000, exception_handler=None)
        client.should_listen = 30000
        # Print every keys which arrive to us
        client.add_key_forward_listener(lambda x: writetolog('got new keys' + x))
    except:
        logging.exception('')
        quit()
    return(client, device_id)


def joinroom(client, device_id, room_id):
    try:
        room = client.join_room(room_id)
    except:
        logging.exception('')
        try:
            room = client.create_room(alias=room_id, is_public=False, invitees=None)
        except:
            logging.exception('')
    try:
        room.send_text("MatrixRob is here!")
        pass
    except E2EUnknownDevices as e:
        #room.verify_devices = True
        # We don't know anyone, but send anyway
        for user_id, devices in e.user_devices.items():
            for device in devices:
                #device.verified = True
                device.ignored = True
                # Out-of-band verification should allow to do device.verified = True instead
    room.add_listener(on_message)
    return room



###-------| ROOM STUFF HAPPENING FROM HERE |-------###


def main(screen, client, user_id, rooms, room_id, room_ids):
    username = user_id.split(':')[0]
    msg = ''
    fps = 0
    scroll = 0
    key = 0
    selectroom = len(room_ids) - 1
    maxyx = screen.getmaxyx()
    cursor = screen.getyx()
    while True:
        c = ''
        key = 0
        try:
            c = screen.get_wch()
            screen.clear()
            if isinstance(c,int):
                key = c
            elif isinstance(c,str):
                if c == '\n':
                    key = 10
                    c = ''
                if c == '\x7f':
                    key = 263
                    c = ''
                msg += c
        except:
            pass
        if maxyx != screen.getmaxyx():
            maxyx = screen.getmaxyx()
        cursor = screen.getyx()
        if key == 10:
            newmessage = ''
            try:
                if msg == "/quit":
                    return msg, ''
                elif '/join' in msg:
                    return msg.split(' ')[0], msg.split(' ')[1]
                    msg = ''
                elif msg == "/listrooms":
                    listrooms = client.get_rooms()
                    for l in listrooms:
                        for p in listrooms[l].aliases:
                            newmessage += 'alias ' + p + '\n'
                        newmessage += listrooms[l].room_id + '\n'
                    msg = ''
                elif msg == "/avatars":
                    whoishere = rooms[selectroom].get_joined_members()
                    newmessage = 'we have '
                    for i in whoishere:
                        newmessage += i.get_friendly_name() + ', '
                    newmessage += 'in the room'
                    msg = ''
                elif msg == "/code":
                    return msg, ''
                    msg = ''
                elif msg == "/debug=0":
                    logging.basicConfig(level=logging.CRITICAL)
                    msg = ''
                elif msg == "/debug=1":
                    logging.basicConfig(level=logging.DEBUG)
                    msg = ''
                else:
                    rooms[selectroom].send_text(msg)
                    msg = ''
            except:
                logging.exception('')
                newmessage = ('Oops! something wrong!\n')
            if newmessage != '' and room_id:
                writetolog(newmessage, room_id)
        elif key == 263:
            msg = msg[:-1]
        elif key == 339 or key == 259:
            scroll += 1
        elif key == 338 or key == 258:
            if scroll > 0:
                scroll = scroll - 1
        elif key == 261:
            if selectroom < len(room_ids) - 1:
                selectroom += 1
        elif key == 260:
            if selectroom > 1:
                selectroom -= 1
        if room_id:
            room_id = room_ids[selectroom]
        fps += 1
        msgheight = int(len(msg)/maxyx[1] + 3)
        screen.addstr(0,0, str(fps) + ' maxyx:' + str(maxyx) + ' cursor:' + str(cursor) + ' key:' + str(c))
        if room_id:
            if not os.path.isfile(logs + room_id + '.log'):
                with open(logs + room_id + '.log', 'a') as out:
                    out.write('Welcome to ' + room_id + '!\n')
            chatlog = [line.rstrip('\n') for line in open(logs + room_id + '.log')]
        else:
            chatlog = ['Join or create a room!']
            listrooms = client.get_rooms()
            for l in listrooms:
                for p in listrooms[l].aliases:
                    chatlog.append('/join ' + p + '\n')
        if scroll > 0:
            chatlog = chatlog[-(maxyx[0] - msgheight) - scroll : - scroll]
        else:
            chatlog = chatlog[-(maxyx[0] - msgheight):]
        chatlog = chatlog[::-1]
        y = maxyx[0] - msgheight
        for a in chatlog:
            #just fancy colors
            i = (len(a) % 10) + 245
            #count line height, print it
            y -= int(len(a)/maxyx[1]) + 1
            try:
                screen.addstr(y,0,a,curses.color_pair(i))
            except:
                logging.exception('')
                pass
            if y < 2:
                break
        screen.addstr(maxyx[0]-1,0, room_id[:maxyx[1]-2], curses.color_pair(242))
        nicemsg = username + ': ' + msg
        screen.addstr(maxyx[0]-int(len(nicemsg)/maxyx[1] + 2),0,nicemsg, curses.color_pair(71))
        screen.refresh()


###---------| FINALLY WE PUT EVERYTHING TOGETHER |---------###


if __name__ == '__main__':
    configfile = argparser()
    host, user, password, logs, debug = getconfig(configfile)
    logging.basicConfig(filename=debug, filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    screen = startcurses()
    client, device_id = connect(host, user, password)
    rooms = []
    room_id = ''
    room_ids = []
    for a in os.listdir(logs):
        room_id = a[:-4]
        room_ids.append(room_id)
        try:
            rooms.append(joinroom(client, device_id, room_id))
        except:
            logging.exception('')
    while True:
        cmd, attr = main(screen, client, user, rooms, room_id, room_ids)
        if cmd == '/join':
            if attr not in room_ids:
                try:
                    rooms.append(joinroom(client, device_id, attr))
                    rooms[-1].update_aliases()
                    for i in rooms[-1].aliases:
                        room_id = i
                    room_ids.append(room_id)
                except:
                    logging.exception('')
                    writetolog('something went wrong', room_id)
        elif cmd == '/code':
            stopcurses(screen)
            code.interact(local=locals())
            screen = startcurses()
        elif cmd == '/quit':
            break
    stopcurses(screen)
