#!/usr/bin/env python3
"""Render the adjacent Lily Blender project and mux its narration/captions.

Requires Blender 4.3+ and FFmpeg with libass. The caption font is bundled.
Only Python's standard library is required by this launcher.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
TIMELINE_FPS = 24
FRAME_COUNT = 1320
DURATION = 55


def executable(value, label):
    resolved = shutil.which(value)
    if resolved:
        return resolved
    candidate = Path(value).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    raise SystemExit(f'{label} was not found: {value}. Supply its full path.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blender', default='blender')
    p.add_argument('--ffmpeg', default='ffmpeg')
    p.add_argument('--width', type=int, default=1280)
    p.add_argument('--height', type=int, default=720)
    p.add_argument('--samples', type=int, default=16,
                   help='Eevee samples per rendered frame (default:16)')
    p.add_argument('--fps', type=int, default=24,
                   help='Final MP4 frame rate; timeline remains24fps')
    p.add_argument('--skip-render', action='store_true')
    p.add_argument('--no-captions', action='store_true')
    p.add_argument('--output', default='Lily_Takes_the_Train_Rerender.mp4')
    a = p.parse_args()
    if min(a.width,a.height,a.samples,a.fps) <= 0:
        p.error('Resolution, samples, and fps must be positive.')
    if a.width % 2 or a.height % 2:
        p.error('Width and height must be even for the MP4 export.')

    blend = HERE/'Lily_Takes_the_Train.blend'
    audio = HERE/'Lily_Narration_55s.wav'
    captions = HERE/'Lily_Word_Highlights.ass'
    for required in [blend,audio] + ([] if a.no_captions else [captions]):
        if not required.is_file():
            raise SystemExit(f'Missing required adjacent file: {required.name}')
    ffmpeg = executable(a.ffmpeg,'FFmpeg')
    work = HERE/'render_work'
    frames = work/'frames'
    frames.mkdir(parents=True,exist_ok=True)
    if not a.skip_render:
        blender = executable(a.blender,'Blender')
        config = {'width':a.width,'height':a.height,'samples':a.samples,
                  'frames':str(frames),'frame_count':FRAME_COUNT,
                  'fps':TIMELINE_FPS}
        driver = work/'render_scene.py'
        driver.write_text('''import bpy,json
from pathlib import Path
C = json.loads('''+repr(json.dumps(config))+''')
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.render.resolution_x = C['width']
s.render.resolution_y = C['height']
s.render.resolution_percentage = 100
s.render.fps = C['fps']
s.render.fps_base = 1
s.frame_start = 1
s.frame_end = C['frame_count']
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.render.use_file_extension = True
s.render.use_persistent_data = True
s.eevee.taa_render_samples = C['samples']
folder = Path(C['frames'])
for frame in range(1,C['frame_count']+1):
    target = folder / ('frame_%04d.png' % frame)
    if target.exists():
        continue
    s.frame_set(frame)
    s.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    print('LILY_RENDER',frame,'/',C['frame_count'],flush=True)
''',encoding='utf-8')
        subprocess.run([blender,'--background',str(blend),'--disable-autoexec',
                        '--python',str(driver)],check=True,cwd=HERE)

    missing = [i for i in range(1,FRAME_COUNT+1)
               if not (frames/f'frame_{i:04d}.png').is_file()]
    if missing:
        raise SystemExit(f'{len(missing)} rendered frames are missing; first missing frame is {missing[0]}. Run without --skip-render.')
    # Run FFmpeg from the package directory, so the ASS path is portable and
    # avoids platform-specific escaping of absolute drive letters or spaces.
    filters = [f'scale={a.width}:{a.height}:flags=lanczos']
    if not a.no_captions:
        filters.append('ass=Lily_Word_Highlights.ass:fontsdir=Fonts')
    filters.append(f'fps={a.fps}')
    output = Path(a.output).expanduser()
    if not output.is_absolute():
        output = HERE/output
    cmd = [ffmpeg,'-y','-framerate',str(TIMELINE_FPS),'-start_number','1',
           '-i',str(frames/'frame_%04d.png'),'-i',str(audio),
           '-vf',','.join(filters),'-map','0:v:0','-map','1:a:0',
           '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
           '-c:a','aac','-b:a','192k','-t',str(DURATION),
           '-movflags','+faststart',str(output)]
    subprocess.run(cmd,check=True,cwd=HERE)
    print(f'Finished: {output}')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f'External program failed with exit code {exc.returncode}.',file=sys.stderr)
        raise SystemExit(exc.returncode)
