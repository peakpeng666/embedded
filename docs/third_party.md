# 第三方资料

- `lab1/vendor/st/`：STMicroelectronics STM32L496 CMSIS 设备头文件，保留原始 `LICENSE.md`。
- `lab1/vendor/arm/`：Arm CMSIS Core 5.9.0 头文件，保留 Apache-2.0 `LICENSE.txt`。
- 每个已纳入仓库的头文件及许可证的来源、SHA-256 见 `lab1/vendor/sources.json`。

参考资料：

- [ST STM32L496 数据手册](https://www.st.com/resource/en/datasheet/stm32l496ve.pdf)
- [ST STM32L4 CMSIS 设备定义](https://github.com/STMicroelectronics/cmsis-device-l4)
- [Arm CMSIS 5.9.0](https://github.com/ARM-software/CMSIS_5/tree/5.9.0)
- [Keil STM32L4xx 设备包](https://www.keil.arm.com/packs/stm32l4xx_dfp-keil/versions/)
- [原厂 Pandora V2.4 图纸公开镜像](https://github.com/TrekMax/Pandora_STM32L475_Zephyr/tree/main_v3.4/docs/Hardware)

V2.4 原图中的 MCU / 调试器为 STM32L475 / ST-Link；本项目实板为 STM32L496 / CMSIS-DAP，按键与颜色已通过实测核对。仓库 PDF 中的最小系统图和实验电路图由本项目整理绘制。

Keil 设备包、Flash 算法缓存、原厂整板 PDF 和工具链留在本地，不随仓库上传。第三方文件分别适用它们各自保留的许可。
