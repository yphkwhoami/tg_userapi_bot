from telethon import TelegramClient, events, sync, functions, types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, InputPeerEmpty
import datetime
import sys
import json 
import time
import pymysql
import tg_config

api_id = tg_config.setting['app_id'] # use app id of telegram account
api_hash = tg_config.setting['app_hash']
# use app hash of your telegram account
# please change your prefix of session name , and don,t send to anyone
listener_session=tg_config.setting['session']['listener']

def tg():
    
    try:
        client = TelegramClient(listener_session, api_id, api_hash)
        client.start()
    except Exception as e:
        print(str(e))
        client.disconnect()   
    else:
        me = client.get_me()
        print(me)
        client.disconnect()   
        
def chunks(clist, n):
    n = max(1, n)
    return (clist[i:i+n] for i in range(0, len(clist), n))
    
tg()