import os
import sys
import time
from telethon import TelegramClient, sync, events, functions, types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, InputPeerEmpty
from datetime import datetime, timedelta
import pymysql
#import logging
import asyncio
import aiomysql
#logging.basicConfig(level=logging.WARNING)
import tg_config
from pathlib import Path


api_id = tg_config.setting['app_id'] # use app id of telegram account
api_hash = tg_config.setting['app_hash']
# use app hash of your telegram account
# please change your prefix of session name , and don,t send to anyone
session_name=tg_config.setting['session']['listener']
db_username=tg_config.setting['database']['username']
db_pwd=tg_config.setting['database']['pwd']
db_name=tg_config.setting['database']['db']
user_bot_id=tg_config.setting['user_bot_id']
server_admin_id=tg_config.setting['server_admin_id']

debug_mode=True
max_delete_message = 1000
future_year = 2028
accepted_chat_ids=[user_bot_id]
config=[]     

@events.register(events.NewMessage(incoming=False))
async def outgoing_hander(event):
    if event.chat_id == user_bot_id:
        listener_client = event.client 
        #handle user bot command, user bot send to saved message 
        #print('---out going--- ' + str(event.chat_id))
        if event.text[0:1] == '_':
            if is_locked(user_bot_id):
                if debug_mode == True:
                    print(str(user_bot_id) + ' LOCKED!')
                await event.reply('Another process is running, please try again later.')
            else:
                Path(tg_config.setting['session_path'] + str(user_bot_id)).touch()
                if event.text == '_users':
                    #list all chat ids
                    users_chat=[]
                    try:
                        dialog_result = await listener_client(functions.messages.GetDialogsRequest(
                            offset_date=datetime(future_year, 12, 25),
                            offset_id=0,
                            offset_peer=InputPeerEmpty(),
                            limit=200,
                            hash = 0
                        ))
                    except Exception as e:
                        if debug_mode == True:
                            print(str(e))
                    users_chat.extend(dialog_result.users) 
                    for this_chat_user in users_chat:
                        try:
                            if this_chat_user.deleted == True or this_chat_user.bot == True:
                                continue
                            v_first_name=''
                            v_last_name=''
                            v_username=''
                            if  this_chat_user.first_name is not None:
                                v_first_name = this_chat_user.first_name

                            if  this_chat_user.last_name is not None:
                                v_last_name = this_chat_user.last_name

                            if  this_chat_user.username is not None:
                                v_username = '@' + this_chat_user.username 
                           
                            await event.reply(str(this_chat_user.id) + ' ' + v_username + ' ' + v_first_name + ' ' + v_last_name)
                            #print('---out going--- ' + str(this_chat_user.id) )
                            await asyncio.sleep(1)
                        except Exception as e:
                            if debug_mode == True:
                                print(str(e))
                            continue
                            
                elif event.text == '_groups':
                    #list all chat ids
                    chats = []
                    try:
                        dialog_result = await listener_client(functions.messages.GetDialogsRequest(
                            offset_date=datetime(future_year, 12, 25),
                            offset_id=0,
                            offset_peer=InputPeerEmpty(),
                            limit=200,
                            hash = 0
                        ))
                    except Exception as e:
                        if debug_mode == True:
                            print(str(e))
                    chats.extend(dialog_result.chats)
                    for chat in chats:
                        try:
                            #if chat.__class__.__name__ == 'Channel':        
                         #   if chat.megagroup == True: 
                            if chat.__class__.__name__ == 'ChatForbidden' or chat.__class__.__name__ == 'ChannelForbidden':
                                continue 
                            
                            try:
                                tmp_data = chat.left 
                            except Exception as e:  
                                pass
                            else:
                                if chat.left == True:
                                    continue
                                    
                            try:
                                tmp_data = chat.migrated_to
                            except Exception as e:       
                                pass
                            else:
                                continue
                                    
                            await event.reply(str(chat.id) + ' ' + chat.title + ' '+ chat.__class__.__name__)
                            await asyncio.sleep(1)
                        except Exception as e:
                            if debug_mode == True:
                                print(str(e))
                            continue

                elif event.text == '_clear':
                    #clear all messages with yourself (saved messages)
                    myself= await listener_client.get_input_entity(user_bot_id)
                    try:
                        await listener_client(functions.messages.DeleteHistoryRequest(
                            peer=myself,
                            max_id=0,
                            just_clear=True,
                            revoke=True
                        ))
                    except Exception as e:
                        if debug_mode == True:
                            print(str(e))

                else:
                    text_arg=event.text.split() 
                    if len(text_arg) > 1 and text_arg[0] == '_delete':
                        try:
                            userid=int(text_arg[1])
                        except Exception as e:
                            if debug_mode == True:
                                print(str(e))
                            await event.reply('Error : please provide user id')
                        else:

                            start = True
                            total = 0
                            while start == True or total > 0:
                                start = False
                                try:
                                    deleted = await listener_client(functions.messages.DeleteHistoryRequest(
                                        peer=userid,
                                        max_id=0,
                                        just_clear=True,
                                        revoke=True
                                    ))
                                except Exception as e:
                                    print(str(e))
                                    await event.reply('Error : ' + str(e))
                                    break

                                else:
                                    toomany = ''
                                    total = deleted.offset
                                    if deleted.offset > 0:
                                        toomany =  str(deleted.offset) + ' messages left. Next 100 messages will be deleted, please wait a moment. '
                                        
                                    await event.reply( str(deleted.pts_count) + ' messages with '+ str(userid) +' are deleted' + toomany)
                                    await asyncio.sleep(1)
                        

                    elif len(text_arg) > 1 and text_arg[0] == '_clear':
                        try:
                            userid=int(text_arg[1])
                        except Exception as e:
                            if debug_mode == True:
                                print(str(e))
                            await event.reply('Error : please provide user id')
                        else:
                            try:
                                deleted = await listener_client(functions.messages.DeleteHistoryRequest(
                                    peer=userid,
                                    max_id=0,
                                    just_clear=True,
                                    revoke=True
                                ))
                            except Exception as e:
                                print(str(e))
                                await event.reply('Error : ' + str(e))

                            else:
                                toomany = ''
                                if deleted.offset > 0:
                                    toomany = '\n' + str(deleted.offset) + ' messages left. If you want to delete all message, consider run _delete <userid>'
                                await event.reply(str(deleted.pts_count) + ' messages with '+ str(userid) +' are deleted' + toomany)


                    elif len(text_arg) > 2 and text_arg[0] == '_whitelist':
                        try:
                            userid=int(text_arg[1])
                            groupid=int(text_arg[2])
                        except Exception as e:
                            if debug_mode == True:
                                print(str(e))
                            await event.reply('Error : please provide user id and group id')
                        else:
                            can_whitelist = await set_whitelist(userid,groupid)
                            whitelist_reply = ''
                            if can_whitelist == 'db_error':
                                whitelist_reply='Error : database error'
                            elif can_whitelist == 'exist':
                                whitelist_reply='Error : already whitelisted'
                            elif can_whitelist == 'ok':
                                whitelist_reply = 'Added to whitelist, please reload the service.'
                            else:
                                whitelist_reply='Error : try again later'
                            await event.reply(whitelist_reply)

                await os.remove(tg_config.setting['session_path'] + str(user_bot_id))

#filter out all chats except whitelisted
@events.register(events.NewMessage(incoming=True,chats=accepted_chat_ids))
async def handler(event):
    #print('---incoming--- ' + str(event.chat_id) )
    #listen for whitelisted user id (single user chat)
    #to check if this is received from this user in single chat 
    manage_group_id=0
    for conf in config:
        #get group id from matched whitelist table
        #allow one user for one group only
        if event.chat_id == conf[0]:
            manage_group_id = conf[1]
            break
            
    listener_client = event.client 
    if event.is_reply and manage_group_id > 0:
        locked=False
        if is_locked(event.from_id):
            if debug_mode == True:
                print(str(event.from_id) + 'LOCKED!')
            await event.reply('Another process is running, please try again later.')
            locked=True
    #handling reply , for banning user when using cdrom report
        omessage = await event.get_reply_message()
        message_info = await this_user_info(omessage.id,False) #check if it is single message
        #get the user info to be banned from the reply message
        if locked == False:
            Path(tg_config.setting['session_path'] + str(event.from_id)).touch()
            if message_info:
                #ignore if he reply to his own sent message ..
                if event.chat_id != omessage.from_id:
                    #print('this is reply from '+ str(omessage.id))
                    #print('--------------')
                    #ban user here , need grant me permission!
                    #listener_client = TelegramClient(tg_config.setting['session']['runtime'] + '_' + str(manage_group_id), api_id, api_hash)
                    try:
                        #await listener_client.start()
                        this_channel = await listener_client.get_input_entity(PeerChannel(message_info[2]))
                        this_user = await listener_client.get_input_entity(PeerUser(message_info[0]))
                        result = await listener_client(functions.channels.EditBannedRequest(
                            channel=this_channel,
                            user_id=this_user,
                            banned_rights=types.ChatBannedRights(
                                until_date=datetime(future_year, 6, 25),
                                view_messages=True,
                                send_messages=True,
                                send_media=True,
                                send_stickers=True,
                                send_gifs=True,
                                send_games=True,
                            )
                        ))
                    except Exception as e:
                        if debug_mode == True:
                            await event.reply('Error : ' + str(e))
                            print(str(e))
                        else:
                            await event.reply('Error : please make sure user bot have permission to do so')
                        #await listener_client.disconnect()
                    else:
                        await omessage.edit('[Banned] ' + omessage.text)
                        await listener_client(functions.messages.DeleteMessagesRequest(
                            id=[event.id],
                            revoke=True
                        ))
                            #await listener_client.disconnect()
            else:
                #no single message detected, try check if it is batch message
                message_infos = await this_user_info(omessage.id,True)
                if len(message_infos) > 0:
                    #listener_client = TelegramClient(tg_config.setting['session']['runtime'] + '_' + str(manage_group_id), api_id, api_hash)
                    if event.text.lower() == 'all':
                        #ban all users of this replied message
                        baned_num =0
                        ban_ids =[]
                        #await listener_client.start()
                        for mi in message_infos:
                            #ban_ids.append(mi[0])
                            #perform ban action 
                            try:
                                #await listener_client.start()
                                this_channel = await listener_client.get_input_entity(PeerChannel(manage_group_id))
                                this_user = await listener_client.get_input_entity(PeerUser(mi[0]))
                                result = await listener_client(functions.channels.EditBannedRequest(
                                    channel=this_channel,
                                    user_id=this_user,
                                    banned_rights=types.ChatBannedRights(
                                        until_date=datetime(future_year, 6, 25),
                                        view_messages=True,
                                        send_messages=True,
                                        send_media=True,
                                        send_stickers=True,
                                        send_gifs=True,
                                        send_games=True,
                                    )
                                ))
                            except Exception as e:
                                if debug_mode == True:
                                    await event.reply('Error : ' + str(e))
                                    print(str(e))
                                else:
                                    await event.reply('Error : please make sure user bot have permission to do so')
                            else:
                                baned_num+=1
                              
                        #await listener_client.disconnect()    
                        await event.reply('Banned '+str(baned_num)+ ' users')
                        #await event.reply('Banned '+str(', '.join(ban_ids)))
                    else:
                        try:
                            valid_ids =[]
                            ban_ids =[]
                            is_failed=False
                            for mi in message_infos:
                                valid_ids.append(str(mi[0]))
                            text_arg=event.text.split(',') 
                            if len(text_arg) == 0:
                                is_failed=True
                                await event.reply('Please reply with "all" to ban all users displaying in the message\nor ban specified users: \n\n"<first user id>,<second user id>,<any number of user id>" (without bracket) ')
                            #strictly check if id are int 
                            for arg_t in text_arg:
                                try:
                                    arg_id = int(arg_t.strip())
                                except Exception as e:
                                    #print(str(e))
                                    is_failed=True
                                else:
                                    try:
                                        index = valid_ids.index(str(arg_id))
                                    except Exception as e:
                                        #id is not found inside the message
                                        #print('index error') 
                                        is_failed=True
                                    else:
                                        ban_ids.append(str(arg_id))
                            if len(ban_ids) >0 and is_failed == False:
                                #perform ban action 
                                baned_num=0
                                #await listener_client.start()
                                for ban_user in ban_ids:
                                    try:
                                        this_channel = await listener_client.get_input_entity(PeerChannel(manage_group_id))
                                        this_user = await listener_client.get_input_entity(PeerUser(ban_user))
                                        result = await listener_client(functions.channels.EditBannedRequest(
                                            channel=this_channel,
                                            user_id=this_user,
                                            banned_rights=types.ChatBannedRights(
                                                until_date=datetime(future_year, 6, 25),
                                                view_messages=True,
                                                send_messages=True,
                                                send_media=True,
                                                send_stickers=True,
                                                send_gifs=True,
                                                send_games=True,
                                            )
                                        ))
                                    except Exception as e:
                                        if debug_mode == True:
                                            await event.reply('Error : ' + str(e))
                                            print(str(e))
                                        else:
                                            await event.reply('Error : please make sure user bot have permission to do so')
                                    else:
                                        baned_num+=1
                                    await event.reply('Banned '+str(baned_num) + ' users')
                                #await listener_client.disconnect()    
                                #await event.reply('Banned '+str(len(ban_ids))+' users')
                            else:
                                await event.reply('No valid user to ban.\n\nPlease reply with "all" to ban all users displaying in the  message\nor ban specified users:\n\n"<first user id>,<second user id>,<any number of user id>" (without bracket) ')
                        except Exception as e:
                            print(str(e))
                                    
                else:
                    print('Error : no handler for this batch message')
                    await event.reply('Error : this message is expired')
            await os.remove(tg_config.setting['session_path'] + str(event.from_id))
            

    else:
        if is_locked(event.from_id):
            if debug_mode == True:
                print(str(event.from_id) + 'LOCKED!')
            await event.reply('Another process is running, please try again later.')
        else:
            Path(tg_config.setting['session_path'] + str(event.from_id)).touch()
            #admin command , handle admin user's group command 
            if event.text[0:1] == '_':
                text_arg=event.text.split() 
                if text_arg[0] == '_help':
                    #help menu
                    help_menu='---- Please read what you can do ----\n\n'
                    help_menu+='[_help] list help menu\n\n'
                    help_menu+='[_howtounban] how to unban user\n\n'
                    help_menu+='[_howtoban] how to ban user from cdrom report\n\n'
                    help_menu+='[_clear] clear all messages with <userbot>\n\n'
                    help_menu+='[_delmsg n] delete all messages of group before n days ago\n'
                    help_menu+='HINTS: it may consume much time if there are too many messages. '
                    help_menu+='Maximum '+str(max_delete_message)+' messages for one batch delete action, you can run the command several times to delete ALL messages.\n'
                    help_menu+='WARNING: 0 will delete messages of group before NOW\n\n'
                    #help_menu+='[_cdrom on n] enable the scheduler to run listing cdrom report every day at 23:00 for those who sent less than n messages\n\n'
                    #help_menu+='[_cdrom off] disable the scheduler to run listing cdrom report every day at 23:00\n\n'
                    help_menu+='[_cdrom] request of listing cdrom report, system admin will run it for you soon\n\n'
                    help_menu+='*  to ban user, reply to message in cdrom report\n'
                    await event.reply(help_menu)
                elif text_arg[0] == '_cdrom':
                    #cdrom report request
                    await event.reply('We will help run the report for you soon, please stop sending command for a moment.\nOr please ask server admin for help directly.')
                    #bot_listener_client = TelegramClient(tg_config.setting['session']['bot'], api_id, api_hash)
                    #await bot_listener_client.start()
                    try:
                        me_entity = await listener_client.get_input_entity(user_bot_id)
                        sent_request= await listener_client(functions.messages.SendMessageRequest(
                            peer=me_entity,
                            message= str(manage_group_id) + ' cdrom request',
                            no_webpage=True
                        ))
                    except Exception as e:
                        if debug_mode == True:
                            print('Error : send message error' + str(e))
                    #await bot_listener_client.disconnect()

                elif text_arg[0] == '_howtounban':
                    try:
                        await event.reply('Clicked Removed Users\n\nhttps://ibb.co/kMwydJ3')
                        await event.reply('Swipe to unban\n\nhttps://ibb.co/zr9hGV4')
                    except Exception as e:
                        await event.reply('Error: ' + str(e))
                    #await listener_client.disconnect()
                elif text_arg[0] == '_howtoban':
                    try:
                        await event.reply('Reply to cdrom report message\n\nhttps://ibb.co/jyQCjGW')
                        await event.reply('Banned\n\nhttps://ibb.co/6XBZMck')
                    except Exception as e:
                        await event.reply('Error: ' + str(e))
                    #await listener_client.disconnect()
                elif text_arg[0] == '_clear':
                    #clear all message with user bot chat
                    #listener_client = TelegramClient(tg_config.setting['session']['runtime']+ '_' + str(manage_group_id), api_id, api_hash)
                    try:
                        #await listener_client.start()
                        target = await listener_client.get_input_entity(event.chat_id)
                        await listener_client(functions.messages.DeleteHistoryRequest(
                            peer=target,
                            max_id=0,
                            just_clear=True,
                            revoke=True
                        ))
                    except Exception as e:
                        await event.reply('Error: ' + str(e))
                    #await listener_client.disconnect()
                else:
                    if len(text_arg) > 1:
                        if text_arg[0] == '_delmsg':
                            #delete group messages
                            try:
                                day=int(text_arg[1])
                            except Exception as e:
                                await event.reply('Please input number of days in integer (0 will delete all messages!).')
                            else:

                                if day >= 0:
                                    #listener_client = TelegramClient(tg_config.setting['session']['runtime']+ '_' + str(manage_group_id), api_id, api_hash)
                                    #await listener_client.start()
                                    if day > 0:
                                        n_datetime=datetime.now() - timedelta(days=day)
                                    else:
                                        n_datetime=datetime.now()
                                    start=True
                                    total=0
                                    offset=0
                                    message_ids=[]
                                    message_selected=[]
                                    #select messages to be deleted
                                    try:

                                        while start == True or total > 0:
                                            my_channel= await listener_client.get_input_entity(manage_group_id)
                                            to_be_deleted = await listener_client(functions.messages.GetHistoryRequest(
                                                peer=my_channel,
                                                offset_date=n_datetime,
                                                offset_id=0,
                                                add_offset=offset,
                                                limit=100,
                                                max_id=0,
                                                min_id=0,
                                                hash=0
                                            ))
                                            offset+=100
                                            start=False
                                            total=len(to_be_deleted.messages)
                                            #print(to_be_deleted.stringify())
                                            message_selected.extend(to_be_deleted.messages)
                                            if len(message_selected) >= max_delete_message:
                                                break
                                    except Exception as e:
                                        await event.reply('Error: ' + str(e))
                                    else:
                                        if len(message_selected) == 0:
                                            await event.reply('No message can be deleted.')
                                        else:
                                            for msg in message_selected:
                                                message_ids.append(msg.id)
                                                #print('---incoming--- ' + str(msg.id))
                                            try:
                                                deleted = await listener_client(functions.channels.DeleteMessagesRequest(
                                                    channel=my_channel,
                                                    id=message_ids
                                                ))
                                            except Exception as e:
                                                await event.reply('Error :' + str(e))
                                            else:
                                                await event.reply(str(deleted.pts_count) + ' message(s) is/are deleted')
                                    #await listener_client.disconnect()
                        else:
                            await event.reply('Invalid command.')
                    else:
                        await event.reply('Invalid command.')
            await os.remove(tg_config.setting['session_path'] + str(event.from_id))


async def this_user_info(id,batch):
    #print('this_user_info')
    #print(id)
    if type(id) != int:
        return None

    message_info=None
    db = await aiomysql.connect(host='localhost', port=3306,
                               user=db_username, password=db_pwd,
                               db=db_name, loop=loop,
                               autocommit=True)

    #db = pymysql.connect("localhost",db_username,db_pwd,db_name)
    cursor = await db.cursor()
    async with db.cursor() as cursor:
        #cursor.execute('SET NAMES utf8mb4')
        if batch:
            sql = "SELECT user_id, username, group_id  FROM tg_users WHERE batch_id = %s" % (id)
            try:
                await cursor.execute(sql)
                message_info = await cursor.fetchall()
            except:
                return None
        else:
            sql = "SELECT user_id, username, group_id  FROM tg_users WHERE message_id = %s" % (id)
            try:
                await cursor.execute(sql)
                message_info = await cursor.fetchone()
            except:
                return None
       
    db.close()
    return message_info

async def set_schedule(group_id, action,min_msg):
    if type(group_id) != int:
        return None
    passed=False
    db = await aiomysql.connect(host='localhost', port=3306,
                       user=db_username, password=db_pwd,
                       db=db_name, loop=set_schedule_loop,
                       autocommit=True)

    cursor = await db.cursor()
    async with db.cursor() as cursor:
        try: 
            sql = "UPDATE tg_schedule set status = %s , value = %s where group_id = %s "
            await cursor.execute(sql, (action,min_msg,group_id))
        except:
            print ("Error: unable to set schedule")
        else:
            passed=True

    db.close() 
    return passed


async def set_whitelist(user_id,group_id):
    if type(group_id) != int or type(user_id) != int:
        return None
    result=''
    db = await aiomysql.connect(host='localhost', port=3306,
                       user=db_username, password=db_pwd,
                       db=db_name, loop=loop_w,
                       autocommit=True)

    cursor = await db.cursor()
    async with db.cursor() as cursor:
        sql = "SELECT count(user_id) as total  FROM tg_whitelist WHERE  user_id = %s or group_id = %s "
        try:
            await cursor.execute(sql, (user_id,group_id))
            whitelist = await cursor.fetchone()
        except:
            result='db_error'
            print('Error: unable to select whitelist')
        else:
            if whitelist[0] == 0:
                try: 
                    sql = "INSERT INTO tg_whitelist (user_id,group_id,name) VALUES (%s,%s,'')"
                    await cursor.execute(sql, (user_id,group_id))
                except:
                    print ("Error: unable to set whitelist")
                    result='db_error'
                else:
                    result='ok'
            else:
                result='exist'
                
    db.close() 
    return result

#check if session is locked
def is_locked(user_id):
    session_file = Path(tg_config.setting['session_path']  + str(user_id))
    return session_file.exists()


#load configuration - whitelisted data
db = pymysql.connect("localhost",db_username,db_pwd,db_name)
cursor = db.cursor()
sql = "SELECT user_id,  group_id  FROM tg_whitelist"
try:
    cursor.execute(sql)
    config = cursor.fetchall()
except:
    print ("Error: unable to fetch data")
    db.close()
else:
    db.close()
    if len(config) > 0:
        for conf in config:
            accepted_chat_ids.append(conf[0])
        client = TelegramClient(session_name,api_id,api_hash)
        with client:
            # This remembers the events.NewMessage we registered before

            loop = asyncio.get_event_loop()
            loop_w = asyncio.get_event_loop()
            #set_schedule_loop = asyncio.get_event_loop()
            #loop2 = asyncio.get_event_loop()
            loop.run_until_complete(this_user_info(loop,False))
            loop_w.run_until_complete(set_whitelist(loop_w,''))
            #set_schedule_loop.run_until_complete(set_schedule(set_schedule_loop,None,None))
            #loop2.run_until_complete(insert_ghost(loop2))

            client.add_event_handler(handler)
            client.add_event_handler(outgoing_hander)
            print('(Press Ctrl+C to stop this)')
            client.run_until_disconnected()
    else:
        print('No config loaded..')