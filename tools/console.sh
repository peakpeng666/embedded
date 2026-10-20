#!/usr/bin/env bash
set -euo pipefail

task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
task_python="$task_root/.venv/bin/python"
task_port="/dev/serial/by-id/usb-ATK_ATK-FS-CMSIS-DAP_ATK-03262021-if00"

if [[ ! -x "$task_python" ]]; then
    echo "项目 Python 环境不存在：$task_python" >&2
    exit 1
fi
if [[ ! -e "$task_port" ]]; then
    echo "未找到开发板，请连接板上的 USB_COM 接口。" >&2
    exit 1
fi
if [[ ! -r "$task_port" || ! -w "$task_port" ]]; then
    echo "为本次连接申请串口访问权限；sudo 密码不会保存。"
    sudo /usr/bin/python3 "$task_root/tools/board_access.py"
fi

echo "115200 / 8N1，无流控。实验固件输入 status/help；原演示固件输入 version/help。"
echo "按 Ctrl+] 退出串口终端。"
exec "$task_python" -m serial.tools.miniterm --raw --eol CR "$task_port" 115200
