from pathlib import Path
import re, json, zipfile, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import fitz

project = Path(__file__).resolve().parents[1]
out = project.parent
frames = sorted((project/'validation'/'powerpoint').glob('*.PNG'), key=lambda p: int(re.search(r'\d+', p.stem).group()))
for batch in range(2):
    canvas = Image.new('RGB', (1640, 1456), '#DDE4E2')
    draw = ImageDraw.Draw(canvas)
    for j, frame in enumerate(frames[batch*6:(batch+1)*6]):
        thumb = Image.open(frame).convert('RGB')
        thumb.thumbnail((800, 450))
        x, y = 12+(j%2)*816, 24+(j//2)*480
        canvas.paste(thumb, (x, y))
        draw.text((x+4,y-17), f'{batch*6+j+1:02}', fill='#132E3B')
    canvas.save(project/'validation'/f'contact_{batch+1}.png')

ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(out/'时钟之迹_课堂展示.pptx') as z:
    slides=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
    notes=[n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
    texts=[' '.join(ET.fromstring(z.read(n)).itertext()) for n in slides]
    shape_count=sum(z.read(n).count(b'<p:sp>') for n in slides)
    assert len(slides)==12 and len(notes)==12
    assert not any(n.startswith('ppt/media/') for n in z.namelist()), 'Unexpected raster assets'
doc=fitz.open(out/'时钟之迹_课堂展示.pdf')
assert len(doc)==12
pdf_text='\n'.join(p.get_text() for p in doc)
assert 'HAL_Delay' in pdf_text and 'HAL_GetTick' in pdf_text and 'SysTick' in pdf_text
for i in [3,7,8]:
    doc[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(project/'validation'/f'pdf_page_{i+1:02}.png')

def compact(s): return re.sub(r'\s+', '', s)
checks={
 'HAL_main.c': ['HAL_Init();','SystemClock_Config();','MX_GPIO_Init();','RCC_OscInitStruct.PLL.PLLM = 8;','RCC_OscInitStruct.PLL.PLLN = 336;','RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;','RCC_OscInitStruct.PLL.PLLQ = 4;','HAL_Delay (1000);','HAL_GPIO_TogglePin(GPIOE, LED2_Pin);'],
 'STD_Usermain.c':['RCC_GetClocksFreq(&RCC_Clocks);','SysTick_Config(RCC_Clocks.HCLK_Frequency / 100);','Delay(10);','if(Index%5==0)','GPIO_ToggleBits(GPIOE, LED2_Pin);','uwTimingDelay = nTime;','while(uwTimingDelay != 0);','uwTimingDelay--;'],
 'HAL_driver.c':['return uwTick;','uint32_t tickstart = HAL_GetTick();','uint32_t wait = Delay;','wait += (uint32_t)(uwTickFreq);','while((HAL_GetTick() - tickstart) < wait)','HAL_SYSTICK_Config(SystemCoreClock / (1000U / uwTickFreq))']
}
for name,phrases in checks.items():
    raw=compact((project/'sources'/name).read_text(encoding='utf-8',errors='replace'))
    for phrase in phrases: assert compact(phrase) in raw, (name,phrase)
report={'slides':len(slides),'speaker_notes':len(notes),'editable_shapes':shape_count,'pdf_pages':len(doc),'source_statements_verified':sum(map(len,checks.values())),'source_audit':'passed','render_engine':'Microsoft PowerPoint','contact_sheets':['contact_1.png','contact_2.png']}
(project/'validation'/'delivery_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
