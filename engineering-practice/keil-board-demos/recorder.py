"""Record real desktop actions and export timed Chinese captions."""
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent


class Recorder:
    def __init__(self, name):
        self.name = name
        self.events = []
        self.log = (BASE / f"{name}_capture.log").open("wb")
        self.process = subprocess.Popen([
            shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "warning", "-y",
            "-f", "gdigrab", "-framerate", "15", "-draw_mouse", "1",
            "-video_size", "2560x1600", "-i", "desktop",
            "-vf", "scale=1920:1200,pad=1920:1320:0:0:color=0x111827",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(BASE / f"{name}_raw.mp4"),
        ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=self.log,
            creationflags=subprocess.CREATE_NO_WINDOW)
        self.start = time.monotonic()
        time.sleep(1.0)
        if self.process.poll() is not None:
            raise RuntimeError("Desktop recording failed; inspect capture log")

    def caption(self, text):
        self.events.append({"start": time.monotonic()-self.start, "text": text})
        print(f"{self.name}: {text}", flush=True)

    def stop(self):
        if self.process.poll() is None:
            self.process.communicate(b"q\n", timeout=30)
        self.log.close()
        duration = time.monotonic()-self.start
        def ts(seconds):
            cs = int(seconds*100)
            return f"{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}"
        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1320
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,34,&H00FFFFFF,&H00FFFFFF,&H00111827,&H00111827,0,0,0,0,100,100,0,0,1,1,0,2,55,55,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = [header]
        for i, event in enumerate(self.events):
            end = self.events[i+1]["start"] if i+1 < len(self.events) else duration
            text = event["text"].replace("\n", r"\N")
            lines.append(f"Dialogue: 0,{ts(event['start'])},{ts(end)},Default,,0,0,0,,{text}\n")
        (BASE/f"{self.name}.ass").write_text("".join(lines),encoding="utf-8-sig")
        (BASE/f"{self.name}_events.json").write_text(json.dumps({"recorded_at":datetime.now().astimezone().isoformat(),"duration":duration,"events":self.events},ensure_ascii=False,indent=2),encoding="utf-8")
        if self.process.returncode:
            raise RuntimeError("Recorder did not complete successfully")
        print(f"Saved {self.name}_raw.mp4, {duration:.1f}s",flush=True)
