from pathlib import Path
import bpy,math,random
from mathutils import Vector
path=str(Path(__file__).resolve().parent/'Lily_V2_CPU_Lookdev.blend')
home=bpy.data.scenes['01 Home — Reference Lookdev'];bpy.context.window.scene=home
mesh=bpy.data.objects['Lily_Actor_Mesh']
# Darken the saturated front sweep too; keep bright forehead skin untouched.
for mat in mesh.data.materials:
    if not mat.use_nodes:continue
    n=mat.node_tree.nodes;l=mat.node_tree.links
    p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
    tex=next((x for x in n if x.type=='TEX_IMAGE' and x.image and 'basecolor' in x.image.name),None)
    hair=next((x for x in n if x.label=='Reference dark brown waves'),None)
    if not p or not tex or not hair:continue
    old=p.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],xyz.inputs[0])
    hsv=n.new('ShaderNodeSeparateColor');hsv.mode='HSV';l.new(tex.outputs['Color'],hsv.inputs[0])
    z=n.new('ShaderNodeMapRange');z.interpolation_type='SMOOTHERSTEP';z.inputs['From Min'].default_value=156.8;z.inputs['From Max'].default_value=159.2
    l.new(xyz.outputs['Z'],z.inputs['Value'])
    sat=n.new('ShaderNodeMapRange');sat.interpolation_type='SMOOTHERSTEP';sat.inputs['From Min'].default_value=.48;sat.inputs['From Max'].default_value=.72
    l.new(hsv.outputs[1],sat.inputs['Value'])
    mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(z.outputs['Result'],mask.inputs[0]);l.new(sat.outputs['Result'],mask.inputs[1])
    mix=n.new('ShaderNodeMixRGB');mix.label='Continuous dark front sweep';l.new(mask.outputs[0],mix.inputs[0]);l.new(old,mix.inputs[1]);l.new(hair.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
# Slightly narrower eye apertures give the face the reference's adult read.
if not mesh.get('v2_adult_eye_refinement'):
    for ob in [mesh]+[x for x in bpy.data.objects if x.name.startswith('Lily eyelid') or x.name.startswith('Lily lower eyelid')]:
        if ob.type!='MESH':continue
        mw=ob.matrix_world.copy();inv=mw.inverted()
        blocks=ob.data.shape_keys.key_blocks if ob.data.shape_keys else [None]
        for block in blocks:
            points=block.data if block else ob.data.vertices
            for p in points:
                w=mw@p.co
                if not (1.515<w.z<1.585 and w.y<-.053):continue
                cx=.0388 if w.x>0 else -.0388;dx=w.x-cx;dz=w.z-1.5513
                r=math.sqrt((dx/.033)**2+(dz/.030)**2)
                if r>=1:continue
                fall=(1-r*r)**2;w.x-=dx*.055*fall;w.z-=dz*.12*fall;p.co=inv@w
        ob.data.update()
    mesh['v2_adult_eye_refinement']=True
# Visible, low-contrast knitted yarn detail is carried in albedo as well as bump.
for mat in bpy.data.materials:
    if 'sage' not in mat.name.lower() or 'lily' not in mat.name.lower() or not mat.use_nodes:continue
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    if not p or n.get('Reference knit yarn'):continue
    tc=n.new('ShaderNodeTexCoord');wave=n.new('ShaderNodeTexWave');wave.name='Reference knit yarn';wave.bands_direction='X'
    wave.inputs['Scale'].default_value=165;wave.inputs['Distortion'].default_value=3.5;wave.inputs['Detail Scale'].default_value=1.7
    l.new(tc.outputs['Object'],wave.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');base=tuple(p.inputs['Base Color'].default_value)
    ramp.color_ramp.elements[0].color=tuple(v*.92 for v in base[:3])+(1,)
    ramp.color_ramp.elements[1].color=tuple(min(1,v*1.045) for v in base[:3])+(1,)
    l.new(wave.outputs['Color'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.0008
    l.new(wave.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
# Replace the old oval background treetops with clustered leafy silhouettes.
old=[o for o in home.objects if 'distant treetop' in o.name]
rng=random.Random(412)
leafmats=[]
for i,col in enumerate([(.16,.29,.12),(.24,.37,.15),(.34,.44,.22),(.42,.50,.28)]):
    m=bpy.data.materials.new('Window tree foliage '+str(i));m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;leafmats.append(m)
for tree in old:
    center=tree.location.copy();tree.hide_render=True
    verts=[];faces=[];mi=[]
    for j in range(85):
        theta=rng.uniform(0,math.tau);radius=math.sqrt(rng.random());x=center.x+math.cos(theta)*radius*.24;z=center.z+math.sin(theta)*radius*.34
        r=rng.uniform(.025,.065);base=len(verts)
        verts.extend([(x-r,2.342-rng.uniform(.001,.01),z),(x,2.34,z+r*.8),(x+r,2.342,z),(x,2.338,z-r*.8),(x,2.321,z)])
        faces.extend([(base,base+1,base+4),(base+1,base+2,base+4),(base+2,base+3,base+4),(base+3,base,base+4)]);mi.extend([rng.randrange(4)]*4)
    me=bpy.data.meshes.new('Leaf canopy');me.from_pydata(verts,[],faces)
    for m in leafmats:me.materials.append(m)
    for p,index in zip(me.polygons,mi):p.material_index=index;p.use_smooth=True
    o=bpy.data.objects.new('V2 layered window foliage',me);home.collection.objects.link(o)
# A separate wide railway composition demonstrates the station, platform and train.
station=bpy.data.scenes['02 Station — Reference Lookdev']
data=bpy.data.cameras.new('Station narrative wide');wide=bpy.data.objects.new('Station narrative wide',data);station.collection.objects.link(wide)
wide.location=(4.8,-4.9,2.0);target=Vector((0,1.1,1.3));wide.rotation_euler=(target-wide.location).to_track_quat('-Z','Y').to_euler();data.lens=40;data.clip_start=.03
data.dof.use_dof=True;data.dof.focus_distance=(Vector((0,0,1.2))-wide.location).length;data.dof.aperture_fstop=6
station['wide_camera']=wide.name
bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
print('ADULT_FACE_HAIR_KNIT_AND_BACKGROUND_REFINED',flush=True)
