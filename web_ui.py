from datetime import datetime
import pickle
import streamlit as st
import pandas as pd
import browser_cookie3

import notice
from fuck_main import run

if 'data' not in st.session_state:
    # print('data not in st.session_state')
    # print('======================init========================')
    st.session_state.data = {
        'student_name': '',
        'student_number': '',
        'phone_number': '',
        # 预约日期
        'target_date': '2023-12-15',
        # 预约时间段白名单
        'target_time_list': ['11:00-12:00','16:00-17:00','17:00-18:00','18:00-19:00','19:00-20:00','21:00-22:00'],
        # 同行人信息 同学的DHID是自动获取的无需填写
        'partners': '[{}]',
        'partners_df_json': pd.DataFrame({'学号': [''], '姓名': [''], '是否同行': [False]}).to_json(orient='records'),#data=[['', '', False]],
        # 不想预约的场地黑名单(凡在此列表的场地永远不会预约) 例子：room_blacklist = ['羽毛球场A3','羽毛球场B4']
        'room_blacklist': [],
        'sleep_time': 0,
        'cookies_string': '',
        'success_count': 0,
        'stop_count': 1,
        'xqdm':1 #学期代码-新接口参数
    }
    # st.session_state.data['partners_df']['是否同行'] = st.session_state.data['partners_df']['是否同行'].astype(bool)

time_options = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00', '20:00-21:00', '21:00-22:00']
default_room_options = []
room_options = []
# default_partners_df = pd.DataFrame(data=[['', '', False]],columns=['学号','姓名','是否同行'])
# default_partners_df['是否同行'] = default_partners_df['是否同行'].astype(bool)
run_times = 1

# 成功日期,场地名名称,时间段
def success_func(target_date, room_namn, time_span):
    st.toast('[3]预约成功场地信息：'+target_date+time_span+room_namn)
    st.session_state.data['success_count'] += 1
    notice.send_notice('[3]预约成功场地信息：'+target_date+time_span+room_namn)

def start_onclick():
    if run_times<1: #运行次数，负数为一直运行
        while st.session_state.data['success_count'] < st.session_state.data['stop_count']:
            run(st.session_state.data, st.toast, st.error, st.exception, success_func)
    else:
        for i in range(int(run_times)):
            run(st.session_state.data, st.toast, st.error, st.exception,success_func)
def read_settings(path='settings_file.pkl'):
    # 读取
    f_read = open(path, 'rb')
    settings_dict_r = pickle.load(f_read)
    f_read.close()
    return settings_dict_r

def save_settings(settings_dict, path='settings_file.pkl'):
    # 字典保存
    # print('======================saving========================')
    # print(settings_dict)
    f_save = open(path, 'wb')
    pickle.dump(settings_dict, f_save)
    f_save.close()
    return True

def try_load_cookie():
    cj = browser_cookie3.load(domain_name='ehall.szu.edu.cn')
    if str(cj).find('_WEU')>-1:
        loaded_cookie_str = get_specific_cookies_by_path(cj)
        st.session_state.data['cookies_string'] = loaded_cookie_str
        st.session_state['cookies_string'] = loaded_cookie_str
        st.toast('Cookie读取成功',icon='✅')
        print(loaded_cookie_str)
    else:
        st.toast('Cookie读取失败：'+str(cj),icon='❌')

def get_specific_cookies_by_path(cookie_jar, cookie_names=['EMAP_LANG','_WEU','route','MOD_AUTH_CAS'], target_path=['/','/qljfwapp/']):
    cookies_string = ""
    for cookie in cookie_jar:
        if cookie.name in cookie_names and cookie.path in target_path:
            cookies_string += f"{cookie.name}={cookie.value};"

    # 移除末尾的分号
    if cookies_string.endswith(";"):
        cookies_string = cookies_string[:-1]

    return cookies_string
def load_onclick():
    try:

        st.session_state.data = read_settings('settings_file.pkl')
        st.toast('配置读取成功',icon='✅')
        st.session_state['student_name'] = st.session_state.data['student_name']
        st.session_state['student_number'] = st.session_state.data['student_number']
        st.session_state['phone_number'] = st.session_state.data['phone_number']
        st.session_state['stop_count'] = st.session_state.data['stop_count']
        st.session_state['xqdm'] = st.session_state.data['xqdm']
        st.session_state['cookies_string'] = st.session_state.data['cookies_string']

        date = datetime.strptime(st.session_state.data['target_date'], '%Y-%m-%d')
        st.session_state['target_date'] = date
        st.session_state['target_time_list'] = st.session_state.data['target_time_list']
        st.session_state['partners_json_show'] = st.session_state.data['partners']
        st.session_state['room_blacklist'] = st.session_state.data['room_blacklist']
        st.session_state['sleep_time'] = st.session_state.data['sleep_time']
        st.session_state.data['success_count'] = 0

        # print(st.session_state.data)
    except Exception as e:
        st.toast(e,icon='❌')

def save_onclick():
    try:
        st.session_state.data['partners_df_json'] = partners_df_edited.to_json(orient='records')
        if(save_settings(st.session_state.data,'settings_file.pkl')):
            st.toast('配置保存成功',icon='✅')
    except Exception as e:
        st.toast('配置保存出错:'+str(e),icon='❌')
        raise e

# def parterns_2df(partners_json):
#     df = pd.read_json(partners_json, orient='records',dtype={'XGH': str, 'XM': str, 'DHID': str})
#     partners_df_empty = pd.DataFrame(columns=['学号','姓名','是否同行'])
#     partners_df_empty['是否同行'] = partners_df_empty['是否同行'].astype(bool)
#     if df.empty:
#         return partners_df_empty
#     df.columns = partners_df_empty.columns
#     df['是否同行'] = True
#     return df

def parterns_2json(p_df):
    p_df = p_df.dropna()
    if p_df.empty or p_df.loc[p_df['是否同行']].empty:
        return '[]'
    df = p_df.loc[p_df['是否同行']].dropna()
    df.drop('是否同行', axis=1, inplace=True)
    df.columns = ['XGH', 'XM']
    df['DHID'] = ''
    partners_json = df.to_json(orient='records', force_ascii=False)
    # print(partners_json)
    return partners_json

with st.sidebar:
    run_times = st.number_input('运行次数(非正就一直运行)',value=1)
    st.button('开始运行', on_click=start_onclick)
    st.button('读取配置', on_click=load_onclick)
    st.button('保存配置', on_click=save_onclick)
    st.button('读取Cookie',on_click=try_load_cookie)
    st.metric('成功次数',value=st.session_state.data['success_count'])

# col1,col2,col3 = st.columns(3)
# with col1:
#     st.button('开始运行', on_click=start_onclick)
# # config_file = st.file_uploader('配置文件',accept_multiple_files=False)
# with col2:
#     st.button('读取配置', on_click=load_onclick)
# with col3:
#     st.button('保存配置', on_click=save_onclick)

st.title('羽毛球场抢票 WebGUI v 1.0')
st.divider()
# st.session_state.data = read_settings('settings_file.pkl')
student_name = st.text_input('君の名字',key='student_name',value=st.session_state.data['student_name'],placeholder='阳菜')
student_number = st.text_input('你的学号',key='student_number',value=st.session_state.data['student_number'],placeholder='2310xxxxxx')
cookies_string = st.text_input('你的cookie',key='cookies_string',value=st.session_state.data['cookies_string'],placeholder='',help='在预约界面：https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do 按F12进入开发者工具，在网络选项中找到请求接口记录，再找到cookie,复制过来')
target_date = st.date_input('预约日期',key='target_date')
target_time_list = st.multiselect('预约时间段(多选)',key='target_time_list',default=st.session_state.data['target_time_list'],options=time_options)
room_blacklist = st.multiselect('场地黑名单(多选)',key='room_blacklist',default=st.session_state.data['room_blacklist'],options=room_options,help='不想预约的场地黑名单(凡在此列表的场地永远不会预约) 例子：room_blacklist = [\'羽毛球场A3\',\'羽毛球场B4\']')

partners_json_show = st.text_input(label='同行人请求JSON(无需编辑)',key='partners_json_show',value=st.session_state.data['partners'],disabled=True)
partners_df_json_show = st.text_input(label='DataFrame JSON(无需编辑)',key='partners_df_json_show',value=st.session_state.data['partners_df_json'],disabled=True)
st.text('同行人管理',help="勾选了“是否同行”的才会提交")

# print('======================partners_df_json========================')
# print(st.session_state.data['partners_df_json'])

# 将 JSON 转为 DataFrame
try:
    partners_df = pd.read_json(partners_df_json_show, orient='records', dtype={'学号': str, '姓名': str, '是否同行': bool})
except Exception as e:
    st.error(f"Error converting JSON to DataFrame: {e}")
    partners_df = pd.DataFrame()
if not partners_df.empty:
    st.session_state.data['partners_df_json'] = partners_df.to_json(orient='records')

partners_df_edited = st.data_editor(partners_df,num_rows="dynamic",hide_index=True,use_container_width=True)
partners_df_json_show = partners_df_edited.to_json(orient='records')
sleep_time = st.number_input('轮询间隔(s)',key='sleep_time',min_value=0,value=0,help='每次查询场地请求的时间间隔，为0则不间隔轮询')
stop_count = st.number_input('抢多少个场停止',key='stop_count',value=1,min_value=1,max_value=2,help='最多为2，默认1请误贪心')
phone_number = st.text_input('手机号码',key='phone_number',help='新接口需要填手机号')
xqdm = st.text_input('学期代码',key='xqdm', value=1,help='第一学期填1，第二学期填2')
# print('=======================partners_df_edited=======================')
# print(partners_df_edited)
st.session_state.data['student_name'] = student_name
st.session_state.data['student_number'] = student_number
st.session_state.data['cookies_string'] = cookies_string
st.session_state.data['target_date'] = target_date.strftime('%Y-%m-%d')
st.session_state.data['target_time_list'] = target_time_list
# st.session_state.data['partners_df_json'] = partners_df_edited.to_json(orient='records')
st.session_state.data['partners'] = parterns_2json(partners_df_edited)
st.session_state.data['room_blacklist'] = room_blacklist
st.session_state.data['sleep_time'] = sleep_time
st.session_state.data['xqdm'] = xqdm
st.session_state.data['stop_count'] = stop_count
st.session_state.data['phone_number'] = phone_number
# print(st.session_state.data)




