# Handoff packaging


### 安全重新打包

`python hardware/package_delivery.py` 保持原交付目录和 ZIP 名称，但仅接受不存在或空的输出目录，且不会覆盖已有 ZIP。旧交付目录非空时会在复制前停止；不要清空旧资料来绕过检查。改用新的输出目录，例如：

```powershell
python hardware/package_delivery.py --output-dir "..\pandora-delivery-new"
```

自定义目录会在旁边生成同名 `.zip`（示例为 `pandora-delivery-new.zip`）；相对路径以当前工作目录为准。中文和空格路径请加引号。`--help` 可查看选项。输入及输出中的符号链接/Windows junction 会被拒绝，避免越界读写。失败留下的部分输出也不要直接复用，应保留检查并选择新目录重试。本脚本不提供并发互斥，不要让多个进程同时使用同一输出位置。
