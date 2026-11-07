from pathlib import Path
"""Reference sage crewneck and blue jeans, generated as native rigged geometry.

No topology edits to the source actor. New meshes are defined in world meters,
then weighted from the existing character surface and attached preserving its
centimeter-scaled armature transforms.
"""
import bpy, math
from array import array
from mathutils import Vector, Matrix

def _mat(name, color, roughness=.82, knit=False):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True;mat.diffuse_color=(*color,1)
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bs=nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Sheen Weight'].default_value=.18
    if knit and not nodes.get('Fine knit fibers'):
        tex=nodes.new('ShaderNodeTexNoise');tex.name='Fine knit fibers'
        tex.inputs['Scale'].default_value=650;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.65
        bump=nodes.new('ShaderNodeBump');bump.name='Subtle fabric knit relief'
        bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.00065
        links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat

def _mesh(name, verts, faces, mat, collection):
    mesh=bpy.data.meshes.new(name+'Mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj);mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=True
    return obj

def _loft(name, sections, mat, collection, steps=64, rib=0, caps=False):
    """sections = (center, axis, elliptical radius1, radius2)."""
    verts=[];faces=[]
    for center,axis,r1,r2 in sections:
        center=Vector(center);axis=Vector(axis).normalized()
        side=Vector((0,1,0))
        if abs(axis.dot(side))>.95:side=Vector((1,0,0))
        u=axis.cross(side).normalized();v=axis.cross(u).normalized()
        for i in range(steps):
            a=2*math.pi*i/steps
            ripple=1+rib*math.cos(32*a)
            verts.append(center+u*(r1*math.cos(a)*ripple)+v*(r2*math.sin(a)*ripple))
    for j in range(len(sections)-1):
        for i in range(steps):
            a=j*steps+i;b=j*steps+(i+1)%steps
            faces.append((a,b,b+steps,a+steps))
    if caps:
        faces.append(tuple(reversed(range(steps))))
        faces.append(tuple(range((len(sections)-1)*steps,len(sections)*steps)))
    return _mesh(name,verts,faces,mat,collection)

def _continuous_garment(objects, name, mat, collection):
    """Union closed native lofts into one soft, continuous fabric silhouette."""
    verts=[];faces=[]
    for obj in objects:
        offset=len(verts)
        verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    garment=_mesh(name,verts,faces,mat,collection)
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.view_layer.objects.active=garment;garment.select_set(True)
    remesh=garment.modifiers.new('Continuous sewn garment volume','REMESH')
    remesh.mode='VOXEL';remesh.voxel_size=.005;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=garment.modifiers.new('Relaxed shoulder and crotch seams','SMOOTH');smooth.factor=1.2;smooth.iterations=5
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    garment.select_set(False)
    return garment

def _neck_opening(garment):
    """Cut a real oval opening after volume union, preserving a free neck."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=2,location=(0,.020,1.60))
    cutter=bpy.context.object;cutter.name='Temporary oval crewneck opening'
    cutter.scale=(.067,.057,.40)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=garment
    cut=garment.modifiers.new('Actual oval neck opening','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=cutter
    bpy.ops.object.modifier_apply(modifier=cut.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

def _ribbed_neck(mat,collection):
    verts=[];faces=[];steps=128
    # Front sits at Z1.36; the back follows the adult neck base at Z1.41.
    # Five oval strips make a small fabric band around the actual cut-out.
    strips=[(.070,.060,-.004),(.074,.064,.002),(.073,.063,.010),(.067,.057,.010),(.067,.057,-.004)]
    for rx,ry,dz in strips:
        for i in range(steps):
            a=2*math.pi*i/steps;rib=1+.010*math.cos(64*a)
            verts.append((rx*math.cos(a)*rib,.020+ry*math.sin(a)*rib,1.385+.025*math.sin(a)+dz))
    for j in range(len(strips)):
        k=(j+1)%len(strips)
        for i in range(steps):faces.append((j*steps+i,j*steps+(i+1)%steps,k*steps+(i+1)%steps,k*steps+i))
    return _mesh('Lily tilted oval ribbed crewneck collar',verts,faces,mat,collection)

def _cloth_ease(garment):
    # Millimeter-scale drape ridges break the rigid cylinder appearance without
    # cloth simulation or a topology change to the actor itself.
    for v in garment.data.vertices:
        p=v.co
        if .88<p.z<1.28:
            blend=math.sin(math.pi*(p.z-.88)/.40)**2
            front=max(0,min(1,(-p.y-.025)/.09))
            p.y-=.0027*blend*front*math.sin(61*p.z+10*p.x)
            p.x+=.0018*blend*math.sin(53*p.z+14*p.y)
    garment.data.update()

def _bone_head(rig, name, fallback):
    b=rig.data.bones.get(name)
    return rig.matrix_world@b.head_local if b else Vector(fallback)

def _weight(obj, source, rig):
    for group in source.vertex_groups:
        if group.name not in obj.vertex_groups:obj.vertex_groups.new(name=group.name)
    transfer=obj.modifiers.new('Fit painted character body weights','DATA_TRANSFER')
    transfer.object=source;transfer.use_vert_data=True
    transfer.data_types_verts={'VGROUP_WEIGHTS'};transfer.vert_mapping='POLYINTERP_NEAREST'
    transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME'
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    try:bpy.ops.object.modifier_apply(modifier=transfer.name)
    except RuntimeError:
        # Fallback remains the same intended nearest-surface data transfer,
        # evaluated before the armature rather than forcing an unsafe context.
        pass
    obj.select_set(False)
    smooth=obj.modifiers.new('Soft garment surface','SUBSURF');smooth.levels=1;smooth.render_levels=1
    arm=obj.modifiers.new('Follow Lily body rig','ARMATURE');arm.object=rig
    # Skinning before subdivision keeps cuffs and upper-arm bends clean.
    obj.modifiers.move(len(obj.modifiers)-1,0)
    world=obj.matrix_world.copy();obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted();obj.matrix_world=world
    obj['wardrobe']='Reference sage sweater / full length denim jeans'

def _recolor_underlayer(mesh):
    """Hide original clothing under new garments; preserve head shader inputs."""
    attr_name='LilyWardrobeCoverage'
    attr=mesh.data.color_attributes.get(attr_name) or mesh.data.color_attributes.new(name=attr_name,type='FLOAT_COLOR',domain='POINT')
    group_names={g.index:g.name.lower() for g in mesh.vertex_groups}
    # The old jacket collar may share neck weights. Identify only its strongly
    # orange UV pixels so exposing the neck does not expose an orange lapel.
    orange=set();uv=mesh.data.uv_layers.active
    image=next((im for im in bpy.data.images if im.name.startswith('rig_basecolor')),None)
    if image and uv:
        pixels=array('f',[0.0])*(image.size[0]*image.size[1]*4)
        image.pixels.foreach_get(pixels);width,height=image.size
        possible={v.index for v in mesh.data.vertices if 1.34<(mesh.matrix_world@v.co).z<1.415}
        for loop in mesh.data.loops:
            if loop.vertex_index not in possible:continue
            tex=uv.data[loop.index].uv
            index=(int((tex.y%1)*(height-1))*width+int((tex.x%1)*(width-1)))*4
            r,g,b=pixels[index:index+3]
            if r>1.5*g and r>0.01 and b/r<.22:orange.add(loop.vertex_index)
    for vertex in mesh.data.vertices:
        p=mesh.matrix_world@vertex.co
        weights={group_names.get(g.group,''):g.weight for g in vertex.groups}
        head=max([w for n,w in weights.items() if 'head' in n]+[0])
        neck=max([w for n,w in weights.items() if 'neck' in n]+[0])
        hand=max([w for n,w in weights.items() if 'hand' in n or 'finger' in n or 'thumb' in n]+[0])
        torso=sum(w for n,w in weights.items() if 'spine' in n or 'shoulder' in n or ('arm' in n and 'forearm' not in n) or 'forearm' in n)
        # Actual source blazer lapels project far beyond a sweater surface.
        # Hide that entire clothing surface through the shader, without deleting
        # or relocating vertices (facial shape keys remain untouched). Hair,
        # neck, hands, and shoes retain their complete original surface shader.
        neck_skin=(p.z>1.345 and (p.x/.070)**2+((p.y-.020)/.062)**2<1.0 and vertex.index not in orange)
        mask=float(.14<p.z<1.405 and head<.18 and neck<.65 and hand<.48 and not neck_skin)
        attr.data[vertex.index].color=(mask,mask,mask,1)
    for material in mesh.data.materials:
        if not material or not material.use_nodes:continue
        nodes=material.node_tree.nodes;links=material.node_tree.links
        if nodes.get('Lily hide original blazer and trousers'):continue
        attribute=nodes.new('ShaderNodeVertexColor');attribute.layer_name=attr_name;attribute.name='Lily wardrobe region mask'
        output=next((n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        if output is None or not output.inputs['Surface'].is_linked:continue
        old=output.inputs['Surface'].links[0].from_socket
        transparent=nodes.new('ShaderNodeBsdfTransparent');transparent.name='Covered source clothing is transparent'
        mix=nodes.new('ShaderNodeMixShader');mix.name='Lily hide original blazer and trousers'
        links.new(old,mix.inputs[1]);links.new(transparent.outputs[0],mix.inputs[2])
        links.new(attribute.outputs['Color'],mix.inputs[0]);links.new(mix.outputs[0],output.inputs['Surface'])

def add_reference_wardrobe(mesh, rig):
    """Add rigged reference garments; return their new object list."""
    collection=bpy.data.collections.get('Lily_Reference_Wardrobe')
    if collection is None:
        collection=bpy.data.collections.new('Lily_Reference_Wardrobe');bpy.context.scene.collection.children.link(collection)
    sage=_mat('Lily sage knit pullover',(.34,.45,.30),.86,True)
    ribmat=_mat('Lily sage ribbed collar and cuffs',(.29,.39,.255),.88,True)
    denim=_mat('Lily fitted blue denim',(.035,.105,.23),.87,True)
    objects=[]
    # Long closed-front torso: seven continuous quad rings remove the old V/lapel
    # silhouette. The neckline is a true small crewneck opening.
    torso_sections=[]
    for z,rx,ry,cy in [(.865,.196,.123,.016),(.89,.194,.122,.015),(.97,.169,.112,.012),(1.06,.153,.107,.009),(1.17,.163,.120,.004),(1.26,.175,.122,.010),(1.310,.178,.115,.014),(1.335,.180,.100,.014),(1.385,.070,.060,.020)]:
        torso_sections.append(((0,cy,z),(0,0,1),rx,ry))
    torso=_loft('Lily crewneck sweater torso',torso_sections,sage,collection,caps=True)
    # Shoulder height peaks at the sides; front chest falls naturally toward a
    # lower crewneck rather than forming a horizontal plank below the chin.
    for i in range(64):
        a=2*math.pi*i/64
        torso.data.vertices[7*64+i].co.z=1.335+.041*math.cos(a)**2
        p=torso.data.vertices[8*64+i].co;p.z=1.385+.025*(p.y-.020)/.060
    objects.append(torso)
    objects.append(_ribbed_neck(ribmat,collection))
    hem=[((0,.016,.865+t),(0,0,1),.198,.125) for t in (0,.007,.015,.025)]
    objects.append(_loft('Lily ribbed sweater hem',hem,ribmat,collection,128,.014))
    # A-pose sleeves use actual joint HEAD positions, never the imported glTF
    # dummy bone tails. This remains valid for the source centimeter rig scale.
    for side,sign in [('Left',1),('Right',-1)]:
        shoulder=_bone_head(rig,side+'Arm',(sign*.13,.01,1.354))
        elbow=_bone_head(rig,side+'ForeArm',(sign*.236,0,1.15))
        wrist=_bone_head(rig,side+'Hand',(sign*.364,0,.957))
        upper=(elbow-shoulder).normalized();lower=(wrist-elbow).normalized()
        c0=shoulder+upper*.012;c1=shoulder.lerp(elbow,.27);c2=shoulder.lerp(elbow,.72)
        c3=elbow;c4=elbow.lerp(wrist,.45);c5=wrist-lower*.012
        sections=[(c0,upper,.071,.078),(c1,upper,.074,.076),(c2,upper,.066,.069),(c3,(upper+lower).normalized(),.062,.063),(c4,lower,.058,.061),(c5,lower,.050,.052)]
        objects.append(_loft('Lily '+side.lower()+' full sweater sleeve',sections,sage,collection,caps=True))
        cuffs=[(wrist-lower*d,lower,.048,.050) for d in (.037,.027,.016,.006)]
        objects.append(_loft('Lily '+side.lower()+' ribbed cuff',cuffs,ribmat,collection,128,.022))
    # Full-length narrow denim legs and hip yoke, kept separate at the natural
    # crotch/waist seams and combined by color. Sweater overlaps the waistband.
    hips=[((0,.013,z),(0,0,1),rx,ry) for z,rx,ry in [(.785,.055,.074),(.83,.165,.108),(.88,.187,.115),(.93,.172,.110),(.99,.150,.101)]]
    objects.append(_loft('Lily denim hip yoke',hips,denim,collection,caps=True))
    for side,sign in [('Left',1),('Right',-1)]:
        hip=_bone_head(rig,side+'UpLeg',(sign*.094,.016,.896))
        knee=_bone_head(rig,side+'Leg',(sign*.132,-.016,.544))
        ankle=_bone_head(rig,side+'Foot',(sign*.165,.038,.143))
        axis=(ankle-hip).normalized()
        sections=[(hip.lerp(knee,.18),axis,.087,.096),(hip.lerp(knee,.30),axis,.080,.089),(hip.lerp(knee,.65),axis,.067,.079),(knee,axis,.059,.070),(knee.lerp(ankle,.55),axis,.052,.058),(ankle+Vector((0,0,-.010)),axis,.045,.048)]
        objects.append(_loft('Lily '+side.lower()+' full-length fitted jeans',sections,denim,collection,caps=True))
    sweater_parts=[o for o in objects if 'sweater torso' in o.name or 'full sweater sleeve' in o.name]
    pants_parts=[o for o in objects if 'denim hip' in o.name or 'full-length fitted jeans' in o.name]
    objects=[o for o in objects if o not in sweater_parts and o not in pants_parts]
    sweater=_continuous_garment(sweater_parts,'Lily continuous sage crewneck sweater',sage,collection)
    _neck_opening(sweater);_cloth_ease(sweater);objects.append(sweater)
    objects.append(_continuous_garment(pants_parts,'Lily continuous fitted blue jeans',denim,collection))
    for obj in objects:_weight(obj,mesh,rig)
    _recolor_underlayer(mesh)
    bpy.context.view_layer.update()
    return objects
