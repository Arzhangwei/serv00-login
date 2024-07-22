import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os
import paramiko
import datetime

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
ss = requests.session()
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN')

async def pushWX(conten):
    result = ss.get(f"https://wxpusher.zjiecode.com/demo/send/custom/{PUSHPLUS_TOKEN}?content={conten}").json()
    if result['code'] == 1000:
        print(f"账号Wxpusher 通知: 推送成功!")
    else:
        print(f"账号Wxpusher 通知: 推送失败!")


#####################函数定义start######################
# 
#ssh链接主机并执行命令，返回结果
#
async def ssh_with_key(hostname, userName, command,passWord):
    try:
        ssh_client = paramiko.SSHClient()
        
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接交换机
        ssh_client.connect(hostname, username=userName, password=passWord)
        #print("登陆成功")
        # 执行 portcfgshow 命令
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()  # 将字节数据解码为字符串
        #print(f"ssh_with_key 返回的是{output}")
        return output 
        
    except Exception as e:
        print(f"ssh_with_key_FUNC An error occurred: {e}")
    finally:
        # 关闭SSH连接
        ssh_client.close()


def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# telegram消息
message = 'serv00&ct8自动化脚本运行\n'

async def login(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)

        await page.type('#id_username', username)
        await page.type('#id_password', password)

        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('无法找到登录按钮')

        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()

async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panelnum']
        sshIPaddress = account['sshIPaddress']

        serviceName = 'ct8' if 'ct8' in panel else 'serv00'
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'{serviceName}账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
            message += success_message + '\n'
            print(success_message)
            await pushWX(success_message)
        else:
            message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)
        
    message += f'所有{serviceName}账号登录完成！'
    
    print(f'所有{serviceName}账号登录完成！')

    stdout_result = await ssh_with_key(sshIPaddress,username,"sh /usr/home/bankwjj/check_xray.sh",password)
    print(stdout_result)
    if 'xray进程正在运行' in stdout_result:
        print('xray进程正在运行')


if __name__ == '__main__':
    asyncio.run(main())