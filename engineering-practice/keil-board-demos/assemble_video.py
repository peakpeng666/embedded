"""Burn the step captions into actual screen recordings and assemble chapters."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
CLIPS = [
    ('01_keil_download', 'Keil：工程、编译与实板下载'),
    ('02_keil_debug_simple', 'Keil：断点位置、单步与变量'),
    ('03_mobaxterm', 'MobaXterm：COM3 串口通信'),
    ('04_cubeide', 'CubeIDE：GCC 编译与 CMSIS-DAP 调试'),
    ('05_cubemx', 'CubeMX：L496 引脚与时钟配置'),
    ('06_proteus', 'Proteus：F401 LCD 电路仿真'),
]

def run(args):
    return subprocess.run(args, cwd=BASE, check=True, capture_output=True,
                          creationflags=subprocess.CREATE_NO_WINDOW)

def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries',
                      'format=duration', '-of', 'default=nw=1:nk=1', str(path)]).stdout)

def encode(clip):
    name, _ = clip
    output = BASE / (name + '.mp4')
    raw = BASE / (name + '_raw.mp4')
    ass = BASE / (name + '.ass')
    if not output.exists() or output.stat().st_mtime < max(raw.stat().st_mtime, ass.stat().st_mtime):
        run(['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y',
             '-i', raw.name, '-vf', f'ass={ass.name}', '-c:v', 'libx264',
             '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
             '-movflags', '+faststart', output.name])
    print('Captioned:', name, flush=True)
    return duration(output)

def stamp(value, srt=False):
    ms = round(value * 1000)
    sep = ',' if srt else '.'
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{sep}{ms%1000:03}'

with ThreadPoolExecutor(max_workers=2) as pool:
    durations = list(pool.map(encode, CLIPS))

offset = 0.0
metadata = [';FFMETADATA1', 'title=Windows 多软件连板开发演示', 'comment=真实桌面录屏；中文步骤字幕；2026-10-21']
subtitles = []
chapters = []
for (name, title), length in zip(CLIPS, durations):
    metadata += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(offset*1000)}',
                 f'END={round((offset+length)*1000)}', f'title={title}']
    chapters.append({'start': round(offset, 3), 'duration': length, 'title': title, 'file': name + '.mp4'})
    events = json.loads((BASE / (name + '_events.json')).read_text(encoding='utf-8'))['events']
    for i, event in enumerate(events):
        end = events[i+1]['start'] if i+1 < len(events) else length
        subtitles.append(f"{len(subtitles)+1}\n{stamp(offset+event['start'], True)} --> {stamp(offset+min(end,length), True)}\n{event['text']}\n")
    offset += length

(BASE / 'chapters.ffmeta').write_text('\n'.join(metadata)+'\n', encoding='utf-8')
(BASE / 'clips.ffconcat').write_text('ffconcat version 1.0\n' + ''.join(f"file '{name}.mp4'\n" for name,_ in CLIPS), encoding='ascii')
output = BASE / 'Windows多软件连板开发演示.mp4'
run(['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y', '-safe', '0',
     '-f', 'concat', '-i', 'clips.ffconcat', '-i', 'chapters.ffmeta',
     '-map', '0:v:0', '-map_metadata', '1', '-map_chapters', '1', '-c', 'copy',
     '-movflags', '+faststart', output.name])
(BASE / 'Windows多软件连板开发演示.srt').write_text('\n'.join(subtitles), encoding='utf-8-sig')
(BASE / 'chapters.json').write_text(json.dumps({'duration': duration(output), 'chapters': chapters}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'file': str(output), 'duration_seconds': duration(output), 'size_bytes': output.stat().st_size, 'chapters': chapters}, ensure_ascii=False, indent=2), flush=True)
