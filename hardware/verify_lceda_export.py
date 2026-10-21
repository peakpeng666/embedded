#!/usr/bin/env python3
"""Check LCEDA's exported connectivity against independently reviewed facts.

Checks the EDA application's netlist, not the generator's planned wire list.
Unknown physical pin numbering is intentionally left as functional port names.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
EDA=ROOT/'hardware/lceda'
native=EDA/'Pandora_L496_原理图与流程图.json'
netfile=EDA/'Pandora_L496_嘉立创导出.net'
project=json.loads(native.read_text(encoding='utf-8'))
nettext=netfile.read_text(encoding='utf-8-sig')
nets={}
for match in re.finditer(r'^\(\s*\n(.*?)^\)',nettext,re.M|re.S):
    lines=[line.strip() for line in match.group(1).splitlines() if line.strip()]
    nets[lines[0]]=set(lines[1:])
components={}
for match in re.finditer(r'^\[\s*\n(.*?)^\]',nettext,re.M|re.S):
    lines=[line.strip() for line in match.group(1).splitlines() if line.strip()]
    components[lines[0]]=lines[2]

# Facts read from the vendor's V3.4 drawing, not from layout coordinates.
expected={
 'RESET':{'U3-14','R16-2','RST1-A','C32-1'},
 'VREF+':{'U3-21','R13-2','C28-1','C29-1'},
 'VDDA':{'U3-22','R15-2','R13-1','C30-1','C31-1'},
 'BOOT0':{'U3-94','R14-1'}, 'BOOT1_2':{'BOOT1-2','R14-2'},
 'VCC_3.3M':{'U3-11','U3-28','U3-50','U3-75','U3-100','U3-6','U3-73','R15-1','R17-2','R18-2',
              'C37-1','C38-1','C39-1','C40-1','C41-1'},
 'VCC_5V':{'U4-1','U4-3','C45-1'},
 'VCC_3V3':{'U4-5','C42-1','C43-1','C44-1','R17-1','R18-1','R16-1','BOOT1-1','R45-1','R42-1','RGB1-A'},
 'GND':{'U4-2','C45-2','C42-2','C43-2','C44-2','C37-2','C38-2','C39-2','C40-2','C41-2',
         'C30-2','C31-2','C28-2','C29-2','C32-2','RST1-B','BOOT1-3','KEY0-B','KEY1-B',
         'C33-2','C34-2','C35-2','C36-2','Y3-2','Y3-4','U3-10','U3-27','U3-49','U3-74','U3-99','U3-19','U3-20'},
 'OSC32_IN':{'U3-8','Y2-IN','C33-1'}, 'OSC32_OUT':{'U3-9','Y2-OUT','C34-1'},
 'OSC_IN':{'U3-12','Y3-1','C35-1'}, 'OSC_OUT':{'U3-13','Y3-3','C36-1'},
 'LED_R':{'U3-38','R39-2'},'LED_G':{'U3-39','R41-2'},'LED_B':{'U3-40','R47-2'},
 'RGB1_R':{'RGB1-R','R39-1'},'RGB1_G':{'RGB1-G','R41-1'},'RGB1_B':{'RGB1-B','R47-1'},
 'KEY0':{'U3-57','R45-2','KEY0-A'},'KEY1':{'U3-56','R42-2','KEY1-A'},
 'UART1_TX':{'U3-68','J1-4','J1-1'},'UART1_RX':{'U3-69','J1-3','J1-2'},
 'T_JTMS':{'U3-72'},'T_JTCK':{'U3-76'},
}
assert nets==expected, {'missing':{k:sorted(v-nets.get(k,set())) for k,v in expected.items() if v!=nets.get(k)},
                       'unexpected':{k:sorted(v-expected.get(k,set())) for k,v in nets.items() if v!=expected.get(k)}}
values={'R13':'10R','R15':'10R','R17':'0R','R18':'0R','R14':'10k','R16':'10k',
        'R39':'1k','R41':'1k','R47':'1k','R42':'10k','R45':'10k',
        'C28':'100nF (104)','C29':'2.2uF (225)','C30':'100nF (104)','C31':'10uF',
        'C32':'100nF (104)','C33':'6pF','C34':'6pF','C35':'22pF','C36':'22pF',
        **{f'C{n}':'100nF (104)' for n in range(37,42)},
        'C42':'1uF','C43':'100nF (104)','C44':'220uF/10V','C45':'1uF','U3':'STM32L496VET6','U4':'RT9013-3.3',
        'Y2':'32.768kHz','Y3':'8MHz','BOOT1':'1x3 选择','J1':'USART1 跳线',
        'KEY0':'按下接通','KEY1':'按下接通','RST1':'按下接通','RGB1':'共阳 / A-R-G-B 功能端'}
assert components==values, (components,values)
symbols=[]
for sheet in project['schematics']:
    for shape in sheet['dataStr']['shape']:
        if shape.startswith('LIB~'):
            chunks=shape.split('#@$')
            ref=next(c.split('~')[12] for c in chunks[1:] if c.startswith('T~P~'))
            symbols.append((ref,chunks))
mcu=next(c for r,c in symbols if r=='U3')
pinmap={int(c.split('^^')[0].split('~')[3]):c.split('^^')[3].split('~')[4] for c in mcu if c.startswith('P~')}
stxml=ROOT/'hardware/sources/STM32L496VETx_ST_CubeMX_pins.xml'
ns={'m':'http://mcd.rou.st.com/modules.php?name=mcu'}
stpins={int(p.attrib['Position']):p.attrib['Name'] for p in ET.parse(stxml).findall('m:Pin',ns)}
assert pinmap==stpins and len(pinmap)==100
saved=EDA/'Pandora_L496_嘉立创保存.json'
app_project=json.loads(saved.read_text(encoding='utf-8'))
app_mcu=None
for sheet in app_project['schematics']:
    for shape in sheet['dataStr']['shape']:
        if shape.startswith('LIB~'):
            chunks=shape.split('#@$')
            ref=next(c.split('~')[12] for c in chunks[1:] if c.startswith('T~P~'))
            if ref=='U3':app_mcu=chunks
assert app_mcu is not None
app_pins={int(c.split('^^')[0].split('~')[3]):c.split('^^')[3].split('~')[4] for c in app_mcu if c.startswith('P~')}
assert app_pins==stpins and len(app_pins)==100
exported=EDA/'Pandora_L496_嘉立创导出.json'
export_project=json.loads(exported.read_text(encoding='utf-8-sig'))
assert export_project['title']=='Pandora_L496_Verified' and len(export_project['schematics'])==4
export_mcu=None
for sheet in export_project['schematics']:
    for shape in sheet['dataStr']['shape']:
        if shape.startswith('LIB~'):
            chunks=shape.split('#@$')
            ref=next(c.split('~')[12] for c in chunks[1:] if c.startswith('T~P~'))
            if ref=='U3':export_mcu=chunks
assert export_mcu is not None
export_pins={int(c.split('^^')[0].split('~')[3]):c.split('^^')[3].split('~')[4] for c in export_mcu if c.startswith('P~')}
assert export_pins==stpins and len(export_pins)==100
assert not [ref for ref,count in Counter(r for r,_ in symbols).items() if count!=1]
report={'result':'PASS','eda_application':'嘉立创EDA 标准版 6.5.51',
        'checks':{'vendor_reviewed_net_memberships':len(expected),'vendor_reviewed_component_values':len(values),'st_verified_mcu_pin_names_and_numbers':100,
                  'duplicate_component_references':0,'editable_native_sheets':4},
        'scope':'验证摘绘范围的网络和标值；不等于完整实板 ERC/PCB/封装验证。',
        'unresolved':['实物 PCB 丝印版本未读取','BOOT1 短接帽位置未检查','元器件阻容值未在实物上测量',
                      '厂商 V3.4 图 U3 标 L475，按配套官方指南使用 L496','VREF 旁注写 R18，器件标注为 R13 / 10R',
                      'RGB、按键和 Y2 无可核验物理封装序号，采用功能端子'],
        'files_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [native,saved,exported,netfile,stxml]}}
(EDA/'核对结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['checks'],ensure_ascii=False))
