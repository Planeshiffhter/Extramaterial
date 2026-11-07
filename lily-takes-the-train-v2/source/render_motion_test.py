import bpy,time,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent;folder=root/'motion';folder.mkdir(exist_ok=True)
s=bpy.context.scene;s.cycles.device='CPU'
print('CPU_ONLY_NATIVE_24FPS_TEST',flush=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
first,last=(map(int,args) if len(args)==2 else (s.frame_start,s.frame_end))
for f in range(max(s.frame_start,first),min(last,s.frame_end)+1):
    out=folder/f'frame_{f:04d}.exr'
    if out.exists():continue
    s.frame_set(f);s.render.filepath=str(out);t=time.time()
    bpy.ops.render.render(write_still=True)
    (root/'motion_progress.json').write_text(json.dumps({'done':f,'total':s.frame_end,'device':'CPU','fps':24,'seconds':round(time.time()-t,2)}))
    print('MOTION_FRAME',f,'SECONDS',time.time()-t,flush=True)
