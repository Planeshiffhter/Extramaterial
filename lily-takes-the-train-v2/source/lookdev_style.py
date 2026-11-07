from pathlib import Path
"""Reference-specific shading and posing, all authored through Blender's API."""
import bpy, math
from mathutils import Vector, Quaternion

def math_node(nodes, operation, a=None, b=None, label=''):
    n=nodes.new('ShaderNodeMath');n.operation=operation;n.label=label
    if a is not None:n.inputs[0].default_value=a
    if b is not None:n.inputs[1].default_value=b
    return n

def style_actor(actor):
    """Keep painted facial detail; darken only the hair, with skin exclusion."""
    mesh=actor['mesh']
    for mat in mesh.data.materials:
        if not mat or not mat.use_nodes:continue
        nt=mat.node_tree;n=nt.nodes;l=nt.links
        p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
        tex=next((x for x in n if x.type=='TEX_IMAGE' and x.image and 'basecolor' in x.image.name),None)
        if p is None or tex is None:continue
        current=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else tex.outputs['Color']
        tc=n.new('ShaderNodeTexCoord');tc.label='Stable undeformed body coordinates'
        sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],sep.inputs[0])
        hsv=n.new('ShaderNodeSeparateColor');hsv.mode='HSV';l.new(tex.outputs['Color'],hsv.inputs[0])
        # Brown hair is dark and saturated. Keep the central skin, lips and eyes.
        high=math_node(n,'GREATER_THAN',b=.795);l.new(sep.outputs['Z'],high.inputs[0])
        dark=math_node(n,'LESS_THAN',b=.48);l.new(hsv.outputs[2],dark.inputs[0])
        sat=math_node(n,'GREATER_THAN',b=.40);l.new(hsv.outputs[1],sat.inputs[0])
        center=math_node(n,'SUBTRACT',b=.5);l.new(sep.outputs['X'],center.inputs[0])
        absolute=math_node(n,'ABSOLUTE');l.new(center.outputs[0],absolute.inputs[0])
        central=math_node(n,'LESS_THAN',b=.096);l.new(absolute.outputs[0],central.inputs[0])
        front=math_node(n,'LESS_THAN',b=.48);l.new(sep.outputs['Y'],front.inputs[0])
        below_fringe=math_node(n,'LESS_THAN',b=.951);l.new(sep.outputs['Z'],below_fringe.inputs[0])
        skin_region=math_node(n,'MULTIPLY');l.new(central.outputs[0],skin_region.inputs[0]);l.new(front.outputs[0],skin_region.inputs[1])
        skin_region2=math_node(n,'MULTIPLY');l.new(skin_region.outputs[0],skin_region2.inputs[0]);l.new(below_fringe.outputs[0],skin_region2.inputs[1])
        inv_skin=math_node(n,'SUBTRACT',a=1);l.new(skin_region2.outputs[0],inv_skin.inputs[1])
        mask=high.outputs[0]
        for factor in [dark.outputs[0],sat.outputs[0],inv_skin.outputs[0]]:
            m=math_node(n,'MULTIPLY');l.new(mask,m.inputs[0]);l.new(factor,m.inputs[1]);mask=m.outputs[0]
        hair=n.new('ShaderNodeHueSaturation');hair.label='Reference dark brown waves'
        hair.inputs['Hue'].default_value=.5;hair.inputs['Saturation'].default_value=.78;hair.inputs['Value'].default_value=.25
        l.new(tex.outputs['Color'],hair.inputs['Color'])
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.label='Preserve facial albedo'
        l.new(mask,mix.inputs[0]);l.new(current,mix.inputs[1]);l.new(hair.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        p.inputs['Metallic'].default_value=0
        if p.inputs['Metallic'].is_linked:l.remove(p.inputs['Metallic'].links[0])
        p.inputs['Roughness'].default_value=.53
        if p.inputs['Roughness'].is_linked:l.remove(p.inputs['Roughness'].links[0])
        p.inputs['IOR'].default_value=1.44
        p.inputs['Subsurface Weight'].default_value=.055
        p.inputs['Subsurface Radius'].default_value=(.8,.4,.2)
        p.inputs['Subsurface Scale'].default_value=.012
        for node in n:
            if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.28

def rotate_world(rig, bone_name, axis, degrees):
    pb=rig.pose.bones.get(bone_name)
    if not pb:return
    pb.rotation_mode='QUATERNION'
    orientation=(rig.matrix_world@pb.matrix).to_quaternion()
    local_axis=orientation.inverted()@Vector(axis)
    pb.rotation_quaternion=pb.rotation_quaternion@Quaternion(local_axis,math.radians(degrees))
    bpy.context.view_layer.update()

def relax_actor(actor, camera_location=(.35,-3.28,1.55)):
    rig=actor['rig'];rig.animation_data_clear()
    for pb in rig.pose.bones:pb.matrix_basis.identity()
    bpy.context.view_layer.update()
    rotate_world(rig,'LeftArm',(0,1,0),18)
    rotate_world(rig,'RightArm',(0,1,0),-18)
    rotate_world(rig,'LeftForeArm',(1,0,0),-12)
    rotate_world(rig,'RightForeArm',(1,0,0),-12)
    eye=rig.matrix_world@rig.pose.bones['Head'].head
    delta=Vector(camera_location)-eye
    yaw=math.degrees(math.atan2(delta.x,-delta.y))
    rotate_world(rig,'Head',(0,0,1),yaw)
    rotate_world(rig,'Head',(0,1,0),-1.5)

def area(name,loc,target,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);bpy.context.scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def home_lighting(scene):
    for o in scene.objects:
        if o.type=='LIGHT':o.hide_render=True
    area('V2 Soft window key',(-2.7,-1.6,3.5),(0,0,1.25),420,3.0,(1,.88,.76))
    area('V2 Soft camera fill',(2,-2.6,2.6),(0,0,1.3),110,3.5,(.82,.9,1))
    area('V2 Window rim',(-1.3,1.8,2.6),(0,0,1.4),160,2.0,(1,.94,.85))
    world=scene.world or bpy.data.worlds.new('V2 Warm daylight');scene.world=world;world.use_nodes=True
    b=world.node_tree.nodes.get('Background');b.inputs[0].default_value=(.58,.69,.85,1);b.inputs[1].default_value=.18

def camera(scene,name,loc,target,lens,focus=None,fstop=3.2):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens;d.clip_start=.02;d.clip_end=150
    if focus is not None:
        d.dof.use_dof=True;d.dof.focus_distance=(Vector(focus)-o.location).length;d.dof.aperture_fstop=fstop;d.dof.aperture_blades=8
    scene.camera=o;return o

def cpu_cycles(scene,samples=32,width=960,height=540):
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=samples
    scene.cycles.use_denoising=False;scene.cycles.max_bounces=6
    scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=6
    scene.cycles.transparent_max_bounces=8;scene.cycles.use_adaptive_sampling=True
    scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.use_persistent_data=False
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    scene.view_layers[0].cycles.denoising_store_passes=True
    scene.render.image_settings.file_format='OPEN_EXR_MULTILAYER';scene.render.image_settings.color_depth='32'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
    print('DEVICE_CONFIRMATION: Cycles CPU; no GPU requested or enabled.',flush=True)
