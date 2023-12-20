import json
from http.cookies import SimpleCookie
from json import JSONDecodeError

import requests
import time

# 固定字段
timeListUrl = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/sportVenue/getTimeList.do"
roomListUrl = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/modules/sportVenue/getOpeningRoom.do"
getOrderNumberUrl = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/sportVenue/getOrderNum.do"
reserveRoomUrl = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/sportVenue/insertVenueBookingInfo.do"

# ---------------- 待填信息 -----------------#
# settings = {
#     'student_name': '',
#     'student_number': '',
#     # 预约日期
#     'target_date': '2023-12-16',
#     # 预约时间段白名单
#     'target_time_list': ['11:00-12:00', '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00', '21:00-22:00'],
#     # 同行人信息 同学的DHID是自动获取的无需填写
#     'partners': '[{}]',
#     # 不想预约的场地黑名单(凡在此列表的场地永远不会预约) 例子：room_blacklist = ['羽毛球场A3','羽毛球场B4']
#     'room_blacklist': [],
#     'sleep_time': 0,
#     'cookies_string': ''
# }


# ------------------------------------------#

# cookie编码处理
# def cookie2Dict(cookie):
#     return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}

def cookie2Dict(cookie_str):
    cookie = SimpleCookie(cookie_str)
    cookie_dict = {key: morsel.value for key, morsel in cookie.items()}
    return cookie_dict

def getPartnerInfo(partners, DHID):
    jsonObject = json.loads(partners)
    if type(jsonObject) == list:
        for partner in jsonObject:
            partner['DHID'] = DHID
        print(json.dumps(jsonObject))
        return json.dumps(jsonObject)
    else:
        return "[]"


def getTimeList(settings,reserveDate,info_func,error_func):
    cookies = cookie2Dict(settings['cookies_string'])
    session = requests.session()
    print('==============================')
    print(settings['cookies_string'])
    res = session.post(url=timeListUrl, data={'XQ':settings['xqdm'],'YYRQ': reserveDate, 'YYLX': '1.0', 'XMDM': '001'}, cookies=cookies)
    print({'YYRQ': reserveDate, 'YYTYPE': '1.0', 'XMDM': '001'})
    print(cookies)
    info_func('目标时间段'+ reserveDate + '查询请求发送成功, 响应信息：'+ res.text)
    print('目标时间段', reserveDate, '查询请求发送成功, 响应信息：', res.text)
    if res.status_code == 200:
        res = json.loads(res.text)
        # info_func('时间段'+ reserveDate+'查询成功,字段信息：'+ str(res))
        print('时间段', reserveDate, '查询成功,字段信息：', res)
    else:
        error_func('时间段'+ reserveDate+ '查询失败, httpcode=='+ str(res.status_code))
        print('时间段', reserveDate, '查询失败, httpcode==', str(res.status_code))
    return res


def getRoomList(settings, reserveDate='2023-09-27', time_span='17:00-18:00'):
    startTime = time_span.split('-')[0]
    endTime = time_span.split('-')[1]
    cookies = cookie2Dict(settings['cookies_string'])
    session = requests.session()
    res = session.post(url=roomListUrl,
                       data={'XMDM': '001', 'YYRQ': reserveDate, 'YYLX': '1.0',
                             'KSSJ': startTime, 'JSSJ': endTime, 'XQDM': settings['xqdm']}, cookies=cookies)
    if res.status_code == 200:
        try:
            res = json.loads(res.text)
        except Exception as e:
            if isinstance(e, JSONDecodeError) and '该预约日期暂未开放预约' in res.text:
                raise Exception('该预约日期暂未开放预约')
            else:
                raise e
        if (res['code'] == '0'):
            print('时间段', reserveDate, time_span, '场地查询成功,字段信息：', res)
            res = res['datas']['getOpeningRoom']['rows']
        else:
            print('时间段', reserveDate, time_span, '查询失败, code==', res['code'])
    else:
        print('时间段', reserveDate, time_span, '查询失败, httpcode==', str(res.status_code))
    return res


def fuckingGetIt(settings,CDWID='b0cb9490b2de4a10b7ded4496c0ed670', reserve_date='2023-09-27', time_span='18:00-19:00'):
    cookies = cookie2Dict(settings['cookies_string'])
    start_datetime = reserve_date + ' ' + time_span.split('-')[0]
    end_datetime = reserve_date + ' ' + time_span.split('-')[1]
    session = requests.session()
    success = False
    # 拿到了orderNum
    order_num = ''  # orderRes['DHID']
    # print('[3]订单号获取成功')
    res = session.post(url=reserveRoomUrl,
                       data={'DHID': order_num, 'YYRGH': settings['student_number'],
                             'YYRXM': settings['student_name'],'CYRS':'','YYRXM':settings['student_name'],
                             'LXFS': settings['phone_number'],
                             'CGDM': '001', 'CDWID': CDWID, 'XMDM': '001', 'XQWID': '1',
                             'KYYSJD': time_span, 'YYRQ': reserve_date, 'YYLX': '1.0',
                             'YYKS': start_datetime, 'YYJS': end_datetime,
                             #'QTYYR': getPartnerInfo(settings['partners'], order_num),
                             'PC_OR_PHONE': 'pc'}, cookies=cookies)
    if res.status_code == 200:
        # res = json.loads(res.text)
        if ('成功' in res.text or 'success' in res.text):
            print('[4]预约成功！', reserve_date, time_span, CDWID,
                  '速去支付 http://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do#/myBooking')
            success = True
        else:
            print('[4]场地预约失败', res.text, reserve_date, time_span, CDWID)

    # orderRes = session.post(url=getOrderNumberUrl, cookies=cookies)
    # print('==============orderRes==============')
    # print(orderRes.text)
    #
    # success = False
    # if orderRes.status_code == 200:
    #     orderRes = json.loads(orderRes.text)
    #     if (orderRes['success']):
    #
    #
    #     else:
    #         print('[4]场地预约失败', reserve_date, time_span, CDWID)
    # else:
    #     print('[3]获取订单号失败')
    return success

def run(settings, info_func, error_func ,except_func,success_func):
    print(settings)
    target_date = settings['target_date']
    target_time_list = settings['target_time_list']
    try:
        timeList = getTimeList(settings,settings['target_date'],info_func,error_func)
        if type(timeList) == list:
            # 成功返回了list
            # 对可预约时间段进行遍历
            time_no_available = True # 若有可用时间则为False
            for item in timeList:
                if (item['NAME'] in target_time_list and item['disabled'] == False):
                    time_no_available = False
                    info_func('[1]时间段'+target_date+item['NAME']+'可预约')
                    print('[1]时间段', target_date, item['NAME'], '可预约')


                    print('[2]查询场地')
                    # 查询该时间段场地
                    roomList = getRoomList(settings,target_date, item['NAME'])
                    if type(roomList) == list:
                        # 成功返回了list
                        # 对可预约场地进行遍历
                        room_no_available = True # 若有可用场地则为False
                        for roomItem in roomList:
                            if (roomItem['CDMC'] not in settings['room_blacklist'] and roomItem[
                                'disabled'] == False):

                                room_no_available = False

                                info_func('[2]场地'+ roomItem['CDMC']+ target_date + item['NAME']+ '可预约，尝试预约中!')
                                print('[2]场地', roomItem['CDMC'], target_date, item['NAME'], '可预约')

                                if(fuckingGetIt(settings,roomItem['WID'], target_date, item['NAME'])):
                                    info_func('[3]预约成功！')
                                    success_func(target_date,roomItem['CDMC'],item['NAME'])
                                    print('!!!!!!!!!!预约成功！')
                                    return
                                else:
                                    info_func('[3]预约失败！')
                        if(room_no_available):
                            print('[2]场地查询结束，没有可用场地')
                            info_func('[2]场地查询结束，没有可用场地')
                    else:
                        error_func('[2]时间段 '+ target_date+item['NAME']+'场地查询失败')
                        print('[2]时间段', target_date, item['NAME'], '场地查询失败')
            if(time_no_available):
                info_func('[1]所有时间段已约完了')
                print('[1]所有时间段已约完了')
        else:
            error_func('[1]可预约时间段查询未成功返回list')
            print('[1]可预约时间段查询未成功返回list')
    except Exception as e:
        if isinstance(e,JSONDecodeError):
            error_func('请求解析失败，可能是Cookies失效，请重新手动更新Cookies')
        except_func(e)
        print(e)
    # 休眠间隔 单位为秒
    print('============= 单轮结束 =============')
    time.sleep(settings['sleep_time'])


# if __name__ == '__main__':
#     print('running')
#     def _f1(_t):
#         return
#     run(settings,_f1,_f1,_f1)
