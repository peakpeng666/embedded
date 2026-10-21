from pathlib import Path
import re

p=Path(__file__).resolve().parents[1]/'svg_output'
for f in p.glob('*.svg'):
    text=f.read_text(encoding='utf-8')
    # Preserve indentation through SVG and DrawingML whitespace handling.
    text=re.sub(r'(<tspan\b[^>]*>)( +)',lambda m:m.group(1)+'\u00a0'*len(m.group(2)),text)
    f.write_text(text,encoding='utf-8')

f=p/'04_pll.svg'
t=f.read_text(encoding='utf-8')
start=t.index('<g id="pll-equation"')
end=t.index('</g>',start)+4
t=t[:start]+'''<g id="pll-equation" data-pptx-bounds="64 180 1152 159">
<text x="94" y="207" font-size="20" text-anchor="middle" fill="#61747B">HSE</text>
<text x="294" y="207" font-size="20" text-anchor="middle" fill="#61747B">M</text>
<text x="523" y="207" font-size="20" text-anchor="middle" fill="#61747B">N</text>
<text x="775" y="207" font-size="20" text-anchor="middle" fill="#61747B">P</text>
<text x="1043" y="207" font-size="20" text-anchor="middle" fill="#167D8D">SYSCLK</text>
<g font-family="Consolas" font-size="68" text-anchor="middle" fill="#132E3B">
<text x="94" y="294">8</text><text x="194" y="294">÷</text><text x="294" y="294">8</text><text x="394" y="294">×</text><text x="523" y="294">336</text><text x="675" y="294">÷</text><text x="775" y="294">2</text><text x="887" y="294">=</text><text x="1043" y="294" fill="#167D8D" font-weight="bold">168</text>
</g><text x="1136" y="294" font-size="28" fill="#167D8D">MHz</text>
<line x1="64" y1="332" x2="1216" y2="332" stroke="#C9D5D2"/></g>'''+t[end:]
f.write_text(t,encoding='utf-8')

f=p/'08_delay.svg'
t=f.read_text(encoding='utf-8')
start=t.index('<text x="86" y="254"')
end=t.index('</g>',start)
t=t[:start]+'''<text x="86" y="251" font-family="Consolas" font-size="20" fill="#F5F6F2"><tspan x="86" dy="0"><tspan fill="#73D5D4">void</tspan> Delay(__IO uint32_t nTime)</tspan><tspan x="86" dy="25">{</tspan><tspan x="86" dy="25">  uwTimingDelay = nTime;</tspan><tspan x="86" dy="25">  <tspan fill="#73D5D4">while</tspan>(uwTimingDelay != 0);</tspan><tspan x="86" dy="25">}</tspan><tspan x="86" dy="35"><tspan fill="#73D5D4">void</tspan> TimingDelay_Decrement(void)</tspan><tspan x="86" dy="25">{</tspan><tspan x="86" dy="25">  <tspan fill="#73D5D4">if</tspan> (uwTimingDelay != 0x00)</tspan><tspan x="86" dy="25">  {</tspan><tspan x="86" dy="25">    uwTimingDelay--;</tspan><tspan x="86" dy="25">  }</tspan><tspan x="86" dy="25">}</tspan></text>'''+t[end:]
f.write_text(t,encoding='utf-8')

f=p/'09_hal_delay.svg'
t=f.read_text(encoding='utf-8')
t=t.replace('__weak void HAL_Delay','<tspan fill="#73D5D4">__weak void</tspan> HAL_Delay')
t=t.replace('uint32_t tickstart','<tspan fill="#73D5D4">uint32_t</tspan> tickstart').replace('uint32_t wait','<tspan fill="#73D5D4">uint32_t</tspan> wait')
t=t.replace('if (wait &lt;','<tspan fill="#73D5D4">if</tspan> (wait &lt;').replace('while((HAL_GetTick()','<tspan fill="#73D5D4">while</tspan>((HAL_GetTick()')
f.write_text(t,encoding='utf-8')
print('Code indentation, syntax emphasis, and PLL alignment updated.')
