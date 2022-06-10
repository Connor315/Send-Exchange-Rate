import pickle
import smtplib
import re
from email.mime.text import MIMEText
from email.header import Header
import time
from datetime import datetime, timedelta
import pytz
import requests

url = 'https://www.boc.cn/sourcedb/whpj/index.html'
html = requests.get(url).content.decode('utf8')
current_time = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S %Z%z')
today = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d')
yesterday = (datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai'))-timedelta(days=1)).strftime('%Y-%m-%d')
print("Current Time =", current_time)

def get_currency(dollar_name):
    dollar = html.index('<td>'+dollar_name+'</td>')
    info = html[dollar:dollar + 300]
    result = re.findall('<td>(.*?)</td>', info)

    file = '货币类型: 人民币 换 ' + dollar_name + ':' + '\n' + '外汇价格:' + result[3] + '\n' + '现钞价格: '+ result[4] + '\n'+'银行买入外汇: '+ result[1]+'\n'+'银行买入外钞: '+ result[2] + '\n'+ '时间:' + current_time + '\n'
    return result, file

def send(email_addresses):
    data1 = "过去七天加拿大币汇率：\n"
    data2 = "过去七天新加坡币汇率：\n"
    Canada_lowest = False
    Singapore_lowest = False

    try:
        file1 = open("Canada.pkl", "rb")
        past7days_Canadian = pickle.load(file1)
        print(past7days_Canadian)
        file1.close()
        for x, y in past7days_Canadian.items():
            d = x + ": " + y + "\n"
            data1 += d
        file2 = open("Singapore.pkl", "rb")
        past7days_Singapore = pickle.load(file2)
        print(past7days_Singapore)
        file2.close()
        for x, y in past7days_Singapore.items():
            d = x + ": " + y + "\n"
            data2 += d
    except:
        file1 = open("Canada.pkl", "wb")
        file1.close()
        file2 = open("Singapore.pkl", "wb")
        file2.close()
        data1 += "暂无数据\n"
        data2 += "暂无数据\n"
        past7days_Canadian = {}
        past7days_Singapore = {}

    # get_currency("货币名字") returns the formatted information as a list and a string
    Canada_result, Canada = get_currency("加拿大元")
    Singapore_result, Singapore = get_currency("新加坡元")
    print(Canada)
    print(Singapore)

    if len(past7days_Canadian) < 7:
        past7days_Canadian[today] = Canada_result[3]
    else:
        if Canada_result[3] <= min(list(past7days_Canadian.values())):
            Canada_lowest = True
        past7days_Canadian.pop(yesterday)
        past7days_Canadian[today] = Canada_result[3]
    if len(past7days_Singapore) < 7:
        past7days_Singapore[today] = Singapore_result[3]
    else:
        if Singapore_result[3] <= min(list(past7days_Singapore.values())):
            Singapore_lowest = True
        past7days_Singapore.pop(yesterday)
        past7days_Canadian[today] = Canada_result[3]

    file1 = open("Canada.pkl", "wb")
    pickle.dump(past7days_Canadian, file1)
    file1.close()
    file2 = open("Singapore.pkl", "wb")
    pickle.dump(past7days_Singapore, file2)
    file2.close()

    body = ""
    if Canada_lowest:
        body += "今天加拿大汇率是过去七天最低!\n"
    if Singapore_lowest:
        body += "今天新加坡汇率是过去七天最低!\n"
    body += '您好, \n' + Canada + data1 + '\n' + Singapore + data2 + '\n HPLD机器人'
    print(body)
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header('加币汇率 现汇:'+Canada_result[3]+'新加坡币汇率 现汇:'+Singapore_result[3]+',点击查看更多','utf-8')
    msg['From'] = 'HPLD机器人'
    msg['To'] = '419032123@qq.com'
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"

    try:
        smtpObj = smtplib.SMTP('smtp.office365.com', 587)
    except Exception as e:
        print(e)
        smtpObj = smtplib.SMTP_SSL('smtp.office365.com', 465)

    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login('lhpiven@outlook.com', "520lhp+.")
    for email in email_addresses:
        smtpObj.sendmail('lhpiven@outlook.com', email, msg.as_string())
    smtpObj.quit()


if __name__ == '__main__':
    emails = input("Email Addresses: (split with one space)\n").split()
    send(emails)
