# Telegram UserBot Beta Version for SuperGroup

It's Work , but use it as your Risk :)

## Requirement

1. Linux platform 
2. Python 3.x
3. Python package [Telethon](https://github.com/LonamiWebs/Telethon)
4. Python package [pymysql](https://github.com/PyMySQL/PyMySQL)
5. Python package [aiomysql](https://github.com/aio-libs/aiomysql)
6. Telegram User Account
7. MySQL database
8. (optional) nodejs


## Preparation 

1. Telegram account which you are using for a long time or few weeks.<br/>Since Telegram will limit your API request if they think the account may be used for spamming.
2. Get app id and app hash of your telegram account (https://my.telegram.org/auth)<br/>
Reference : (https://core.telegram.org/api/obtaining_api_id)
3. Setup python 3.x 
4. Install telegram core api package  - [Telethon](https://github.com/LonamiWebs/Telethon)
```shell
pip3 install telethon

```
5. Install pm2 for running as service (nodejs is needed)


## Description
{userbot} is Telegram account which use as user bot<br/>
{admin} is Telegram user who control the group via user bot (can anyone else)<br/>
ONE group is allowed for each {admin} to manage

### One time Setup
Run me.py to get your {userbot} Telegram user ID<br/>
At first time, it will ask for {userbot}'s  authentication<br/>
Enter <br/>
1. phone number 
2. Code sent to your phone or Telegram
3. Two step verification password if ANY<br/>
(Active Session will be created in {userbot} Telegram account, you can terminate it ANYTIME to stop granting permission to the BOT!! )
<br/>

Edit setting in tg_config.py<br/>

- user_bot_id : {userbot} Telegram user ID
- app_id : App ID you get from https://my.telegram.org/auth
- app_hash : App Hash you get from https://my.telegram.org/auth
- session_path : it is the path of user session file , to indicate process is running by this user (filename is the ID of user)
- session.listener : session name of session file generated by SQLite of Telethon (listener is for running event.py)
- session.bot : session name of session file generated by SQLite of Telethon (bot is for running your own script)
- database : MySQL database for whitelist user as {admin} to manage his group 

### Setup for each group (need do by ADMIN of group)

- Let {userbot} join the group that need to manage by ADMIN of group <br/>
- Give {userbot} permissions in the group : "Delete message" and "Ban users" (go to : Group info > Edit > Administrators > )<br/>
- {admin} send any message to {userbot}<br/>

### Setup for each group
- {userbot} send command to himself (via Saved Message) 
- run [_users] and [_groups] via Saved message to get user id of {admin} and group id of group to be managed 
- run [_whitelist m n]   m = user id, n = group id , whitelist a new user {admin} to manage this group (script or pm2 service need restart)<br/>


### Execute
Run event.py as service using pm2 <br/>

## Commands
### admin command : <br/>
{admin} talk to {userbot} like a normal private chat (do not use Secret Chat). See command below : <br/>
- [_help] list help menu
- [_clear] clear all messages with {userbot}
- [_delmsg n] delete all messages of group before n days ago<br/>
 HINTS: it may consume much time if there are too many messages.<br/>
 Maximum 1000 messages for one batch delete action, you can run the command several times to delete ALL messages.<br/>
 WARNING: 0 will delete messages of group before NOW
- [_cdrom] request of listing cdrom report, system admin will run it for you soon<br/>
 *  to ban user, reply to message in cdrom report

### userbot command : <br/>
{userbot} send command to {userbot} via Saved Message<br/>
- [_groups] list all group id joined
- [_users] list all user id with chat
- [_clear] clear all messages in Saved Message
- [_whitelist m n] whitelist m = user id, n = group id 


## CDRom Report
It is the report to tell you which members may consider as CDRom in the group. However, it consume much time if too many members in the group due to the limitation of API or my coding limitation :), it first get all participants of group which only include brief information, then it iterates all members by searching their message (one request for one member <- wtf, no choice! ), my purpose is getting the message COUNT of all members, so it doesn't matter if there are huge of messages. <br/><br/>

It would take few minutes for it.. <br/><br/>

And run it using another session, run the cdrom.py at server directly, good luck ! :)


     
