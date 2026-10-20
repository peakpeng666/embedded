# Windows 接续指南

## 取得全部资料

仓库：[peakpeng666/embedded](https://github.com/peakpeng666/embedded)。

完整交接下载位于 [v1.0.0 Release](https://github.com/peakpeng666/embedded/releases/tag/v1.0.0)：

- `embedded-windows.zip`：Windows 接续用工程，含源码、图纸、已测试固件、原固件备份、设备包、历史记录和文件校验清单；不包含无法在 Windows 直接运行的 Linux Python 环境/编译器。
- `embedded-linux-workspace.tar.gz`：清理前整个 Linux 工作目录的完整快照，含 `.git`、`.venv`、`.toolchains`、原固件、全部日志、缓存、临时文件和历史版本。
- `SHA256SUMS.txt`：两个压缩包和清单的 SHA-256。
- `windows-manifest.json`、`linux-manifest.json`：逐项文件清单和校验值。

GitHub 自动生成的 `Source code (zip)` 仅包含 Git 跟踪文件，不含原固件备份；用于接续时请下载上面命名的交接包。

建议先克隆仓库，再把 Windows 交接包解压覆盖到相同的 `embedded` 目录。交接包不带 `.git`，因此会保留克隆的 Git 历史：

```powershell
git clone https://github.com/peakpeng666/embedded.git C:\Projects\embedded
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\embedded-windows.zip" -DestinationPath C:\Projects -Force
cd C:\Projects\embedded
```

解压后先检查交接包：

```powershell
py -3.12 tools\verify_handoff.py
```

## Python 环境

安装 Python 3.12 的 64 位 Windows 版本。重新创建 Windows 虚拟环境，不复用完整 Linux 快照中的 `.venv`：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r tools\requirements-windows.txt
```

命令直接调用虚拟环境里的 Python，无需修改 PowerShell 执行策略或激活脚本。pyOCD 会安装 Windows 对应的 HID 后端依赖。

## 编译

安装 Windows 版 Arm GNU Toolchain，目标选择 `arm-none-eabi`，把它的 `bin` 目录加入 PATH。使用原生 Python 构建，不需要 GNU Make：

```powershell
arm-none-eabi-gcc --version
.\.venv\Scripts\python.exe tools\build_firmware.py
.\.venv\Scripts\python.exe lab1\verify_image.py
```

如果工具链没有加入 PATH，可指定实际目录：

```powershell
.\.venv\Scripts\python.exe tools\build_firmware.py --toolchain-dir "C:\ArmGNU\bin"
```

输出仍在 `lab1/build/`，不会自动覆盖 `firmware/` 中已实测的发布镜像。不同编译器版本可能产生不同二进制校验值；烧录工具不会自动采纳重编译的任意镜像。电脑端带 ASan/UBSan 的 GCC 行为测试可继续在 WSL/Linux 运行：`make -C lab1 test`。

## 串口与后续连接

板上当前固件：KEY0 启动七色轮闪，KEY1 全灭，再按 KEY0 从红色重新开始。重新插入时连接 USB_COM，保留两只 USART1 跳线。

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
.\.venv\Scripts\python.exe tools\console.py
```

可显式选择端口：

```powershell
.\.venv\Scripts\python.exe tools\console.py --port COM5
```

串口参数为 115200/8N1，无流控。输入 `status` 或 `help`；Ctrl+] 退出。

该探针是 CMSIS-DAP v1 HID。pyOCD 使用 Windows HID 后端；Linux 的 `board_access.py`、sudo 和 udev 权限处理不用于 Windows。串口 COM 号以设备管理器和上面的列举结果为准。

## 回退到原 LCD/温湿度演示

Windows 交接包包含 `backups/` 原备份和 `.toolchains/Keil.STM32L4xx_DFP.3.1.0.pack`，路径已经与工具匹配。先关闭串口终端，再执行：

```powershell
.\.venv\Scripts\python.exe tools\lab1_flash.py plan
.\.venv\Scripts\python.exe tools\lab1_flash.py restore
```

`plan` 是离线检查；`restore` 会实际恢复应用区两个页面。原始备份、设备包、芯片身份与固定范围不匹配时，工具停止，不会自动解除保护。恢复只适用于本次这块板。

## 验证边界与来源

跨平台构建脚本已在当前 Linux 主机编译验证，BIN 与实板验收版本一致。Windows 依赖进行了 Windows x64/Python 3.12 的二进制包解析检查；本次没有在 Windows 实机连接开发板，首次 Windows USB/COM 连接仍需当地确认。

PDF 已预生成。Windows 重新生成报告时使用系统宋体和 Arial；没有这些字体时直接阅读 `docs/lab1_design.pdf` 即可。

- [Python Windows 下载](https://www.python.org/downloads/windows/)
- [Arm GNU Toolchain 官方入口](https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain)
- [Arm 官方 Windows 安装说明](https://learn.arm.com/install-guides/gcc/arm-gnu/)
- [pyOCD 安装](https://pyocd.io/docs/installing)
- [pyOCD USB 后端说明](https://pyocd.io/docs/env_vars.html)
