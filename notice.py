import requests
import time
import json
import datetime
import random
import os

event_name="notice_phone"
#event_name="detail_phone"
key="hKefUotd7wksifHydjMce6hEuePcvQDEqBo5f_cDF16"

def send_notice(text,t=1):
    #if t==1:
    #    open_app()
    '''
    wt=datetime.datetime.now()
    text=text+" "+str(wt.hour)+":"+str(wt.minute)
    '''
    wt=time.localtime()
    text=text+" "+str(wt.tm_hour)+":"+str(wt.tm_min)
    global event_name
    global key
    url = "https://maker.ifttt.com/trigger/"+event_name+"/with/key/"+key
    data = {'value1': text}
    data = json.dumps(data)
    tmp_t=random.randint(1,10)
    headers = {
            'Content-Type': "application/json",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "a9477d0f-08ee-4960-b6f8-9fd85dc0d5cc,d376ec80-54e1-450a-8215-952ea91b01dd",
            'Host': "maker.ifttt.com",
            'accept-encoding': "gzip, deflate",
            'content-length': "63",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
    }
    tt=0
    while True:
        tt=tt+1
        if tt>20:
            #input("Some Error,maby net,input to continue:")
            print("notice error")
            tt=0
        try:
            response = requests.post(url=url,data=data,headers=headers,timeout=10)
        except Exception as e:
            print("send_notice失败: ",end="")
            if "time out" in str(e) or "timed out" in str(e):
                print("timed out")
            elif "HTTPSConnectionPool" in str(e):
                time.sleep(5)
                print("HTTPCP")
            else:
                print(e)
            time.sleep(5)
            continue
        else:
            break
    print(response.text)



if __name__ == '__main__':
    send_notice("123",0)
