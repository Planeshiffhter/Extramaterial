import bpy,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent;(root/'previews').mkdir(exist_ok=True);args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['home']
jobs={'home':'01 Home — Reference Lookdev','station':'02 Station — Reference Lookdev','station_wide':'02 Station — Reference Lookdev','interior':'03 Train Interior — Environment Lookdev','exterior':'04 Station Exterior — Environment Lookdev'}
for job in args:
    scene=bpy.data.scenes[jobs[job]]
    if len(args)==1:
        # Isolate each lookdev render to release unused scene dependency graphs.
        for other in list(bpy.data.scenes):
            if other!=scene:bpy.data.scenes.remove(other)
        bpy.data.orphans_purge(do_recursive=True)
    bpy.context.window.scene=scene
    if job=='station_wide':
        scene.camera=bpy.data.objects[scene['wide_camera']];scene['preview_output']='station_wide.exr'
        actor=bpy.data.objects.get('Lily_Actor')
        if actor:actor.rotation_euler.z=.68
    scene.cycles.device='CPU';scene.cycles.use_denoising=False
    scene.render.use_simplify=True;scene.render.simplify_subdivision_render=1
    scene.render.filepath=str(root/'previews'/scene['preview_output'])
    print('RENDER_DEVICE_CONFIRMED CPU',job,flush=True)
    t=time.time();bpy.ops.render.render(write_still=True,scene=scene.name);print('CPU_RENDER_SECONDS',job,time.time()-t,flush=True)
