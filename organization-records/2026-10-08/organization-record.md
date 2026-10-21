# 2026-10-08 整理记录

本次做了两件事：时钟之迹终版归档，以及全目录去编号前缀改名。

## 一、时钟之迹终版归入

- 桌面 `时钟之迹.pptx`（409,779 字节，2026-10-08 01:21，SHA-256 前缀 e4a795d9…，全文件夹中最新）以**原名**移入 `课程作业/时钟之迹/时钟之迹.pptx`，作为终版。
- 用 PowerPoint 导出配套 `时钟之迹.pdf`（6 页，518,793 字节）。
- 常用入口两个快捷方式改指终版：`时钟之迹_课堂PPT.lnk` → 终版 pptx；`时钟之迹_PDF预览.lnk` → 终版 pdf。

### 归档去向（历史归档/时钟之迹/）

| 原位置（旧名） | 现位置 |
| --- | --- |
| 课程作业/时钟之迹/时钟之迹_课堂展示_修订版.pptx、.pdf | 历史归档/时钟之迹/课堂展示修订版/ |
| 课程作业/时钟之迹/时钟之迹.pptx（10-08 00:45 中间版） | 历史归档/时钟之迹/真实截图优化/时钟之迹_中间版_1008_0045.pptx |
| 课程作业/时钟之迹/真实截图优化/ 下 5 个中间稿与交付包（时钟之迹.pptx 422KB、六页学术讲解版.pptx/.pdf、六页真实截图优化版.pdf、真实截图与索引.zip） | 历史归档/时钟之迹/真实截图优化/ |
| 同目录 .build/（119MB：脚本、过程截图、日志、重复 RM0090.pdf 等） | 历史归档/时钟之迹/真实截图优化/构建中间文件_build/ |

`课程作业/时钟之迹/真实截图优化/` 保留 `真实截图/` 与 `截图索引.txt`（终版截图底稿，仍被引用）。

## 二、目录去编号前缀

顶层及各级共 47 个目录去掉 `数字_` 前缀：`00_常用入口`→`常用入口`、`01_课程资料`→`课程资料`、`02_课程作业`→`课程作业`、`03_学习笔记`→`学习笔记`、`04_工程实践`→`工程实践`、`07_软件工具`→`软件工具`、`90_历史归档`→`历史归档`、`99_整理记录`→`整理记录`，子目录同理（教师课件、工程例程、安装包等）。历史归档内的日期前缀版本目录一并去前缀（如 `20261007_真实截图优化`→`真实截图优化`，日期以本记录为准）。

保留不改：

- `整理记录/2026-10-06/修改前/` 内旧结构快照（历史记录，改名会失真）；
- 教师例程自带编号名（如 `5-STM32时钟系统`、`7-SysTick系统定时器`）；
- `作业1_2026-09-19`（日期为作业信息本身）；
- 构建产物中的纯数字目录。

## 三、引用修正

- 常用入口全部 8 个快捷方式按新路径重指，逐一验证目标存在。
- 补记：桌面本身的 `STM32CubeMX 6.18.1.lnk` 当日漏改（仍指 `07_软件工具`），用户发现打不开后已修（Target/Args/WorkDir/Icon 四处），自带 JRE 冒烟测试正常。
- 根 README、各子目录 README、课件引用映射表、学习笔记等 20 个活跃文档中的旧路径已替换；整理记录与历史归档此前审校记录中的历史文档保持原样。
- 顺带修复 `课程资料/教师课件/课件引用映射表.md` 中 6 个被截断的 UTF-8 字符（按上下文补为：各个/描述/描述/构建/）/基础）。
- `工程实践/作业2_GPIO工程.lnk`（与常用入口重复）移入 `历史归档/重复资料/作业2_GPIO工程_04目录冗余.lnk`。

未动：`课程作业/作业2/_build`（编译脚本 `编译PDF.ps1` 的活动输出目录）。

## 四、桌面英文教材归档与谷歌云盘备份

桌面 6 个书稿文件（原文件名末尾带多余空格）经 PDF 元数据与内文核对版次后改名，移入 `课程资料/参考书/`，并原样复制到谷歌云盘 `G:\我的云端硬盘\嵌入式\课程资料\参考书\`（云端新建目录，Google Drive 桌面客户端自动上传）。

| 原位置（桌面） | 现名（本地与云端同名） | 字节 | SHA-256 前缀 |
| --- | --- | --- | --- |
| The Art of Electronics .pdf | The Art of Electronics（第2版）.pdf | 28,838,709 | 391908a6401f… |
| Microelectronic Circuits .pdf | Microelectronic Circuits（第8版）.pdf | 62,776,110 | a4404cb4fdf8… |
| Microelectronic Circuits .epub | Microelectronic Circuits（第8版）.epub | 78,794,295 | 4c3c30752d47… |
| Foundations of Analog and Digital Electronic Circuits .pdf | Foundations of Analog and Digital Electronic Circuits.pdf | 8,502,702 | b6c4a90e0813… |
| Analysis and Design of Analog Integrated Circuits .pdf | Analysis and Design of Analog Integrated Circuits（第6版）.pdf | 34,912,843 | 3e30a49f1152… |
| Digital Design and Computer Architecture RISC.pdf | Digital Design and Computer Architecture（RISC-V版）.pdf | 26,098,092 | 8ddfdd0ed24c… |

版次核对依据：

- Gray/Hurst/Lewis/Meyer：PDF 元数据 "Analysis and Design of Analog Integrated Circuits, 6th Edition"（Stephen H Lewis），975 页，即 2024 年 Wiley 第 6 版。
- Sedra 等：EPUB 内文两处 "Eighth Edition"；PDF 1757 页。
- Agarwal & Lang、Harris & Harris RISC-V：各仅此一版。
- **The Art of Electronics 为第 2 版**（首页 "The Art Of Electronics - 2nd Edition"，Horowitz & Hill，1041 页），并非书单所求第 3 版，文件名已如实标注。

另：云端 `我的云端硬盘/嵌入式/` 仍为本日第二节"去编号前缀"之前的旧结构（01_课件、02_课程作业 等），本次仅新增 `课程资料/参考书/` 放入上述文件，未改动云端旧目录；云端如需同步新版目录结构，另行整理。桌面已无残留书稿文件。
