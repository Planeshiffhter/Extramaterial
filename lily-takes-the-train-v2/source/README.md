# Rebuilding the Blender prototype

The packed `.blend` files one folder above are the easiest way to view/edit the work. No add-on, account, MCP server or GPU is needed to open them.

These sources use Blender 4.3 Python APIs. From the parent project folder, run each command in order (one Blender process at a time):

```sh
blender -b --factory-startup --python source/build_lookdev.py
blender -b source/Lily_V2_CPU_Lookdev.blend --python source/refine_lookdev.py
blender -b source/Lily_V2_CPU_Lookdev.blend --python source/add_lookdev_detail.py
blender -b source/Lily_V2_CPU_Lookdev.blend --python source/fix_fringe.py
blender -b source/Lily_V2_CPU_Lookdev.blend --python source/build_motion_test.py
```

This saves newly built projects under `source/`; it does not overwrite the packed review projects above. Geometry, clothes, face, home, railway, cameras and shader sources are included. The base character is CC0 and AI-assisted; see the supplied license and manifest.

For a CPU EXR still, use `blender -b source/Lily_V2_CPU_Lookdev.blend --python source/render_lookdev.py -- home` (or `station_wide`, `interior`, `exterior`). The per-job process isolates unused scenes to limit memory. For the 108-frame test use `blender -b source/Lily_V2_CPU_Motion_Test.blend --python source/render_motion_test.py`. Optional positional frame bounds after `--` let you render in batches, e.g. `-- 1 24`. Output is multilayer EXR with albedo/normal guides; apply your local CPU denoiser and AgX Medium High Contrast for presentation PNGs. On Blender builds with built-in CPU Open Image Denoise, enabling Render Denoise is convenient. The project used a separately installed official Intel OIDN CPU binary because its Blender build lacked built-in support.

After creating denoised `source/motion/frame_0001.png` through `frame_0108.png`, run `python source/assemble_preview.py` with FFmpeg installed. This combines the native24fps frames with the first4.5s of narration and the licensed caption font. It uses scale/subtitle filters and no optical-flow interpolation.

The provided PNG and MP4 files are already denoised. No denoiser binary, external Python environment, reference footage, credentials or GPU service configuration is redistributed.
