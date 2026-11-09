# Continue Lily v2 from Codex Local

## Quick start

1. Clone or download this repository and open it in Codex Local.
2. Read `AGENTS.md` and this handoff before asking the new session to continue.
3. Review `Gallery.html`, the MP4 or GIF in your browser. This does not start Blender or a render.
4. Keep expensive Blender work on an authorized remote worker. A browser and code editor are enough for lightweight local review/control.

Suggested first prompt:

> Read AGENTS.md and lily-takes-the-train-v2/LOCAL_CODEX_HANDOFF.md. Continue the Lily V2 project toward the 55-second reference-style video. Keep my 8 GB laptop workload light: do not launch local Blender or rendering. Review the current prototype and source first, then use an authenticated remote worker for heavy work.

The cloud conversation and its attachments do not automatically transfer to a new local chat. For direct visual comparison, attach your original reference video again locally; the public repository contains analysis and project work, not that reference footage.

If your laptop is Windows, note that the official Colab CLI currently supports Linux/macOS. Avoid adding a memory-heavy Linux VM just for this project; Colab's browser interface or the existing Linux cloud workspace can control remote work instead.

## Laptop constraint

The user has a normal **8 GB RAM laptop** and wants to avoid heavy local load.
Use it for browser review, reading/editing files and controlling a remote
worker. **Do not automatically launch Blender, rendered viewports, local
renders, baking, benchmarks, denoising or large development environments.**
Run a heavy local job only if the user explicitly requests it. Moving this
chat to Codex Local does not supply a GPU or make rendering lightweight.

## Goal and current state

Create a **55-second Blender English-learning video** containing all 12 Lily
lines unchanged. Match the supplied reference's general presentation: an adult
woman with loose shoulder-length dark waves, sage knit pullover, full-length
jeans, warm soft light, believable home/station/train locations, restrained
acting and white captions with the current word highlighted orange.

The previous Ellie-based V1 was rejected as a poor match. It is archived and
must not be presented as the revised result. V2 uses an adult source model,
new wardrobe and custom mouth/eyelid controls. **V2 is still a prototype:**
four environment/character studies and a **4.5-second, 108-native-frame test**,
not the completed 55-second film. That test renders at 640×360 and is presented
at 1280×720/24 fps; it is not a native-720p production-quality proof.

The source character has a different identity from the reference. A faster GPU
will not automatically fix character design, expression or physical contact.
Do not promise an exact identity match without the original model. The supplied
reference footage itself is not redistributed in this repository; its concrete
visual targets are recorded in `reference_analysis.md`.

## Repository and easy visual review

Repository: https://github.com/Planeshiffhter/Extramaterial

Work from `lily-takes-the-train-v2/`. Read the repository's current instructions
and status before changing it. The user wants necessary editable/supporting
files retained on GitHub. Preserve the V1 archive and keep credentials, runtime
tokens, caches and render-worker environments out of the repository.

The user does not need to open a `.blend` file to see progress:

- Play `previews/Lily_V2_CPU_First_Line_Test.mp4` or view the silent
  `previews/Lily_V2_CPU_First_Line_Loop.gif` in a browser.
- View `home_hero.png`, `station_wide.png`, `station_exterior.png` and
  `train_interior.png` in `previews/`.
- Open `Gallery.html` locally in a browser. Its relative video/image files are
  in this folder; a downloaded `Lily_V2_CPU_Preview_Pack.zip` also contains the
  offline gallery. This does not launch Blender.
- Do not claim GitHub Pages is live. Enabling it returned **HTTP 403, Resource
  not accessible by integration**. Owner activation is still pending; see
  `WEBSITE_SETUP.md`. Ordinary GitHub file uploads had succeeded.

## Important files

| Path inside `lily-takes-the-train-v2/` | Purpose |
| --- | --- |
| `Lily_V2_CPU_Lookdev.blend` | Packed Blender 4.3+ project: home, station/platform, train interior and station exterior scenes |
| `Lily_V2_CPU_Motion_Test.blend` | Packed first-line motion test, frames 1–108 at 24 fps, with narration packed/trimmed in an audio strip |
| `verification.json` | Existing scene/device, fractional facial-control, packed-media and short-video checks |
| `storyboard.json`, `reference_analysis.md` | Full 12-line/55-second shot plan and look-development targets |
| `audio/Lily_Narration_55s.wav` | Complete 55-second narration, ready to reuse |
| `captions/Lily_Word_Highlight.ass`, `captions/Lily_Captions.srt` | Complete timed captions; Noto font is alongside them |
| `source/README.md` | Rebuild order for portable Blender sources |
| `source/assets/character_v2.py`, `source/assets/casual_woman_compatible.blend` | Custom face setup and reusable adult base asset |
| `source/build_lookdev.py`, `source/wardrobe.py`, `source/environments/build_railway.py` | Scene, new clothing and railway sources |
| `source/build_motion_test.py`, `source/lipsync/phonemes.json` | Rhubarb mouth-cue mapping and motion-test keys |
| `LICENSES/` | Base-character, font and production-tool notices |

The packed projects contain their visual assets and can be opened without a
plugin/MCP server, but **do not open them automatically on this laptop**. The
full story performance, prop interactions, location edit and final film remain
unfinished. A 1320-frame range in the lookdev file is a duration placeholder.

## Remote GPU: not connected yet

No authenticated remote GPU, Colab runtime or GPU render worker has been
established. The official Colab CLI was installed and its local invocation/help
was investigated in the prior cloud workspace only. That does not prove a
remote GPU connection, quota, renderer compatibility or a successful GPU job.
No ready-to-run authenticated Colab worker is currently supplied by the repo.

Use a user-authorized remote GPU resource for expensive work. Authentication
and provider access must be established through the supported sign-in flow;
do not ask for secrets in chat or assume old cloud credentials exist locally.

The current sources deliberately **force CPU rendering**. Adapt these before
attempting any GPU benchmark:

- `source/lookdev_style.py`: `cpu_cycles()` sets `scene.cycles.device='CPU'`;
  `source/build_lookdev.py` calls it for every scene.
- `source/render_lookdev.py` and `source/render_motion_test.py` reset the active
  scene to CPU immediately before rendering.
- `source/build_motion_test.py` saves CPU settings.
- Optional preview/main blocks in `source/fix_fringe.py`,
  `source/environments/build_railway.py` and
  `source/kitchen/build_environment.py` also select CPU.

On the **remote worker**, enumerate Blender's available Cycles devices, choose
supported **CUDA or OptiX** hardware, enable the actual GPU device(s), disable
unintended CPU fallback, and set the render scenes to `GPU` after any helper
that would reset them. Verify the renderer build, selected device name/backend
and available memory. `nvidia-smi` alone is insufficient evidence that Blender
is rendering on the GPU. Stop on an absent/unsupported device instead of
silently benchmarking CPU rendering. Only then run a small authorized remote
test before scheduling the full sequence. Do not do this benchmark locally.

## Preserve the fixes and render data

- Facial root properties on `Lily_Actor` are **floats**: `jaw_open`,
  `mouth_round`, `smile`, `blink`. An earlier integer initialization rounded
  fractional jaw values to zero and produced an invalid silent-mouth diagnostic.
  Keep float creation and `float(value)` assignments in both builders. Existing
  checks show frame 13 jaw ≈0.14 and frame 53 jaw ≈0.28 matching the driven
  shape key; blinks close at frames 29 and 82. Do not use the unreleased integer
  diagnostic as evidence of working motion.
- The motion file packs narration in an audio strip, while
  `scene.render.use_sequencer=False` keeps camera renders from being replaced
  by the audio-only sequencer. Preserve that separation.
- For future remote rendering, keep **raw multilayer EXR**, denoised images and
  exports in separate locations, for example `render/raw_exr/`,
  `render/denoised_png/`, `exports/`. Preserve original beauty/albedo/normal
  passes; never overwrite raw EXRs with a denoised result. Match AgX/Medium High
  Contrast once, and avoid applying the view transform twice.
- Finish and check the full performance before production rendering. Target
  native frames at 24 fps: **1320 frames for 55 seconds**. Avoid the V1
  optical-flow interpolation workaround on hands, hair, eyes and lips.
- Verify complete frame sets and final video/audio duration before packaging.
  Do not infer readiness from the existence of a partially written MP4 or ZIP.

## Rights and production notes

The adult base is [Grab3D Casual Woman](https://grab3d.com/models/characters/woman/),
**CC0 1.0**, with the publisher's explicit **AI-assisted Meshy mesh/texture**
disclosure. Custom clothing, mouth/eyelid geometry and railway work are included.
Keep `LICENSES/Grab3D_CC0.txt`, source notes and font notices. V2 is not the
earlier Ellie/CC-BY character. Rhubarb is MIT; Noto is SIL OFL 1.1; station text
uses DejaVu notices. Narration uses the user's script through `edge-tts`, voice
`en-US-JennyNeural`, rate `-10%`; do not invent a license for the voice/output.

Next: review the existing browser-visible prototype with the user, preserve
their requested look changes, prepare/verify the remote worker, and continue
the full storyboard and native-frame production there. Keep local work light.
