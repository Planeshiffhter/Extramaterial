"""Build actual CPU-only Blender lookdev scenes for the reference revision."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'assets'),str(ROOT/'environments'),str(ROOT/'kitchen'),str(ROOT)]
from character_v2 import append_lily
from wardrobe import add_reference_wardrobe
from lookdev_style import style_actor,relax_actor,home_lighting,camera,cpu_cycles
from build_environment import build_environment
from build_props import make_props
from build_railway import build_station,CAMERAS

def move_to(objects,col):
    for o in objects:
        for old in list(o.users_collection):old.objects.unlink(o)
        col.objects.link(o)

def drive(key,root,prop):
    fc=key.driver_add('value');d=fc.driver;d.type='SCRIPTED'
    var=d.variables.new();var.name='v';var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["'+prop+'"]';d.expression='v'

def face_controls(actor):
    root=actor['root'];f=actor['facial']
    for name,val in [('jaw_open',0),('mouth_round',0),('smile',.10),('blink',0)]:
        root[name]=float(val);root.id_properties_ui(name).update(min=0.0,max=1.0,soft_min=0.0,soft_max=1.0)
    for key,prop in [('jaw','jaw_open'),('round','mouth_round'),('smile','smile'),('blink_L','blink'),('blink_R','blink'),('blink_lower_L','blink'),('blink_lower_R','blink')]:
        if key in f:drive(f[key],root,prop)
    for key in f.get('lower_oral',[]):drive(key,root,'jaw_open')

def scene_world(s,name,strength=.32):
    w=bpy.data.worlds.new(name);w.use_nodes=True;b=w.node_tree.nodes['Background']
    b.inputs[0].default_value=(.55,.68,.85,1);b.inputs[1].default_value=strength;s.world=w

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    home=bpy.context.scene;home.name='01 Home — Reference Lookdev'
    actor=append_lily(home,facial=True)
    garments=add_reference_wardrobe(actor['mesh'],actor['rig'])
    style_actor(actor);relax_actor(actor);face_controls(actor)
    actorcol=bpy.data.collections.new('Lily V2 — Adult Character');home.collection.children.link(actorcol)
    move_to(list(home.objects),actorcol)
    build_environment()
    before=set(home.objects);props=make_props()
    propcol=bpy.data.collections.new('Home — Travel Props');home.collection.children.link(propcol);move_to(set(home.objects)-before,propcol)
    # Bring the canvas bag within normal arm reach and reference-like framing.
    for name,o in props.items():
        if name!='clock':o.location.x-=.68
    for o in home.objects:
        if o.name.startswith(('Env_travel table','Env_table apron')):o.location.x-=.68
        if o.type=='FONT' and o.name=='Bag label':o.hide_render=True
    props['clock'].location=(.55,1.92,2.17)
    home_lighting(home)
    camera(home,'Home hero',(.35,-3.28,1.55),(.35,0,1.22),56,focus=(0,-.105,1.55),fstop=3.0)
    cpu_cycles(home,32,960,540)
    home['purpose']='CPU reference-matching preview. No GPU connected or selected.'
    home['reference_targets']='Adult oval face; loose dark brown shoulder-length waves; sage crewneck; warm window light; waist-up staging.'
    home['preview_output']='home_hero.exr'

    station=bpy.data.scenes.new('02 Station — Reference Lookdev');bpy.context.window.scene=station
    station.collection.children.link(actorcol)
    build_station();scene_world(station,'Station daylight',.32)
    # Real transmissive window glass for Cycles, rather than Eevee alpha glass.
    for m in bpy.data.materials:
        if not m.name.startswith('Rail_') or not m.use_nodes:continue
        p=m.node_tree.nodes.get('Principled BSDF')
        if p and p.inputs['Alpha'].default_value<.99:
            p.inputs['Alpha'].default_value=1;p.inputs['Transmission Weight'].default_value=.96
            p.inputs['Roughness'].default_value=.065;p.inputs['Metallic'].default_value=0;p.inputs['IOR'].default_value=1.45
    camera(station,'Station hero',(.35,-3.65,1.58),(.35,.05,1.25),56,focus=(0,-.105,1.55),fstop=4.0)
    cpu_cycles(station,32,960,540);station['preview_output']='station_hero.exr'

    interior=bpy.data.scenes.new('03 Train Interior — Environment Lookdev');bpy.context.window.scene=interior
    interior.collection.children.link(bpy.data.collections['Rail_Set']);scene_world(interior,'Train daylight',.32)
    c=CAMERAS['train_interior'];camera(interior,'Train interior',c['location'],c['target'],c['lens'],focus=c['target'],fstop=5.6)
    cpu_cycles(interior,32,960,540);interior['preview_output']='train_interior.exr'

    exterior=bpy.data.scenes.new('04 Station Exterior — Environment Lookdev');bpy.context.window.scene=exterior
    exterior.collection.children.link(bpy.data.collections['Rail_Set']);scene_world(exterior,'Exterior daylight',.32)
    c=CAMERAS['exterior_wide'];camera(exterior,'Station exterior',c['location'],c['target'],c['lens'])
    cpu_cycles(exterior,24,960,540);exterior['preview_output']='station_exterior.exr'

    bpy.context.window.scene=home;home.frame_set(1)
    for s in [home,station,interior,exterior]:s.frame_start=1;s.frame_end=1320;s.render.fps=24
    text=bpy.data.texts.new('V2 PRE-GPU LOOKDEV README')
    text.write('CPU-only look development. Four scenes: adult character at home; railway platform; train interior; station exterior.\n')
    text.write('Reference film supplied by user. Base adult woman: Grab3D Casual Woman, CC0, https://grab3d.com/models/characters/woman/.\n')
    text.write('Custom new mouth cavity, teeth/tongue, eyelids, controlled facial shapes; new sage sweater and fitted jeans; original railway environment.\n')
    text.write('Facial preview controls are custom properties on Lily_Actor: jaw_open, mouth_round, smile, blink.\n')
    text.write('This is a reviewable lookdev prototype, not a completed revised55-second movie. GPU has not been connected or used.\n')
    bpy.ops.file.pack_all()
    path=ROOT/'Lily_V2_CPU_Lookdev.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    print('V2_LOOKDEV_READY',path,'scenes',[(s.name,len(s.objects)) for s in bpy.data.scenes],flush=True)

if __name__=='__main__':build()
