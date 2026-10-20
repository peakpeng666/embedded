# embedded

STM32L4 嵌入式实验项目。当前完成实验 1：两个按键分别采用查询法和外部中断，控制一颗板载 RGB 灯的七色轮闪与灭灯。

实板为潘多拉 STM32L496VET6，使用板载 CMSIS-DAP 和 USB_COM。已通过编译、六组逻辑测试和实板验收；原演示程序的回退也已实际验证。

## 当前操作

| 按键 | 检测方法 | 效果 |
| --- | --- | --- |
| KEY0 / PD10 | 主循环每 5 ms 查询 | 红、绿、蓝、黄、青、紫/品红、白轮闪，每种颜色亮 300 ms、灭 300 ms |
| KEY1 / PD9 | EXTI9 外部中断 | 消抖确认后全部熄灭，保持停止 |
| 释放 KEY1 后重新按 KEY0 | 查询法 | 从红色重新开始 |

两键消抖 20 ms，长按只登记一次。上电时灯灭；按住 KEY1 时 KEY0 不能启动。**中断是 CPU 响应事件的机制，本实验给中断键指定的动作是灭灯。**

用户现有硬件是一颗 RGB，选择先完成单灯验证。本项目演示 RGB 的七种基本点亮组合，不把一个封装算作原题要求的 2～8 颗独立 LED。

## 文件

```text
embedded/
├── lab1/                 # C 源码、启动文件、链接脚本、Makefile、逻辑测试
│   ├── src/
│   ├── tests/
│   └── vendor/           # ST/Arm CMSIS 头文件及原许可证
├── firmware/             # 与实板一致的 BIN、HEX 和镜像校验清单
├── docs/                 # 最小系统图、电路图、操作与验收记录
└── tools/                # 本地连接、串口、观测和固定范围烧录/回退工具
```

- [实验设计与引脚说明](lab1/README.md)
- [最小系统图、电路图和实测结果 PDF](docs/lab1_design.pdf)
- [实板验收记录](docs/validation.md)
- [本地连接与原温湿度演示说明](docs/board_setup.md)
- [固件文件与校验值](firmware/README.md)
- [工具说明](tools/README.md)
- [Windows 接续与完整备份下载](docs/windows.md)

Git 历史只跟踪工程文件；完整资料与回退备份另作为 Release 附件上传。Windows 接续请先看 [Windows 指南](docs/windows.md)，下载 [完整交接包](https://github.com/peakpeng666/embedded/releases/tag/v1.0.0)。

## 编译

需要 GNU Make、主机 GCC，以及 `arm-none-eabi-gcc`。实测 ARM GCC 10.3.1；Makefile 优先使用本地 `.toolchains/arm/usr/bin/`，否则从 PATH 查找。也可以设置 `CROSS_COMPILE` 指向自己的工具链前缀。

```bash
make -C lab1 all test
```

`all` 生成 `lab1/build/lab1.elf`、`lab1.bin`、`lab1.hex`；`test` 在电脑上运行六组 AddressSanitizer / UndefinedBehaviorSanitizer 行为测试。它们不会操作开发板。

镜像验证和串口工具使用项目 Python 环境：

```bash
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
.venv/bin/python lab1/verify_image.py
```

应用链接在 `0x08010000`，保留前 64 KiB 引导区。编译本身不会烧录。仓库中的 `firmware/` 是已实测的固定版本，重新编译不会自动替换它。

第三方头文件保留各自许可证和来源，见 [第三方说明](docs/third_party.md)。
