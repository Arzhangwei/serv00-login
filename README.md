

account.json:

[  
  { "username": "xxxx", "password": "xxx*xxxxT#xx!xxx", "panelnum": "panel7.serv00.com", "sshIPaddress": "sxx.serv00.com","sshCommand":"sh /usr/home/bankwjj/check_xray.sh" },
  { "username": "xxxx", "password": "xxxxxxxx", "panelnum": "panel7.serv00.com", "sshIPaddress": "sxx.serv00.com","sshCommand":"sh /usr/home/sunwei/check_xray.sh" }
]

check_xray.sh:
check_and_run_xray() {
    if ! pgrep -x "xray" > /dev/null
    then
        echo "$(date): xray进程不存在，重新启动..."
        nohup ./xray -c config.json >/dev/null 2>&1 &
    else
        echo "$(date): xray进程正在运行。"
    fi
}

libaba

serv00面板设置cron作业，GitHub 登录延期以及补充登录ssh并检查xray。




