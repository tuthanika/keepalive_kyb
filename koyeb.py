#!/usr/bin/python3
# -*- coding: utf8 -*-
"""
说明: 环境变量`KOY_EB`账号密码`-`分割，多账户用&隔开[例如：aaa-bbb&ccc-ddd]
cron: 20 9 */7 * *
new Env('koyeb-自动登陆');
"""
import json
import requests
import os, random
import time, datetime
try:
    from sendNotify import send
except:
    def send(*args):
        print("Không tìm thấy tệp thông báo sendNotify.py không bật thông báo！")

List = []
session = requests.Session()


# 内置Python环境变量[纯Python环境可启用]
#os.environ['KOY_EB'] = "aaa-bbb"

def get_time_stamp(result):
    utct_date = datetime.datetime.strptime(result, "%Y-%m-%dT%H:%M:%S.%f%z")
    local_date = utct_date + datetime.timedelta(hours=8)
    local_date_srt = datetime.datetime.strftime(local_date, "%Y-%m-%d %H:%M:%S")
    return local_date_srt

def auto_living(token):
    # 获取账户应用信息
    list_url = 'https://app.koyeb.com/v1/apps?limit=100'
    list_head = {
        'authorization': f'Bearer {token}',
        'cookie': f'accessToken={token}',
        'content-type': 'application/json',
        'referer': 'https://app.koyeb.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
    }
    res_list = session.get(list_url, headers=list_head)
    if res_list.status_code == 200:
        list_date = res_list.json()
        if len(list_date.get("apps")) > 0:
            for i in range(len(list_date.get("apps"))):
                stop_url = f"https://app.koyeb.com/v1/apps/{list_date.get('apps')[i]['id']}/pause"  # 暂停api
                run_url = f"https://app.koyeb.com/v1/apps/{list_date.get('apps')[i]['id']}/resume"  # 启动api
                ac_head = {
                    'authorization': f'Bearer {token}',
                    'content-type': 'application/json',
                    'origin': 'https://app.koyeb.com',
                    'referer': f"https://app.koyeb.com/apps/{list_date.get('apps')[i]['id']}/settings/danger-zone",
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
                }
                if list_date.get('apps')[i]['status'].lower() == "healthy":
                    List.append(f"{list_date.get('apps')[i]['name']} Ứng dụng chạy tốt！！！")
                elif list_date.get('apps')[i]['status'].lower() == "paused":
                    List.append(f"{list_date.get('apps')[i]['name']} Ứng dụng bị tạm dừng！！！")
                    res_run = session.post(run_url, headers=ac_head)
                    if res_run.status_code == 200:
                        List.append(f"Lệnh khởi động đã được gửi và ứng dụng sẽ trở lại bình thường sau 3 phút！！！")
                    else:
                        List.append(f"Lỗi gửi lệnh khởi động, vui lòng kiểm tra url！！！")
                elif list_date.get('apps')[i]['status'].lower() == "resuming":
                    List.append(f"{list_date.get('apps')[i]['name']} Ứng dụng đang bắt đầu！！！")
                else:
                    List.append(f"{list_date.get('apps')[i]['name']} Lỗi chạy ứng dụng！！！")
                    res_stop = session.post(stop_url, headers=ac_head)
                    if res_stop.status_code == 200:
                        List.append(f"Lệnh tạm dừng đã được gửi. Đợi 1 phút trước khi gửi lệnh bắt đầu.")
                    else:
                        List.append(f"Lỗi gửi lệnh tạm dừng, vui lòng kiểm tra url！！！")
                    time.sleep(60)
                    res_run = session.post(run_url, headers=ac_head)
                    if res_run.status_code == 200:
                        List.append(f"Lệnh khởi động đã được gửi và ứng dụng sẽ trở lại bình thường sau 3 phút！！！")
                    else:
                        List.append(f"Lỗi gửi lệnh khởi động, vui lòng kiểm tra url！！！")
        else:
            List.append(f"Không có ứng dụng phiên bản nào được tạo cho tài khoản hiện tại！！！")
    else:
        List.append(f"Đã xảy ra lỗi khi lấy thông tin ứng dụng tài khoản, vui lòng kiểm tra url！！！")
        print(res_list.text)

def login(usr, pwd):
    login_url = 'https://app.koyeb.com/v1/account/login'
    headers = {
        'origin': 'https://app.koyeb.com',
        'referer': 'https://app.koyeb.com/auth/signin',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'
    }
    data = {
        'email': usr,
        'password': pwd
    }
    res = session.post(login_url, headers=headers, data=json.dumps(data))
    if res.status_code == 200:
        status = res.json()
        token = status.get('token').get('id')
        check_url = 'https://app.koyeb.com/v1/account/profile'
        check_head = {
            'authorization': f'Bearer {token}',
            'referer': 'https://app.koyeb.com/auth/signin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'

        }
        resp = session.get(check_url, headers=check_head)
        if resp.status_code == 200:
            info = resp.json()
            List.append(f"Tài khoản`{info.get('user').get('name')}`Đăng nhập thành công")
            List.append(f"ID：{info.get('user').get('id')}")
            List.append(f"Ngày đăng ký：{get_time_stamp(info.get('user').get('created_at'))}")
            lastlogin_url = 'https://app.koyeb.com/v1/activities?offset=0&limit=20'
            lastlogin_head = {
                'authorization': f'Bearer {token}',
                'referer': 'https://app.koyeb.com/activity',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; PBEM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.52 Mobile Safari/537.36'

            }
            time.sleep(7)
            resg = session.get(lastlogin_url, headers=lastlogin_head)
            if resg.status_code == 200:
                lastlogin = resg.json()
                j = 0
                for i in range(len(lastlogin.get('activities'))):
                    if lastlogin.get('activities')[i].get('object').get('name') == "console" and j < 2:
                        if lastlogin.get('count') is not None and lastlogin.get('count') > 1 and j == 1:
                            List.append(f"Ngày đăng nhập cuối cùng：{get_time_stamp(lastlogin.get('activities')[i].get('created_at'))}")
                        else:
                            List.append(f"Ngày đăng nhập hiện tại：{get_time_stamp(lastlogin.get('activities')[i].get('created_at'))}")
                        j += 1
            else:
                print(resg.text)
        else:
            print(resp.text)
        # 自动保活应用
        auto_living(token)
    else:
        List.append('Đăng nhập tài khoản không thành công: sai tài khoản hoặc mật khẩu')
        List.append(res.text)


if __name__ == '__main__':
    delay_sec = random.randint(1,50)
    List.append(f'Độ trễ ngẫu nhiên{delay_sec}s')
    time.sleep(delay_sec)
    i = 0
    if 'KOY_EB' in os.environ:
        users = os.environ['KOY_EB'].split('&')
        for x in users:
            i += 1
            name, pwd = x.split('-')
            List.append(f'===> [Tài khoản{str(i)}]Start <===')
            login(name, pwd)
            List.append(f'===> [Tài khoản{str(i)}]End <===\n')
            time.sleep(1)
        tt = '\n'.join(List)
        print(tt)
        send('koyeb', tt)
    else:
        print('Biến môi trường không được cấu hình')
        send('koyeb', 'Biến môi trường không được cấu hình')
