import bpy,json,math
from pathlib import Path
from mathutils import Quaternion,Vector
root=Path(__file__).resolve().parent;s=bpy.data.scenes['01 Home — Reference Lookdev']
for other in list(bpy.data.scenes):
    if other!=s:bpy.data.scenes.remove(other)
bpy.data.orphans_purge(do_recursive=True);bpy.context.window.scene=s
actor=bpy.data.objects['Lily_Actor'];rig=bpy.data.objects['Lily_Body_Rig']
actor.animation_data_clear();rig.animation_data_clear()
poses={'X':(0,0),'A':(.02,0),'B':(.14,0),'C':(.28,.05),'D':(.40,0),'E':(.22,.65),'F':(.14,.9),'G':(.09,.12),'H':(.22,.1)}
last=(0,0)
for cue in json.loads((root/'lipsync/phonemes.json').read_text())['mouthCues']:
    a=round(cue['start']*24)+1;b=max(a,round(cue['end']*24))
    target=poses.get(cue['value'],(0,0))
    for prop,old,new in [('jaw_open',last[0],target[0]),('mouth_round',last[1],target[1])]:
        actor[prop]=old;actor.keyframe_insert(data_path='["'+prop+'"]',frame=max(1,a-1))
        actor[prop]=new;actor.keyframe_insert(data_path='["'+prop+'"]',frame=a)
        actor.keyframe_insert(data_path='["'+prop+'"]',frame=b)
    last=target
for frame,val in [(1,0),(25,0),(27,.15),(29,1),(31,.2),(33,0),(78,0),(80,.15),(82,1),(84,.2),(86,0),(108,0)]:
    actor['blink']=val;actor.keyframe_insert(data_path='["blink"]',frame=frame)
actor['smile']=.1
head=rig.pose.bones['Head'];base=head.rotation_quaternion.copy()
for f in range(1,109):
    t=(f-1)/107;head.rotation_mode='QUATERNION'
    head.rotation_quaternion=base@Quaternion((1,0,0),math.radians(.9)*math.sin(t*math.tau))
    head.keyframe_insert(data_path='rotation_quaternion',frame=f)
s.frame_start=1;s.frame_end=108;s.render.fps=24;s.frame_set(1)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=False
s.cycles.max_bounces=4;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2
s.render.use_simplify=True;s.render.simplify_subdivision_render=1
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=3
s['motion_test']='4.5-second native24fps CPU first-line test, phoneme-timed lips, blink and subtle head movement. No interpolated frames.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(root/'Lily_V2_CPU_Motion_Test.blend'),compress=True)
print('CPU_MOTION_TEST_PREPARED 108 native frames',flush=True)
