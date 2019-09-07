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
session_name=tg_config.setting['session']['bot']
db_username=tg_config.setting['database']['username']
db_pwd=tg_config.setting['database']['pwd']
db_name=tg_config.setting['database']['db']

config=[]
admin_user_id=0
min_message=10 #min message count criteria to determine as cdrom
num_to_batch= 20 #number of cdrom users reached to use batch message approach
num_per_batch=50 #number of cdrom users as a batch
future_year = 2028

def tg(group_id):

    #load configuration - whitelisted data
    db = pymysql.connect("localhost",db_username,db_pwd,db_name)
    cursor = db.cursor()
    sql = "SELECT user_id,  group_id  FROM tg_whitelist WHERE group_id = %s" % (group_id)
    try:
        cursor.execute(sql)
        config = cursor.fetchone()
    except:
        print ("Error: unable to fetch data")
        db.close()
        sys.exit()
    else:
        db.close()
        if config:
            admin_user_id = config[0]
        else:
            print('No config loaded..')
            sys.exit()

    try:
        # tg client start
        # same session would lock the database, nothing can do if this session is in process
        client = TelegramClient(session_name, api_id, api_hash)
        client.start()
    except Exception as e:
        print(str(e))
    else:


        try:
            #to play safe, run get dialog first 

            dialog_result = client(functions.messages.GetDialogsRequest(
                offset_date=datetime.datetime(future_year, 12, 25),
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=200,
                hash = 0
            ))

            #clear all message history with admin user first 
            client(functions.messages.DeleteHistoryRequest(
                peer=client.get_input_entity(admin_user_id),
                max_id=0,
                just_clear=True,
                revoke=True
            ))
        except Exception as e:
            print(str(e))
        print('history deleted')
        try:
            seperator = ','
            users=[]
            outputs=[]
            mychannel=client.get_input_entity(group_id)
            start=True
            total=0
            offset=0
            total_ghost=0  
            db = pymysql.connect("localhost",db_username,db_pwd,db_name)
            cursor = db.cursor()
            #delete everything first 
            sql='DELETE FROM tg_users where group_id = %s ' % (group_id)
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
               
            cursor.execute('SET NAMES utf8mb4')
            insert_data=[]
            while start == True or total > 0:
                channel_members=client(functions.channels.GetParticipantsRequest(
                    channel=mychannel,
                    filter=types.ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=200,
                    hash=0
                ))
                
                print('get participants ' + str(offset))
                print('')
                offset += 200
                start=False
                total=len(channel_members.users)
                #print(channel_members.stringify())
                if len(channel_members.users) > 0:
                    for user in channel_members.users:
                        user_field=()
                        if user.deleted == True or admin_user_id == user.id or user.id == tg_config.setting['user_bot_id']:
                            continue
                        print('loop' + str(user.id))
                        result = client(functions.messages.SearchRequest(
                           peer=mychannel,
                           q='',
                           filter=types.InputMessagesFilterEmpty(),
                           min_date=datetime.datetime(future_year, 6, 25),
                           max_date=datetime.datetime(future_year, 6, 25),
                           offset_id=0,
                           add_offset=0,
                           limit=1,
                           max_id=0,
                           min_id=0,
                           hash=0,
                           from_id=client.get_input_entity(user.id)
                        ))
                        
                        #print(result.stringify())
                        if user.bot == False and result.count > min_message:
                            continue
                            
                        total_ghost += 1

                        username=''
                        first_name=''
                        last_name=''
                        is_bot=0

                        user_field = user_field + (group_id,)
                        user_field = user_field + (user.id,)
                        #user_field.append(str(group_id))
                        #user_field.append(str(user.id))
                       
                        if user.username is not None:
                            username=user.username
                            
                        if user.first_name is not None:
                            first_name=user.first_name
                            
                        if user.last_name is not None:
                            last_name=user.last_name

                        if user.bot == True:
                            is_bot=1

                        user_field = user_field + (username,)
                        user_field = user_field + (first_name,)
                        user_field = user_field + (last_name,)
                        user_field = user_field + (result.count,)
                        user_field = user_field + (is_bot,)
                        
                        #user_field.append("'"+username+"'")    
                        #user_field.append("'"+first_name+"'")    
                        #user_field.append("'"+last_name+"'")    
                        #user_field.append(str(result.count))    
                            
                        #sql_str='(' + seperator.join(user_field) + ') '
                        insert_data.append(user_field)
        
            if len(insert_data) > 0:
                try:
                   cursor.executemany('INSERT INTO tg_users(group_id,user_id,username,first_name,last_name,message_count,bot) VALUES (%s, %s, %s, %s, %s, %s, %s) ', insert_data)
                   db.commit()
                except:
                   db.rollback()
            db.close()
            user_field=None 
            insert_data=None 

        except Exception as e:
            client.disconnect()
            print(str(e))
        else:
            client.disconnect()
            if total_ghost >0:
                tg_send(group_id,admin_user_id,total_ghost)

def tg_send(group_id,admin_user_id,total_ghost):
    try:
        client = TelegramClient(session_name, api_id, api_hash)
        client.start()
    except Exception as e:
        print(str(e))
    else:
        db = pymysql.connect("localhost",db_username,db_pwd,db_name)
        cursor = db.cursor()
        cursor.execute('SET NAMES utf8mb4')
        sql = "SELECT user_id, username, first_name, last_name, message_count , bot FROM tg_users WHERE group_id = %s" % (group_id)
        try:
           cursor.execute(sql)
           results = cursor.fetchall()
        except:
           print ("Error: unable to fetch data")
           db.close() 
        else:   

            mychannel=client.get_entity(group_id)
            if len(results) > 0:
                if total_ghost > num_to_batch:
                    chunked_results= chunks(results,num_per_batch)
                    #there are too many cdrom, so group together as 50 cdrom as one batch to send 
                    #reply a batch to ban whole batch of cdrom users, or reply with id (use comma to separate)
                    for this_c in chunked_results:
                        batch_messages=[]
                        update_user_id=[]
                        for row in this_c:
                            user_id = row[0]
                            username = row[1]
                            first_name = row[2]
                            last_name = row[3]
                            message_count = row[4]
                            bot = row[5]
                            d_username=''
                            d_bot=''
                            if username:
                                d_username = ' @'+ username.strip()
                            if bot == 1:
                                d_bot='-- BOT --\n'
                            message = d_bot + 'msg count : ' + str(message_count) + '\n' + str(user_id) + '\n' + d_username + ' ' + first_name + ' ' + last_name + '\n\n'
                            batch_messages.append(message)
                            update_user_id.append(str(user_id))
                            
                        #send message here
                        try:
                            batch_msg= ''.join(batch_messages)
                            result=client(functions.messages.SendMessageRequest(
                                peer=client.get_input_entity(admin_user_id),
                                message=batch_msg,
                                no_webpage=True
                            ))
                            #print(result.stringify())
                        except Exception as e:
                            print(str(e))
                        else:
                            print('batch sent '+ str(result.id))
                            #update batch id for this batch users 
                            try:
                              id_t=','.join(update_user_id)
                              sql='UPDATE tg_users set batch_id =  ' + str(result.id) + ' WHERE user_id IN (' + id_t + ') and group_id = ' + str(group_id)
                              cursor.execute(sql)
                              db.commit()
                            except:
                                db.rollback()
                                print ("Error: unable to update message")        
                        time.sleep(2)  
             
                else:
                    update_sql_when=[]
                    update_user_id=[]
                    #send per cdrom, reply to ban
                    for row in results:
                        user_id = row[0]
                        username = row[1]
                        first_name = row[2]
                        last_name = row[3]
                        message_count = row[4]
                        bot = row[5]
                        d_username=''
                        d_bot=''
                        if username:
                            d_username = ' @'+ username.strip()
                        if bot == 1:
                            d_bot='-- BOT --\n'
                        message = d_bot + 'msg count : ' + str(message_count) + '\n' + str(user_id) + '\n' + d_username + ' ' + first_name + ' ' + last_name
                        try:
                            result=client(functions.messages.SendMessageRequest(
                                peer=client.get_input_entity(admin_user_id),
                                message=message,
                                no_webpage=True
                            ))
                            #print(result.stringify())
                        except Exception as e:
                            print(str(e))
                        else:
                            update_user_id.append(str(user_id))
                            update_sql_when.append( 'WHEN user_id = '+str(user_id)+' THEN ' + str(result.id))
                            print('sent '+ str(result.id))
                        time.sleep(2)
                    try:
                        sql_t= ' '.join(update_sql_when)
                        id_t=','.join(update_user_id)
                        sql='UPDATE tg_users set message_id = CASE ' +   sql_t + ' END WHERE user_id IN (' + id_t + ') and group_id = ' + str(group_id)
                        cursor.execute(sql)
                        db.commit()
                    except:
                        db.rollback()
                        print ("Error: unable to update message")
            else:        
                try:
                    client(functions.messages.SendMessageRequest(
                        peer=client.get_input_entity(admin_user_id),
                        message='Seems no CDRom..',
                        no_webpage=True
                    ))
                except Exception as e:
                    print(str(e))   
                
            finish_message='-----------------------\n' + mychannel.title + ' cdrom report ended'
            try:
                gresult=client(functions.messages.SendMessageRequest(
                    peer=client.get_input_entity(admin_user_id),
                    message=finish_message,
                    no_webpage=True
                ))
            except Exception as e:
                print(str(e))   
          
            db.close()
        client.disconnect()   
        
def chunks(clist, n):
    n = max(1, n)
    return (clist[i:i+n] for i in range(0, len(clist), n))
    
    
if len(sys.argv) > 1:
    group_id=int(sys.argv[1])
    #session_name = session_name + '_' + str(group_id)
    tg(group_id)
 
