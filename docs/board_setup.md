# 本地连接与原演示记录

## 连接

开发板型号为 STM32L496VET6，内部 Flash 512 KiB。实测 `DBGMCU_IDCODE=0x20006461`，Cortex-M4，读保护字节为 `0xAA`。

USB 线接板上的 USB_COM。板载探针显示为 ATK-FS-CMSIS-DAP；另一个仅标 USB 的接口属于目标应用 USB。串口跳线保持 PA9(T) ↔ RXD、PA10(R) ↔ TXD。

Ubuntu 本地工具通过 pyOCD / PyUSB 访问 CMSIS-DAP。若重新插线后缺少设备节点访问权限：

```bash
python3 tools/board_access.py --check
sudo python3 tools/board_access.py
```

脚本仅给准确匹配的设备节点增加当前连接周期的访问权限，不修改永久用户组或 udev 配置，也不保存密码。固件和备份的具体操作见 [工具说明](../tools/README.md)。

## 串口

```bash
tools/console.sh
```

115200 / 8N1，无流控。当前实验输入 `status` 或 `help`；按 Ctrl+] 退出。恢复原 RT-Thread 演示后，使用 `version` 或 `help`，提示符为 `msh />`。

曾出现单向串口通信问题。用户断电重新插紧并互换两个 USART1 跳线帽后，`version` 和 `help` 双向通信通过。结果支持跳线连接或接触问题，没有单独认定某一只帽损坏。

## 原演示的温湿度读取

这是恢复原演示后才提供的命令，不属于当前实验固件：

```text
aht10 probe i2c2
aht10 read
```

原程序读取时首次返回 0.0% / -50.0°C，判为无效。随后连续五次有效读数：31.7°C/29.0%、31.6°C/30.4%、31.6°C/30.5%、31.6°C/30.6%、31.6°C/30.8%。基础读取通过，未使用参考仪表校准。

原始 Flash 备份保留在本机 `backups/`，不上传仓库；外部 SPI Flash 和选项字节不包含在该内部 Flash 备份中。回退已实际验证，详见 [验收记录](validation.md)。
