from pathlib import Path
import bpy
from mathutils import Vector
path=str(Path(__file__).resolve().parent/'Lily_V2_CPU_Lookdev.blend')
home=bpy.data.scenes['01 Home — Reference Lookdev']
c=home.camera;c.location=(.20,-2.20,1.50);target=Vector((.20,0,1.37));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
c.data.lens=58;c.data.dof.focus_distance=(Vector((0,-.105,1.55))-c.location).length;c.data.dof.aperture_fstop=4.0
# Smooth color masks keep natural warm hair highlights without abrupt orange bands.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    nt=mat.node_tree;n=nt.nodes;l=nt.links
    for old in list(n):
        if old.type!='MATH':continue
        if old.operation=='LESS_THAN' and abs(old.inputs[1].default_value-.951)<.0001:old.inputs[1].default_value=.928
        if not old.inputs[0].is_linked:continue
        incoming=old.inputs[0].links[0].from_node
        if incoming.type!='SEPARATE_COLOR':continue
        kind=None
        if old.operation=='LESS_THAN' and abs(old.inputs[1].default_value-.48)<.0001:kind='value'
        if old.operation=='GREATER_THAN' and abs(old.inputs[1].default_value-.40)<.0001:kind='saturation'
        if kind is None:continue
        smooth=n.new('ShaderNodeMapRange');smooth.interpolation_type='SMOOTHERSTEP';smooth.clamp=True
        smooth.label='Smooth brown hair '+kind
        if kind=='value':a,b,lo,hi=.20,.75,1,0
        else:a,b,lo,hi=.10,.50,0,1
        for socket,val in [('From Min',a),('From Max',b),('To Min',lo),('To Max',hi)]:smooth.inputs[socket].default_value=val
        l.new(old.inputs[0].links[0].from_socket,smooth.inputs['Value'])
        for link in list(old.outputs[0].links):l.new(smooth.outputs['Result'],link.to_socket)
        old.label='Replaced hard threshold'
# Counter-height travel island and a tote beside the narrator, as in the reference.
for o in home.objects:
    if o.name in {'PROP_Phone','PROP_Wallet','PROP_Bottle','PROP_SmallBag'}:o.location.z+=.10
    if o.name=='PROP_SmallBag':o.location.x=.62
    if o.name.startswith('Env_travel table top') or o.name.startswith('Env_table apron'):o.location.z+=.10
    if o.name.startswith('Env_travel table top'):o.dimensions.x=.94
    if o.name.startswith('Env_travel table leg'):o.location.z+=.05;o.dimensions.z+=.10
station=bpy.data.scenes['02 Station — Reference Lookdev'];c=station.camera
c.location=(.25,-2.95,1.57);c.rotation_euler=(Vector((.25,.05,1.30))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=55
c.data.dof.focus_distance=(Vector((0,-.105,1.55))-c.location).length;c.data.dof.aperture_fstop=4.5
bpy.context.window.scene=home
bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
print('V2_LOOKDEV_REFINED',flush=True)
