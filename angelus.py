#!/usr/bin/python3

# Adapted from tdjson_example.py, which is copyright Aliaksei Levin (levlam@telegram.org), 
# Arseny Smirnov (arseny30@gmail.com), Pellegrino Prevete (pellegrinoprevete@gmail.com)
# 2014-2021. Source: https://github.com/tdlib/td/blob/master/example/python/tdjson_example.py
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
# Author: John Khoo (john_khoo@u.nus.edu)

from ctypes.util import find_library
from ctypes import *
from random import randint
import json
import os
import sys
import datetime as dtime
import socket

# load secrets
decoder = json.JSONDecoder()
try:
    secrets_path, sock_path, tdjson_path = sys.argv[1:4]
except ValueError:
    sys.exit(f"Usage: {__file__} <path to secrets JSON> <path to input socket> <path to libtdjson.so>")
with open(secrets_path, 'r') as f:
    secret_str = f.read().replace('\n','')
    SECRETS = decoder.decode(secret_str)
BUFSIZE = 4096
RAND_UPPER, RAND_LOWER = 0, 2**32
TOL_SECS = 3 * 60

ANGELUS = """
The Angel of the Lord declared to Mary: And she conceived of the Holy Spirit. Hail Mary...

Behold the handmaid of the Lord: Be it done unto me according to Thy word. Hail Mary...

And the Word was made Flesh:
And dwelt among us. Hail Mary...

Pray for us, O Holy Mother of God, that we may be made worthy of the promises of Christ. 

Let us pray:

Pour forth, we beseech Thee, O Lord, Thy grace into our hearts; that we, to whom the incarnation of Christ, Thy Son, was made known by the message of an angel, may by His Passion and Cross be brought to the glory of His Resurrection, through the same Christ Our Lord. Amen.
"""

EXAMEN = """
As the day draws to a close, let us take a few minutes to examine our day in God's presence. Begin by acknowledging the presence of God, giving thanks for the day that has passed, and asking for His light as you review it. Then, step through the events of the day, from when you woke up, praising God with gratitude for the blessings you have received and humbly asking His forgiveness for the times you have failed Him. Here are some questions to help in our reflection!

- Do I love God? Do I prioritise and seek to glorify Him, to worship Him as He deserves, and to understand and follow His commandments?
- Am I constantly aware of the presence of God in everything I do, and His love for me? Do I draw peace and joy from the knowledge that I am His child, or do I allow worldly cares to overwhelm me? Do I trust in God's love?
- Did things go according to plan today, or even better than expected? Have I been grateful for these occasions?
- Did anyone go out of his way today to help me? Did I acknowledge him with gratitude?
- Did I have any unpleasant interactions with people today? Why were they unpleasant?
- Have I fulfilled my responsibilities to my family, friends, and work? Do I love my family and friends? Do they know that I love them?
- Have I wasted my time today, or caused other people to waste their time? Have I used my resources (talents, money, belongings, etc.) well?
- Do I bear the difficulties of each day with patience, in union with Christ? Am I overly attached to comfort, preference, and convenience?
- Have I entertained prideful, lustful, hateful, envious, etc. thoughts instead of resisting them?
- Have I been dishonest? Have I discussed the faults of others unnecessarily?
- Do I humbly acknowledge my faults and ask forgiveness from people? Do I forgive others? Do I seek to grow from my mistakes, and help others to grow too?
- Have I taken reasonable care of my health?
- Have I tried to bring the love of Christ to others today, and to lead them to Him?

No matter how well or badly your day has gone, God loves you with an eternal love. If we open our hearts to Him, He will give us the grace to do better. Even the gravest of sins can be forgiven, and our relationship with God restored, in Confession. Let's keep praying for each other!
"""

def unlink_sock(path):
    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise RuntimeError(f"Something else already exists at {path}!")

# load shared library
tdjson = CDLL(tdjson_path)

# load TDLib functions from shared library
def load_tdlib_func(attr, restype, argtypes):
    funcptr = getattr(tdjson, attr)
    funcptr.restype = restype
    funcptr.argtypes = argtypes
    return funcptr

_td_create_client_id = load_tdlib_func("td_create_client_id", c_int, [])
_td_receive = load_tdlib_func("td_receive", c_char_p, [c_double])
_td_send = load_tdlib_func("td_send", None, [c_int, c_char_p])
_td_execute = load_tdlib_func("td_execute", c_char_p, [c_char_p])
log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)
_td_set_log_message_callback = load_tdlib_func("td_set_log_message_callback", None,
    [c_int, log_message_callback_type])

# initialize TDLib log with desired parameters
def on_log_message_callback(verbosity_level, message):
    if verbosity_level == 0:
        sys.exit('TDLib fatal error: %r' % message)

def td_execute(query):
    query = json.dumps(query).encode('utf-8')
    result = _td_execute(query)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

c_on_log_message_callback = log_message_callback_type(on_log_message_callback)
_td_set_log_message_callback(2, c_on_log_message_callback)

# setting TDLib log verbosity level to 1 (errors)
td_execute({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1, '@extra': 1.01234})

# create client
client_id = _td_create_client_id()

# simple wrappers for client usage
def td_send(query):
    query = json.dumps(query).encode('utf-8')
    _td_send(client_id, query)

def td_receive():
    result = _td_receive(1.0)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

# start the client by sending request to it
td_send({'@type': 'getAuthorizationState'})

# compute unix timestamps to send messages tomorrow
sgtz = dtime.timezone(dtime.timedelta(hours=8)) # ensure timezone is correct
tmrw = dtime.datetime.now(sgtz) + dtime.timedelta(days=1)
def time_to_epoch(dt, h, m):
    ndt = dtime.datetime(dt.year, dt.month, dt.day,
            hour=h, minute=m)
    return ndt.timestamp()

morning_angelus = int(time_to_epoch(tmrw, 6, 0))
noon_angelus = int(time_to_epoch(tmrw, 12, 0))
evening_angelus = int(time_to_epoch(tmrw, 18, 0))
examen = int(time_to_epoch(tmrw, 22, 30))

def sched_msg(text, timestamp):
    extra = randint(RAND_UPPER, RAND_LOWER)
    td_send({'@type': 'sendMessage', 'chat_id': SECRETS['channel_id'], 
        'options': {'@type': 'messageSendOptions', 'scheduling_state': 
            {'@type': 'messageSchedulingStateSendAtDate', 'send_date': timestamp} }, 
        'input_message_content': {'@type': 'inputMessageText',
            'text': {'@type': 'formattedText', 'text': text}},
        '@extra': extra})
    

def msg_before(timestamp): 
    extra = randint(RAND_UPPER, RAND_LOWER)
    td_send({'@type': 'getChatMessageByDate', 'chat_id': SECRETS['channel_id'], 
        'date': timestamp, '@extra': extra})
    return extra

def get_sched():
    extra = randint(RAND_UPPER, RAND_LOWER)
    td_send({'@type': 'getChatScheduledMessages', 'chat_id': SECRETS['channel_id'], 
        '@extra': extra})
    return extra

def wait_extra(extra):
    while True:
        event = td_receive()
        if event and event.get('@extra', None) == extra:
            print(event)
            return event

auth_ready = False
# main events cycle
while True:
    event = td_receive()
    if event:
        # process authorization states
        if event['@type'] == 'updateAuthorizationState':
            auth_state = event['authorization_state']

            # if client is closed, we need to destroy it and create new client
            if auth_state['@type'] == 'authorizationStateClosed':
                td_send({'@type': 'getAuthorizationState'})

            # set TDLib parameters
            # you MUST obtain your own api_id and api_hash at https://my.telegram.org
            # and use them in the setTdlibParameters call
            if auth_state['@type'] == 'authorizationStateWaitTdlibParameters':
                td_send({'@type': 'setTdlibParameters', 'parameters': {
                                                       'database_directory': 'data',
                                                       'use_message_database': True,
                                                       'use_secret_chats': True,
                                                       'api_id': SECRETS['api_id'],
                                                       'api_hash': SECRETS['api_hash'],
                                                       'system_language_code': 'en',
                                                       'device_model': 'Olinuxino',
                                                       'application_version': '0.1',
                                                       'enable_storage_optimizer': True},
                                                       })

            # set an encryption key for database to let know TDLib how to open the database
            if auth_state['@type'] == 'authorizationStateWaitEncryptionKey':
                td_send({'@type': 'checkDatabaseEncryptionKey', 'encryption_key': ''})

            # enter phone number to log in
            if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
                td_send({'@type': 'setAuthenticationPhoneNumber', 'phone_number': SECRETS['phone_number']})

            # wait for authorization code
            if auth_state['@type'] == 'authorizationStateWaitCode':
                unlink_sock(sock_path)
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                sock.bind(sock_path)
                code = sock.recv(BUFSIZE).decode(encoding='utf-8')[:6]
                td_send({'@type': 'checkAuthenticationCode', 'code': code})

            if auth_state['@type'] == 'authorizationStateReady':
                auth_ready = True

            print(event)
            continue

        if not auth_ready:
            continue

        sched_msgs = wait_extra(get_sched()).get('messages', None)
        # if not sched_msgs:
        pending_scheds = {morning_angelus: ANGELUS, noon_angelus: ANGELUS, evening_angelus: ANGELUS,
                examen: EXAMEN}
        for msg in sched_msgs:
            try:
                sched_timestamp = msg.get('scheduling_state', None).get('send_date', None)
                sched_text = msg.get('content', None).get('text', None).get('text', None)
            except AttributeError:
                continue
            rmlist = []
            for time in pending_scheds.keys():
                if abs(sched_timestamp - time) < TOL_SECS:
                    rmlist.append(time)
            for rmtime in rmlist:
                pending_scheds.pop(rmtime)

        for time, msg in pending_scheds.items():
            sched_msg(msg, time)

        break

        # main events here
