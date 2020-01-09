#!/usr/bin/env python

import itchat

@itchat.msg_register(itchat.content.PICTURE, isGroupChat=True)
def scanner(msg):
    print(msg['MsgType'])
    print(msg['ActualNickName'])
    print(msg['MsgId'])
    print(msg['Content'])
    print(msg['Text'])
    print(msg['FileName'])
    msg.download(msg['FileName'])

itchat.auto_login(hotReload=True, enableCmdQR=True)
itchat.run()