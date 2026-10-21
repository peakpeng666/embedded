# 本机 Keil 连板开发

2026-10-21 已在本机 Windows 和实板验证。直接打开 `lab1.uvprojx`。

## 日常操作

1. 编辑 `../lab1/src/main.c`、`lab_logic.c`。Keil 与 CubeIDE 使用同一份 C 源码。
2. 按 **F7** 编译，确认输出无错误。
3. 按 **F8** 下载，确认 **Erase Done / Programming Done / Verify OK**。
4. 按 **Ctrl+F5** 进入硬件调试，自动加载匹配的 AXF 并停在 `main`。
5. **F10** 单步、**F5** 继续运行、**Ctrl+F5** 退出调试。
6. MobaXterm 新建 Serial 会话：**COM3 / 115200 / 8 数据位 / 1 停止位 / 无校验 / Flow control=None**。输入 `status` 或 `help` 后按 Enter。

KEY0（PD10）启动七色轮闪，KEY1（PD9）通过 EXTI 停止。录像中还演示了在调试器中写 `lab.mode = 1`，这是修改 RAM；实际按键需在开发板上操作。

## 已保存的配置

| 项目 | 本机设置 |
| --- | --- |
| Keil | MDK 5.35，Arm Compiler 5.06 update 7 build 960 |
| 设备 | STM32L496VETx，Keil.STM32L4xx_DFP 2.5.0 |
| 程序地址 | `0x08010000`，保留前 64 KiB 引导区 |
| 调试器 | CMSIS-DAP，SWD，100 kHz；探针 ATK-03262021 |
| Flash 算法 | STM32L4xx 512 KB Flash |
| 擦写 | Erase Sectors、Program、Verify |
| 调试启动 | Load Application at Startup、Run to main |

`startup_keil.s` 和 `lab1.sct` 是 AC5 对应的启动与链接配置。GNU 构建继续使用原来的 GNU 启动文件和链接脚本。`cmsis_armcc.h` 来自 CMSIS 5.9.0，来源及 SHA-256 已写入 `../lab1/vendor/sources.json`。

首次验证镜像：3344 字节，SHA-256 `0b157cf932fed16121ed43d49ee1a3801099f4d2737385a1399ed5379ef8f76a`。实板完整读回与此镜像匹配；下载前后仅应用的两个 2 KiB 页面变化，引导区与其余 Flash 均保持一致。证据位于 `../logs/windows_before_keil.json`、`../logs/windows_after_keil.json` 和 `../backups/windows_*keil_*.bin`。

`attach_existing.ini` 是可选的纯符号加载命令，当前默认调试启动不使用它。不要同时让 Keil Debug 和 CubeIDE/OpenOCD 占用同一探针。

## CubeIDE 继续使用

工作区：`D:\Peak\Desktop\嵌入式\工程实践\CubeIDE工作区`，项目 `Pandora_Lab1`。按 **Ctrl+B** 使用 CubeIDE 自带 GNU Arm 工具链编译，输出在 `lab1/build/`。

附加调试前，在工程根目录运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\start_cubeide_debug.ps1
```

再打开 **运行 → 调试配置 → GDB Hardware Debugging → CMSIS_DAP_Attach**。连接 `127.0.0.1:3333`，使用 `keil/Objects/lab1_keil.axf`，关闭复位和 Load image，附加到当前已烧录的 Keil 镜像。**F6** 单步、**F8** 继续、**Ctrl+F2** 结束调试；结束后关闭 OpenOCD 窗口再使用 Keil。

这份附加配置的符号必须与板上程序一致。CubeIDE 的 GNU 输出与 Keil 输出不同；更换板上镜像时同步更换调试符号。源码映射保存在 `.launch` 中，移动工程后若提示找不到源，用“定位文件”选择对应的 `main.c`。

## 录像与其它软件

录像：`../../keil-board-demos/Windows-multi-tool-board-demo.mp4`，约 3 分 29 秒，带中文步骤字幕与章节。

| 时间 | 内容 |
| --- | --- |
| 00:00 | Keil 工程、编译与实板下载 |
| 00:54 | Keil 单步与变量 |
| 01:19 | MobaXterm 串口状态查询 |
| 01:48 | CubeIDE 编译与实板调试 |
| 02:29 | CubeMX 引脚与时钟 |
| 02:59 | Proteus LCD 仿真 |

CubeMX 打开 `../cubemx/Pandora_L496.ioc` 核对 PE7/8/9、PD10/9、PA9/10、PA13/14 和 HSI16；此裸机工程由源码配置寄存器，`.ioc` 用作配置参考。工具文件夹中失效的 CubeMX 快捷方式已修复。

Proteus 已运行本机既有 `D:\Embedded\Projects\Proteus_STM32F4_LCD\project.pdsprj`，LCD 计数正常。它是 STM32F401 的软件仿真工程，与当前 L496 实物分别使用不同固件。
