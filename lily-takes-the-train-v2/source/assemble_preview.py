"""Assemble denoised native PNG frames, narration and highlighted captions."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent.parent
out=root/'previews/Lily_V2_CPU_First_Line_Test.mp4'
out.parent.mkdir(exist_ok=True)
assert (root/'source/motion/frame_0108.png').is_file(), 'Denoise/export all108 PNGs into source/motion first.'
subprocess.run([
    'ffmpeg','-v','error','-y','-framerate','24','-i','source/motion/frame_%04d.png',
    '-i','audio/Lily_Narration_55s.wav','-t','4.5',
    '-vf','scale=1280:720:flags=lanczos,ass=filename=captions/Lily_Word_Highlight.ass:fontsdir=captions',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
    '-c:a','aac','-movflags','+faststart',str(out)
],check=True,cwd=root)
print(out)
