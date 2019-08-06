from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import hashlib
from . import receive
from . import reply


# Create your views here.
# django默认开启了csrf防护，@csrf_exempt是去掉防护
# 微信服务器进行参数交互，主要是和微信服务器进行身份的验证
@csrf_exempt
def check_signature(request):
    if request.method == "GET":
        print("request: ", request)
        # 接受微信服务器get请求发过来的参数
        # 将参数list中排序合成字符串，再用sha1加密得到新的字符串与微信发过来的signature对比，如果相同就返回echostr给服务器，校验通过
        # ISSUES: TypeError: '<' not supported between instances of 'NoneType' and 'str'
        # 解决方法：当获取的参数值为空是传空，而不是传None
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        # 微信公众号处配置的token
        token = str("Txy159wx")

        hashlist = [token, timestamp, nonce]
        hashlist.sort()
        print("[token, timestamp, nonce]: ", hashlist)

        hashstr = ''.join([s for s in hashlist]).encode('utf-8')
        print('hashstr before sha1: ', hashstr)

        hashstr = hashlib.sha1(hashstr).hexdigest()
        print('hashstr sha1: ', hashstr)

        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("weixin index")
    elif request.method == "POST":
        otherContent = autoreply(request)
        return HttpResponse(otherContent)
    else:
        print("你的方法不正确....")


def autoreply(request):
    try:
        webData = request.body
        print("Handle POST webData is: ", webData)

        recMsg = receive.parse_xml(webData)
        if isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text':
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            content = recMsg.Content
            replyMsg = reply.TextMsg(toUser, fromUser, content)
            return replyMsg.send()
        else:
            print("暂不处理")
            return "success"
    except Exception as e:
        print(e)

# ② 微信服务器推送的消息格式是xml格式的
#   使用ElementTree来解析出不同的xml内容返回不同的回复信息，就实现了基本的自动回复功能
# def autoreply(request):
#     try:
#         # 获取用户发给的信息，并用ET解析
#         webData = request.body
#         print("POST webData is", webData)
#         xmlData = ET.fromstring(webData)
#
#         msg_type = xmlData.find('MsgType').text
#         ToUserName = xmlData.find('ToUserName').text
#         FormUserName = xmlData.find('FromUserName').text
#         CreateTime = xmlData.find('CreateTime').text
#         MsgType = xmlData.find('MsgType').text
#         MsgId = xmlData.find('MsgId').text
#
#         toUser = FormUserName
#         fromUser = ToUserName
#
#         if msg_type == 'text':
#             content = '你好，你已调试成功了，你真帅'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             print("Yeah!!!!")
#             print("replyMsg: ", replyMsg)
#             return replyMsg.send()
#         elif msg_type == 'image':
#             content = '图片已收到，谢谢'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#         elif msg_type == 'voice':
#             content = '语音已收到，谢谢'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#         elif msg_type == 'video':
#             content = '视频已收到，谢谢'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#         elif msg_type == 'shortVideo':
#             content = '小视频已收到，谢谢'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#         elif msg_type == 'location':
#             content = '位置已收到，谢谢'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#         else:
#             msg_type == 'link'
#             content = '链接已收到，谢谢！'
#             replyMsg = TextMsg(toUser, fromUser, content)
#             return replyMsg.send()
#     except Exception as e:
#         return e
#

# class Msg(object):
#     def __init__(self, xmlData):
#         print("接受到的数据：", xmlData)
#         self.ToUserName = xmlData.find('ToUserName').text
#         self.FromUserName = xmlData.find('FormUserName').text
#         self.CreateTime = xmlData.find('CreateTime').text
#         self.MsgType = xmlData.find('MsgType').text
#         self.MsgId = xmlData.find('MsgId').text
#
#
# class TextMsg(Msg):
#     def __int__(self, toUserName, fromUserName, content):
#         self.__dict = dict()
#         self.__dict['ToUserName'] = toUserName
#         self.__dict['FromUserName'] = fromUserName
#         self.__dict['CreateTime'] = int(time.time())
#         self.__dict['Content'] = content
#
#     def send(self):
#         XmlForm = """
#         <xml>
#         <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
#         <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
#         <CreateTime>{CreateTime}</CreateTime>
#         <MsgType><![CDATA[text]]></MsgType>
#         <Content><![CDATA[{Content}]]></Content>
#         </xml>
#         """
#         return XmlForm.format(**self.__dict)
