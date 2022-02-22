#!/usr/bin/python3

# Adapted from tdjson_example.py, which is copyright Aliaksei Levin (levlam@telegram.org),
# Arseny Smirnov (arseny30@gmail.com), Pellegrino Prevete (pellegrinoprevete@gmail.com)
# 2014-2021. Source: https://github.com/tdlib/td/blob/master/example/python/tdjson_example.py
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
# Author: John Khoo (john_khoo@u.nus.edu)

from ctypes import CDLL, CFUNCTYPE, c_int, c_char_p, c_double
from random import randint
import json
import os
import sys
import socket
import datetime as dtime
import dateparser as dp

BUFSIZE = 4096
RAND_UPPER, RAND_LOWER = 0, 2**32
TOL_SECS = 3 * 60
DP_SETTINGS = {"DATE_ORDER": "DMY", "TIMEZONE": "Singapore"}


def unlink_sock(path):
    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise RuntimeError(f"Something else already exists at {path}!")


def time_to_epoch(dt, h, m):
    ndt = dtime.datetime(dt.year, dt.month, dt.day, hour=h, minute=m)
    return ndt.timestamp()


class Autotele(object):
    def __init__(self, argv):
        # load secrets
        decoder = json.JSONDecoder()
        try:
            secrets_path, self.sock_path, tdjson_path, self.data_path = argv[1:5]
        except ValueError:
            sys.exit(
                f"Usage: {__file__} <path to secrets JSON> <path to input socket> <path to libtdjson.so> <path to database folder>"
            )
        with open(secrets_path, "r") as f:
            secret_str = f.read().replace("\n", "")
            self.secrets = decoder.decode(secret_str)

        self.custom_date = None
        try:
            self.custom_date = dp.parse(argv[5], settings=DP_SETTINGS)
        except IndexError:
            pass

        # load shared library
        self.tdjson = CDLL(tdjson_path)

        # load TDLib functions from shared library
        def load_tdlib_func(attr, restype, argtypes):
            funcptr = getattr(self.tdjson, attr)
            funcptr.restype = restype
            funcptr.argtypes = argtypes
            return funcptr

        _td_create_client_id = load_tdlib_func("td_create_client_id", c_int, [])
        _td_receive = load_tdlib_func("td_receive", c_char_p, [c_double])
        _td_send = load_tdlib_func("td_send", None, [c_int, c_char_p])
        _td_execute = load_tdlib_func("td_execute", c_char_p, [c_char_p])
        _td_log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)
        _td_set_log_message_callback = load_tdlib_func(
            "td_set_log_message_callback", None, [c_int, _td_log_message_callback_type]
        )

        # initialize TDLib log with desired parameters
        def on_log_message_callback(verbosity_level, message):
            if verbosity_level == 0:
                sys.exit("TDLib fatal error: %r" % message)

        def td_execute(query):
            query = json.dumps(query).encode("utf-8")
            result = _td_execute(query)
            if result:
                result = json.loads(result.decode("utf-8"))
            return result

            c_on_log_message_callback = _td_log_message_callback_type(
                on_log_message_callback
            )
            _td_set_log_message_callback(2, c_on_log_message_callback)

            # setting TDLib log verbosity level to 1 (errors)
            td_execute(
                {
                    "@type": "setLogVerbosityLevel",
                    "new_verbosity_level": 1,
                    "@extra": 1.01234,
                }
            )

            # create client
            client_id = _td_create_client_id()

            # simple wrappers for client usage
            def td_send(query):
                query = json.dumps(query).encode("utf-8")
                _td_send(client_id, query)

            def td_receive():
                result = _td_receive(1.0)
                if result:
                    result = json.loads(result.decode("utf-8"))
                return result

            self.td_send = td_send
            self.td_receive = td_receive
            self.td_execute = td_execute

    def sched_msg(self, text, timestamp, chat_id):
        extra = randint(RAND_UPPER, RAND_LOWER)
        self.td_send(
            {
                "@type": "sendMessage",
                "chat_id": chat_id,
                "options": {
                    "@type": "messageSendOptions",
                    "scheduling_state": {
                        "@type": "messageSchedulingStateSendAtDate",
                        "send_date": timestamp,
                    },
                },
                "input_message_content": {
                    "@type": "inputMessageText",
                    "text": {"@type": "formattedText", "text": text},
                },
                "@extra": extra,
            }
        )

        self.td_send({"@type": "loadChats", "limit": 10, "chat_list": None})
        return extra

    def msg_before(self, timestamp, chat_id):
        extra = randint(RAND_UPPER, RAND_LOWER)
        self.td_send(
            {
                "@type": "getChatMessageByDate",
                "chat_id": chat_id,
                "date": timestamp,
                "@extra": extra,
            }
        )
        return extra

    def get_sched(self, chat_id):
        extra = randint(RAND_UPPER, RAND_LOWER)
        self.td_send(
            {"@type": "getChatScheduledMessages", "chat_id": chat_id, "@extra": extra}
        )
        return extra

    def load_chats(self, limit=10, chat_list=None):
        extra = randint(RAND_UPPER, RAND_LOWER)
        self.td_send(
            {
                "@type": "loadChats",
                "limit": limit,
                "chat_list": chat_list,
                "@extra": extra,
            }
        )
        return extra

    def wait_extra(self, extra, show=True):
        while True:
            event = self.td_receive()
            if event and event.get("@extra", None) == extra:
                if show:
                    print(event)
                return event

    def authenticate(self):
        self.td_send({"@type": "getAuthorizationState"})
        while True:
            event = self.td_receive()
            if event:
                # process authorization states
                if event["@type"] == "updateAuthorizationState":
                    auth_state = event["authorization_state"]

                    # if client is closed, we need to destroy it and create new client
                    if auth_state["@type"] == "authorizationStateClosed":
                        self.td_send({"@type": "getAuthorizationState"})

                    # set TDLib parameters
                    # you MUST obtain your own api_id and api_hash at https://my.telegram.org
                    # and use them in the setTdlibParameters call
                    if auth_state["@type"] == "authorizationStateWaitTdlibParameters":
                        self.td_send(
                            {
                                "@type": "setTdlibParameters",
                                "parameters": {
                                    "database_directory": self.data_path,
                                    "use_message_database": True,
                                    "use_secret_chats": True,
                                    "api_id": self.secrets["api_id"],
                                    "api_hash": self.secrets["api_hash"],
                                    "system_language_code": "en",
                                    "device_model": "Olinuxino",
                                    "application_version": "0.1",
                                    "enable_storage_optimizer": True,
                                },
                            }
                        )

                    # set an encryption key for database to let know TDLib how to open the database
                    if auth_state["@type"] == "authorizationStateWaitEncryptionKey":
                        self.td_send(
                            {
                                "@type": "checkDatabaseEncryptionKey",
                                "encryption_key": "",
                            }
                        )

                    # enter phone number to log in
                    if auth_state["@type"] == "authorizationStateWaitPhoneNumber":
                        self.td_send(
                            {
                                "@type": "setAuthenticationPhoneNumber",
                                "phone_number": self.secrets["phone_number"],
                            }
                        )

                    # wait for authorization code
                    if auth_state["@type"] == "authorizationStateWaitCode":
                        unlink_sock(self.sock_path)
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                        sock.bind(self.sock_path)
                        code = sock.recv(BUFSIZE).decode(encoding="utf-8")[:6]
                        self.td_send({"@type": "checkAuthenticationCode", "code": code})

                    if auth_state["@type"] == "authorizationStateReady":
                        break

                if event.get("@type", None) in {"updateAuthorizationState", "error"}:
                    print(event)

    def schedule(self, pending_scheds, chat_id):
        sched_msgs = self.wait_extra(self.get_sched(chat_id)).get("messages", None)
        while not sched_msgs:
            self.wait_extra(self.load_chats())
            sched_msgs = self.wait_extra(self.get_sched(chat_id)).get("messages", None)

        for msg in sched_msgs:
            try:
                sched_timestamp = msg.get("scheduling_state", None).get(
                    "send_date", None
                )
                sched_text = (
                    msg.get("content", None).get("text", None).get("text", None)
                )
            except AttributeError:
                continue
            rmlist = []
            for time in pending_scheds.keys():
                if abs(sched_timestamp - time) < TOL_SECS:
                    rmlist.append(time)
            for rmtime in rmlist:
                pending_scheds.pop(rmtime)

        for time, msg in pending_scheds.items():
            self.wait_extra(self.sched_msg(msg, time, chat_id))
