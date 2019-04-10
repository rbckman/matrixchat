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
import subprocess
import logging
import configparser
import argparse
import getpass
from datetime import datetime
import code
import time
import requests
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
    global logs, botapi
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
        try:
            botapi = config['botapi']['botapi']
        except:
            botapi = ''
            logging.exception('')
            pass
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
    curses.noecho()
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
    screen.keypad(False)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


###-------| THE BASIC FUNCTIONS  |-------------###


def writetolog(newmessage, room_id):
    if room_id:
        with open(logs + room_id + '.log', 'a') as out:
            out.write(newmessage + '\n')


def on_message(room, event):
    newmessage = ''
    ts = int(event['origin_server_ts'])/1000
    msgtime = datetime.fromtimestamp(ts).strftime('%d/%m-%H:%M') + ' '
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            newmessage = msgtime + ("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        buddy = "{0}".format(event['sender'])
        buddy = buddy.split(':')[0] + ': '
        if event['content']['msgtype'] == "m.text":
            msg =  "{0}".format(event['content']['body'])
        elif event['content']['msgtype'] == "m.image": 
            msg =  "image: {0}".format(event['content']['body'] + '\n')
            msg += "{0}".format(event['content']['file'])
            #msg +=  "size:  {0}".format(event['content']['size'])
        elif event['content']['msgtype'] == "m.file": 
            msg =  "file: {0}".format(event['content']['body'] + '\n')
            msg +=  "{0}".format(event['content']['file'])
            #msg +=  "size:  {0}".format(event['content']['size'])
        elif event['content']['msgtype'] == "m.audio": 
            msg =  "audio: {0}".format(event['content']['body'] + '\n')
            msg +=  "{0}".format(event['content']['file'])
            #msg +=  "size:  {0}".format(event['content']['size'])
        newmessage = msgtime + buddy + msg
    else:
        newmessage = (event['type'])
    room.update_aliases()
    for i in room.aliases:
        room_alias = i
        break
    writetolog(newmessage, room_alias) 

def resetconnection(screen, client):
    screen.addstr(0,0, 'Oops! no connection, trying again in 5 sec...') 
    screen.refresh()
    client.start_listener_thread()
    client.stop_listener_thread()
    client.start_listener_thread()
    return

def connectionlost(e):
    logging.exception(e)

def connect(host, user_id, password):
    global client
    try:
        client = MatrixClient(host, encryption=True, restore_device_id=True)
        client.login(username=user_id, password=password)
        client.start_listener_thread(timeout_ms=30000, exception_handler=None)
        #client.bad_sync_timeout_limit = 0
        #client.start_listener_thread()
        #client.should_listen=30000
        client.add_key_forward_listener(lambda x: writetolog('got new keys' + x))
    except:
        logging.exception('')
        quit()
    return(client)

def joinroom(client, room_id):
    try:
        room = client.join_room(room_id)
        device_id = client.device_id
        fingerprint = client.get_fingerprint()
        assert client.device_id == device_id
        # Print every keys which arrive to us
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

def bot(log, lastupdate):
    msg = ''
    #put your bot scripts here
    #if you need to get information from an api put the key in /.matrixchat/config.ini file like this
    # [botapi]
    # botapi = key
    if time.time() - lastupdate > 18000:
        msg = "anet: Hello! I'm Anet printer, whats your name? run: [anet help] to see what u can do with me"
        msg += "bakerbot: Whatsup evybaady, I'm bakerbot, I keep track of how much energy goes into robs ryebreads, check me out with [bakerbot status]"
        lastupdate = time.time()
    if 'anet help' in log:
        msg = "anet: Hello I'm Anet printer! [anet status] for my status" 
    if 'anet status' in log: 
        progress = requests.get(url=botapi).json()
        try:
            msg = 'anet:'+str(progress['state'])+' model:'+(progress['job']['file']['name'])
            msg += ' time left: ' + str(int(progress['progress']['printTimeLeft']/60))
            msg += ' has been printing for: ' + str(int(progress['progress']['printTime']/60)) + ' min'
            msg += ' is ' + str(int(progress['progress']['completion'])) + '% complete'
        except:
            msg = "I'm currently offline, thanks for asking!"
            logging.exception('')
            pass
    if 'bakerbot status' in log:
        try:
            cmd = '/home/pi/smartpick/smartpick.py'
            cmd2 = '/home/pi/smartpick/smartpick.py'
            o = subprocess.check_output([cmd, 'http://smartpi.local']).decode().rstrip('\n')
            o2 = subprocess.check_output([cmd2, 'http://smartpi2.local']).decode().rstrip('\n')
            msg = 'bakerbot: Heres the stats for the owens and baking machines for today: ' + o
            msg += ' and heres the stats for the other electronics: ' + o2
        except:
            msg = "Baker bot is feeling bad today! check the logs.."
            logging.exception('')
            pass
    return(msg, lastupdate)


###-------| ROOM STUFF HAPPENING FROM HERE |-------###


def main(screen, client, user_id, rooms, room_id, room_ids, host):
    username = user_id.split(':')[0]
    roomusers = ''
    msg = ''
    fps = 0
    scroll = 0
    key = 0
    selectroom = len(room_ids) - 1
    maxyx = screen.getmaxyx()
    cursor = screen.getyx()
    timeupdate = time.time()
    oldbotmsg = ''
    while True:
        c = ''
        key = 0
        try:
            c = screen.get_wch()
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
                elif '/resync' in msg:
                    resetconnection(screen, client)
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
                elif msg != '':
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
            if selectroom > 0:
                selectroom -= 1
        if room_id:
            room_id = room_ids[selectroom]
            roomusers = rooms[selectroom].display_name
            #load messages from file in log directory
            if not os.path.isfile(logs + room_id + '.log'):
                with open(logs + room_id + '.log', 'a') as out:
                    out.write('Welcome to ' + room_id + '!\n')
            chatlog = [line.rstrip('\n') for line in open(logs + room_id + '.log')]
            if botapi:
                botmsg, timeupdate = bot(chatlog[-1], timeupdate)
                if botmsg:
                    rooms[selectroom].send_text(botmsg)
                    botmsg = ''
        else:
            chatlog = ['Join or create a room!']
            listrooms = client.get_rooms()
            for l in listrooms:
                for p in listrooms[l].aliases:
                    chatlog.append('/join ' + p + '\n')
        #if scrolling then put messages in where they should be
        usrmsg = username + ': ' + msg
        msgheight = int(len(usrmsg)/maxyx[1] + 3)
        if scroll > 0:
            chatlog = chatlog[-(maxyx[0] - msgheight) - scroll : - scroll]
        else:
            chatlog = chatlog[-(maxyx[0] - msgheight):]
        #reverse chatlog so latest message is at bottom
        chatlog = chatlog[::-1]
        y = maxyx[0] - msgheight
        fps += 1
        screen.clear()
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
        #show debuugging stuff
        #screen.addstr(0,0, str(fps) + ' maxyx:' + str(maxyx) + ' cursor:' + str(cursor) + ' key:' + str(c))
        screen.addstr(0,0, roomusers[:maxyx[1]-2])
        screen.addstr(maxyx[0]-1,0, room_id[:maxyx[1]-2], curses.color_pair(242))
        screen.addstr(maxyx[0]-int(len(usrmsg)/maxyx[1] + 2),0,usrmsg, curses.color_pair(71))
        screen.refresh()


###---------| FINALLY WE PUT EVERYTHING TOGETHER |---------###


if __name__ == '__main__':
    configfile = argparser()
    host, user, password, logs, debug = getconfig(configfile)
    logging.basicConfig(filename=debug, filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.WARNING)
    screen = startcurses()
    client = connect(host, user, password)
    rooms = []
    room_id = ''
    room_ids = []
    for a in os.listdir(logs):
        room_id = a[:-4]
        rooms.append(joinroom(client, room_id))
    for i in rooms:
        i.update_aliases()
        for p in i.aliases:
            room_ids.append(p)
            break
    while True:
        cmd, attr = main(screen, client, user, rooms, room_id, room_ids, host)
        if cmd == '/join':
            if attr not in room_ids:
                try:
                    rooms.append(joinroom(client, attr))
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
