"""Assemble denoised native PNG frames, narration and highlighted captions."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent.parent
out=root/'previews/Lily_V2_CPU_First_Line_Test.mp4'
out.parent.mkdir(exist_ok=True)
assert all((root/'source/motion'/f'frame_{i:04d}.png').is_file() for i in range(1,109)), 'Denoise/export all 108 PNGs into source/motion first.'
subprocess.run([
    'ffmpeg','-v','error','-y','-framerate','24','-i','source/motion/frame_%04d.png',
    '-i','audio/Lily_Narration_55s.wav','-t','4.5',
    '-vf','scale=1280:720:flags=lanczos,ass=filename=captions/Lily_Word_Highlight.ass:fontsdir=captions',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
    '-c:a','aac','-movflags','+faststart',str(out)
],check=True,cwd=root)
print(out)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-vf','fps=12,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',str(root/'previews/Lily_V2_CPU_First_Line_Loop.gif')],check=True)
