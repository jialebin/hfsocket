from datetime import datetime

from sqlalchemy import (Column, Integer, String,
                        Boolean, DateTime)

from libs.db.dbsession import Base


class ChatLog(Base):

    __tablename__ = 'chat_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    receiver_id = Column(Integer, comment="接收方")
    sender_id = Column(Integer, comment="发送方")
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    message = Column(String(128), comment="消息")
    type = Column(String(8), comment='消息类型')


'''
用户消息设计
消息设计
{
sender： 发送方 (用户/客服)(user/customer_service)
type：消息类型(image/str/url/list)，list为历史记录
create_time: 发送时间
message: 发送内容[image,url 均传输字符串，图片为链接暂未实现图片传输]
}

建立链接后首先发送列表消息，为最后n条聊天信息记录
{
“type”：list
message：[
        {
        sender: user
        type：str
        create_time: 2020-05-10 12:21:12
        message: "这是一条聊天记录"
        },
        {
        sender: customer_service
        type：str
        create_time: 2020-05-10 12:21:13
        message: "这是一条聊天记录"
        },
        {
        sender: user
        type：str
        create_time: 2020-05-10 12:21:14
        message: "这是一条聊天记录"
        },
        {
        sender: customer_service
        type：str
        create_time: 2020-05-10 12:21:15
        message: "这是一条聊天记录"
        },
        {
        sender: user
        type：str
        create_time: 2020-05-10 12:21:16
        message: "这是一条聊天记录"
        },   
    ]
}

服务端-客户端实时消息
{
    type：str
    create_time: 2020-05-10 12:21:16
    message: "这是一条聊天消息"
},
'''

"""
客服消息设计
接受消息设计
{
sender：发送者 (那个用户发送的消息)
type：消息类型(image/str/url/list)，list为历史记录
create_time: 发送时间
message: 发送内容[image,url 均传输字符串，图片为链接暂未实现图片传输]
}

{
receiver： 接收方 (那个用户接受消息)
type：消息类型(image/str/url/list)，list为历史记录
create_time: 发送时间
message: 发送内容[image,url 均传输字符串，图片为链接暂未实现图片传输]
}

有用户链接时的消息
{
receiver： 接收方 (那个用户接受消息)
type：message
create_time: 发送时间
message: {'user": 60}
}

"""