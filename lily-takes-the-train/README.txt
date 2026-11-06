LILY TAKES THE TRAIN
55-second English-learning animation

Open Lily_Takes_the_Train.mp4 to watch the finished video. Open Lily_Takes_the_Train.blend in Blender 4.3 or newer to edit
the scene, cameras, character performance, props, and lighting.

VIEWING EXPORT

The viewing MP4 is 1280x720 at 24 fps. The CPU-rendered frames use motion
interpolation for smoother playback. The editable Blender timeline contains
the full 24 fps performance; the supplied rerender script renders it natively.

PROJECT

The Blender timeline is 55 seconds: frames 1-1320 at 24 frames per second.
It contains all 12 supplied dialogue lines. Their original five-second labels
were adjusted so the final "All right. I am ready. Let's go!" fits within the
requested 55-second running time.

The narration WAV is packed into the Blender project. A separate copy,
Lily_Narration_55s.wav, is supplied for convenient audio export and mixing.
Lily_Captions.srt contains the complete captions. Lily_Word_Highlights.ass
adds the rounded dark caption panel and orange spoken-word highlighting.
The viewing MP4 includes the caption treatment; captions can also be replaced
or switched off when exporting a new version.

Lily is an adaptation of the Blender Studio Ellie character and pose-library
demo. The adaptation changes the hair and clothing colors, hides selected
accessories, and adds this story's dialogue performance and gestures. The
home environment, props, camera sequence, and animation assembly were made
for this video. Facial movement combines the character's supplied poses with
timing derived from the narration; it is a stylized performance.

The video was built and rendered with Blender. No external video-generation
plugin was used. The local Blender MCP bridge was used to control Blender;
it is not required to open or render this saved project.

RERENDER WITH BLENDER AND FFMPEG

Install Blender 4.3 or newer, FFmpeg with libass support, and Python 3. The
Noto Sans Bold font is bundled in Fonts under the SIL Open Font License.
Keep Fonts, the .blend, WAV, ASS, and render_video.py together.

From a terminal in this folder:

    python render_video.py

This renders every timeline frame at 1280x720 and 24 fps, then adds the
narration and highlighted captions. Rendering all 1320 frames can take
substantial time, depending on your computer.

To choose installed program paths or a smaller render:

    python render_video.py --blender "/path/to/blender" --ffmpeg "/path/to/ffmpeg" --width 960 --height 540 --samples 16

To export a 30 fps MP4 from the same 24 fps animation timeline:

    python render_video.py --fps 30

The --fps option changes the output video's frame rate without changing the
55-second story timing. The saved scene is always rendered at its original
24 fps, using every timeline frame.

If rendering was interrupted, run the same command again to resume missing
frames. If all frames already exist, use --skip-render to repeat only the
audio/caption export. Use --no-captions for a clean viewing copy.

Frames and the temporary Blender render driver are stored in render_work.
The output is Lily_Takes_the_Train_Rerender.mp4 unless --output is supplied.

RENDER FROM THE BLENDER INTERFACE

1. Open Lily_Takes_the_Train.blend. Select the Scene camera view (Numpad 0).
2. In Output Properties, keep frames 1-1320 and 24 fps. Set the output path
   to render_work/frames/frame_ inside this package folder, and choose your
   desired resolution.
3. Select PNG image output, then choose Render > Render Animation.
4. Keep the exported frames in render_work/frames with names
   frame_0001.png through frame_1320.png. Run render_video.py --skip-render
   to combine those frames with the WAV and highlighted captions.

SOURCE AND ATTRIBUTION

Ellie character and pose library by Blender Studio, licensed CC-BY:
https://www.blender.org/download/demo-files/

Blender MCP by Siddharth Ahuja and contributors, MIT license:
https://github.com/ahujasid/blender-mcp

See CREDITS.txt for source details and attribution requirements. Keep the
Ellie credit when sharing the adapted character, project, or rendered film.
