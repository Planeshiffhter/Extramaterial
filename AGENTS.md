# Lily video project: execution defaults

Read `lily-takes-the-train-v2/LOCAL_CODEX_HANDOFF.md` before continuing. In an
extracted V2 preview pack, read `LOCAL_CODEX_HANDOFF.md` in the archive root.

- The user has a normal 8 GB RAM laptop and wants to keep its load low. Treat
  Codex Local as a file editor and remote-job controller. Do not automatically
  launch local Blender, rendered viewports, CPU/GPU renders, baking, benchmarks,
  denoising, or background render workers. Use remote compute for heavy work;
  perform local rendering only when the user explicitly requests that mode.
- Review the existing MP4, GIF, PNGs or offline `Gallery.html` in a browser.
  Opening a `.blend` requires Blender and is optional for reviewing progress.
- The active work is V2. Its delivered animation is a 4.5-second prototype.
  The revised 55-second film is unfinished; V1 is a rejected archived attempt.
- At this handoff, no authenticated remote GPU worker is connected. Check
  access and actual Blender CUDA/OptiX device selection before a remote test.
  Existing render helpers force CPU and must be adapted for remote GPU use.
- Preserve float facial controls, packed media, licenses and the V1 archive.
  Keep raw render data separate from denoised output.
- Keep necessary editable files, previews and documentation on GitHub. Never
  commit authentication tokens, credential files, logs, caches or environments.
