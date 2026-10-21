<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 嵌入式系统课程教师与同学
- objective: 沿初始化、设置、获取、应用四阶段讲清实际例程的时钟和延时。
- core_message: 频率决定滴答，滴答决定延时，延时决定动作。

## mode
- mode: custom
- mode_behavior: 四阶段总览后逐段跟踪实际源码，用公式和流程连接配置、读取与LED动作。

## visual_style
- visual_style: custom
- visual_style_behavior: 技术出版网格、明确的信号连线、米白正文和深蓝封面、青绿HAL与橙色标准库对照；代码保留等宽字体，大数字突出计算结果。

## colors
- background: #F5F6F2
- secondary_bg: #E8EEEB
- primary: #132E3B
- accent: #167D8D
- secondary_accent: #D66A35
- body_text: #1D3440
- secondary_text: #61747B
- divider: #C9D5D2
- inverse: #F5F6F2
- inverse_secondary: #AABDBF
- code_accent: #73D5D4

## typography
- font_family: Microsoft YaHei
- title_family: Microsoft YaHei
- body_family: Microsoft YaHei
- code_family: Consolas
- display_family: Consolas
- body: 24
- title: 40
- subtitle: 28
- annotation: 16
- code: 20
- display: 68
- label: 20

## icons
- library: none
- inventory: none

## page_rhythm
- P01: anchor
- P02: breathing
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: breathing
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: anchor

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
- 不要进行防御性说明，避免ai味道 (user)
