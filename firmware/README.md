# 已实测固件

- `lab1.bin`：纯二进制，必须使用明确地址 `0x08010000`。
- `lab1.hex`：含应用地址的 Intel HEX。
- `manifest.json`：向量、大小、地址和 BIN SHA-256。

行为：KEY0 查询启动七色轮闪，KEY1 中断全灭，释放 KEY1 后再按 KEY0 从红色重启。上电时熄灭。

当前 BIN 为 2724 字节，SHA-256：

`231683d50a998b4049ab6d5d939e86cf33b15599c28d222b3fb2cdfc777cec27`

源码重新构建会写入 `lab1/build/`，不会自动更新本目录。烧录工具固定校验这里的镜像。`tools/lab1_flash.py` 是本次实板的局部写入/回退工具，必须具备匹配的本地原始备份和设备包；不会把 BIN 按默认地址写到引导区。

完整实测结果见 [验收记录](../docs/validation.md)。
