from pathlib import Path
"""CC0 adult Lily character, imported from Grab3D Casual Woman.
Source: https://grab3d.com/models/characters/woman/ (CC0, AI-assisted base).
Body rig is a 54-bone deform rig; face controls below are custom new geometry.
No addon or auto-executed scripts are required. Dimensions are in metres.
"""
import bpy, math, json
from array import array
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SOURCE=str(Path(__file__).with_name('casual_woman_compatible.blend'))
MOUTH_Z=1.4865

def smooth(a,b,x):
    if a==b:return float(x>=b)
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)

def seam(x):return MOUTH_Z+.0068*min(1.4,(x/.031)**2)

def material(name,color,roughness=.55):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness
    return m

def append_lily(scene=None,facial=True):
    scene=scene or bpy.context.scene
    with bpy.data.libraries.load(SOURCE,link=False) as (src,dst):
        dst.objects=['Armature','char1'];dst.actions=list(src.actions)
    rig=next(o for o in dst.objects if o.type=='ARMATURE');mesh=next(o for o in dst.objects if o.type=='MESH')
    for o in (rig,mesh):
        if not o.users_collection:scene.collection.objects.link(o)
    rig.name='Lily_Body_Rig';mesh.name='Lily_Actor_Mesh';rig.animation_data_clear()
    # GLTF bone tails were exported100times too long; head positions and axes are correct.
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for b in rig.data.edit_bones:b.tail=b.head+(b.tail-b.head)*.01
    bpy.ops.object.mode_set(mode='OBJECT')
    for b in rig.pose.bones:b.matrix_basis.identity()
    for b in rig.pose.bones:
        if b.custom_shape:b.custom_shape=None
    root=bpy.data.objects.new('Lily_Actor',None);scene.collection.objects.link(root);rig.parent=root
    rig['license']='CC0 1.0 — Grab3D Casual Woman, AI-assisted base';rig['source']='https://grab3d.com/models/characters/woman/'
    bpy.context.view_layer.update()
    actor={'rig':rig,'mesh':mesh,'root':root,'facial':{},'mouth_objects':[],'eyelids':[],'actions':{a.name:a for a in dst.actions}}
    for a in dst.actions:a.use_fake_user=True
    if facial:build_face(actor)
    return actor

import_character=append_lily

def _head_bind(obj,actor):
    obj.parent=actor['root'];v=obj.vertex_groups.new(name='Head');v.add(list(range(len(obj.data.vertices))),1.0,'REPLACE')
    mod=obj.modifiers.new('Follow animated head','ARMATURE');mod.object=actor['rig']
    return obj

def _mesh_object(name,verts,faces,actor,mat=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    _head_bind(o,actor);return o

def _oral_piece(name,location,scale,mat,actor,lower=False):
    if 'tooth' in name:
        bpy.ops.mesh.primitive_cube_add(size=2,location=location)
    else:bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=location)
    o=bpy.context.object;o.name=name
    for v in o.data.vertices:
        v.co.x*=scale[0];v.co.y*=scale[1];v.co.z*=scale[2]
    # Bake world position into coordinates so Head armature uses the same rest frame.
    for v in o.data.vertices:v.co+=Vector(location)
    o.location=(0,0,0);o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    if 'tooth' in name:
        bevel=o.modifiers.new('Soft tooth edges','BEVEL');bevel.width=.00065;bevel.segments=3
        bevel.affect='EDGES';bevel.harden_normals=True
        norm=o.modifiers.new('Flat natural tooth fronts','WEIGHTED_NORMAL');norm.keep_sharp=True
    _head_bind(o,actor)
    if lower:
        o.shape_key_add(name='Basis');k=o.shape_key_add(name='Jaw_Open')
        for p in k.data:p.co.z-=.0175;p.co.y+=.001
        actor['facial'].setdefault('lower_oral',[]).append(k)
    actor['mouth_objects'].append(o);return o

def build_face(actor):
    mesh=actor['mesh'];mw=mesh.matrix_world.copy();inv=mw.inverted()
    dark=material('Lily mouth interior',(.055,.009,.013),.94)
    teeth=material('Lily natural ivory teeth',(.78,.73,.61),.32)
    tongue=material('Lily tongue',(.28,.055,.072),.62)
    mesh.data.materials.append(dark)
    # A real boolean recess opens the lip seam. It does not stretch a sealed surface.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=24,location=(0,0,0))
    cutter=bpy.context.object;cutter.name='Mouth cavity cutter'
    for v in cutter.data.vertices:
        x=v.co.x*.0285;v.co=(x,-.095+v.co.y*.036,seam(x)+v.co.z*.00135)
    cutter.data.materials.append(mesh.data.materials[0]);cutter.data.materials.append(dark)
    for p in cutter.data.polygons:p.material_index=1
    bpy.context.view_layer.objects.active=mesh;mesh.select_set(True);cutter.select_set(False)
    cut=mesh.modifiers.new('Actual lip opening and oral recess','BOOLEAN');cut.object=cutter;cut.operation='DIFFERENCE';cut.solver='EXACT'
    # Move before the armature so geometry stays in its rest position.
    bpy.ops.object.modifier_move_up(modifier=cut.name)
    bpy.ops.object.modifier_apply(modifier=cut.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    # The mouth cut carries dark material on its newly generated internal faces.
    basis=mesh.shape_key_add(name='Basis')
    jaw=mesh.shape_key_add(name='Jaw_Open');roundkey=mesh.shape_key_add(name='Mouth_O');smile=mesh.shape_key_add(name='Smile')
    for i,v in enumerate(mesh.data.vertices):
        w=mw@v.co;x,y,z=w;s=seam(x);dz=z-s
        wx=1-smooth(.027,.052,abs(x));wy=1-smooth(-.060,-.035,y)
        wz=1-smooth(.011,.046,abs(dz));weight=wx*wy*wz
        if weight>.00001:
            side=math.tanh(dz/.00065)
            down=(1-side)*.5
            d=(.0018*(1-down)-.0175*down)*weight
            j=w.copy();j.z+=d;j.y+=.0015*down*weight;jaw.data[i].co=inv@j
            ro=w.copy();ro.x-=x*.29*weight;ro.y-=.0023*weight;roundkey.data[i].co=inv@ro
            su=w.copy();corner=smooth(.008,.025,abs(x))*weight
            su.x+=math.copysign(.0028*corner,x);su.z+=.0028*corner;smile.data[i].co=inv@su
    actor['facial'].update(jaw=jaw,round=roundkey,smile=smile)
    # Recessed individual upper and lower teeth and a small tongue remain behind lips.
    for i in range(8):
        x=(i-3.5)*.0049;curve=(x/.023)**2
        _oral_piece('Lily upper tooth %02d'%i,(x,-.083+curve*.003,1.4858),(.00245,.0026,.0033),teeth,actor)
        _oral_piece('Lily lower tooth %02d'%i,(x,-.080+curve*.003,1.4858),(.00235,.0024,.0021),teeth,actor,lower=True)
    _oral_piece('Lily tongue',(0,-.072,1.4860),(.018,.010,.0031),tongue,actor,lower=True)
    # Raycast the actual textured facial surface to fit eyelid skins tightly.
    mesh.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in mesh.data.loop_triangles]
    coords=[mw@v.co for v in mesh.data.vertices]
    bvh=BVHTree.FromPolygons(coords,triangles,all_triangles=True)
    skin=material('Lily eyelid skin',(.74,.49,.39),.67)
    tex=bpy.data.images.get('rig_basecolor');pix=array('f',[0.0])*len(tex.pixels);tex.pixels.foreach_get(pix)
    skin_source=(mesh,bvh,tex,pix)
    for side,cx in [('L',.0388),('R',-.0388)]:
        create_eyelid(actor,bvh,side,cx,skin,skin_source)
    actor['root']['face_controls']='Jaw_Open, Mouth_O, Smile on Lily_Actor_Mesh; Blink on Lily eyelid.L/R'
    actor['root']['facial_geometry']='Boolean oral recess; separate upper/lower teeth and tongue; fitted upper eyelid skins'
    return actor

def create_eyelid(actor,bvh,side,cx,mat,skin_source):
    # Two fitted skins close toward one natural seam. The lower lid rises slightly,
    # while the upper lid does most of the closing, covering the original painted lash.
    for is_lower in (False,True):
        verts=[];closed=[];faces=[];nx=40;ny=24 if not is_lower else 12;cz=1.5513;rx=.0239
        for j in range(ny+1):
            t=j/ny
            for i in range(nx+1):
                q=-1+2*i/nx;x=cx+rx*q;arc=math.sqrt(max(0.,1-q*q));slope=.0015*q*(1 if cx>0 else -1)
                upper=cz+.0122*arc+slope;lower=cz-.0103*arc+slope;line=cz-.0035*arc+slope
                if not is_lower:
                    border=upper+.0055*arc;zo=border-.0061*arc*t;zc=border+(line-border)*t
                else:
                    border=lower-.0045*arc;zo=border+.0049*arc*t;zc=border+(line+.0001-border)*t
                def point(z):
                    hit,_,_,_=bvh.ray_cast(Vector((x,-.30,z)),Vector((0,1,0)))
                    y=hit.y-.0005 if hit else -.103
                    return (x,y,z)
                verts.append(point(zo));closed.append(point(zc))
        for j in range(ny):
            for i in range(nx):
                a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1) if is_lower else (a,a+nx+1,a+nx+2,a+1))
        label=('Lily lower eyelid.' if is_lower else 'Lily eyelid.')+side
        o=_mesh_object(label,verts,faces,actor,mat.copy());_eyelid_texture(o,skin_source,cx,cz,rx,nx,ny,side,is_lower)
        o.shape_key_add(name='Basis');k=o.shape_key_add(name='Blink')
        for p,co in zip(k.data,closed):p.co=co
        actor['facial'][('blink_lower_' if is_lower else 'blink_')+side]=k;actor['eyelids'].append(o)
    return o

def _skin_sample(source,x,z):
    mesh,bvh,tex,pix=source
    p,normal,idx,dist=bvh.ray_cast(Vector((x,-.30,z)),Vector((0,1,0)))
    if p is None:return (.90,.67,.55)
    tri=mesh.data.loop_triangles[idx];mw=mesh.matrix_world
    a,b,c=[mw@mesh.data.vertices[v].co for v in tri.vertices]
    v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-18:return (.90,.67,.55)
    vv=(d11*d20-d01*d21)/den;ww=(d00*d21-d01*d20)/den;uv=mesh.data.uv_layers.active.data
    u0,u1,u2=[uv[l].uv for l in tri.loops];tx,ty=u0*(1-vv-ww)+u1*vv+u2*ww
    W,H=tex.size;ix=max(0,min(W-1,int(tx*(W-1))));iy=max(0,min(H-1,int(ty*(H-1))));k=(iy*W+ix)*4
    return pix[k:k+3]

def _eyelid_texture(o,source,cx,cz,rx,nx,ny,side,is_lower=False):
    # Project nearby real skin texture over the eyelid; the moving bottom edge has a fine lash line.
    uv=o.data.uv_layers.new(name='Lid UV')
    for poly in o.data.polygons:
        for loop_index in poly.loop_indices:
            vi=o.data.loops[loop_index].vertex_index;i=vi%(nx+1);j=vi//(nx+1);uv.data[loop_index].uv=(i/nx,j/ny)
    upper=[];lower=[]
    for i in range(nx+1):
        q=-1+2*i/nx;x=cx+rx*q;arc=math.sqrt(max(0,1-q*q));slope=.0015*q*(1 if cx>0 else -1)
        if not is_lower:
            upper.append(_skin_sample(source,x,cz+.0122*arc+slope+.006));lower.append(_skin_sample(source,x,cz-.0103*arc+slope-.005))
        else:
            col=_skin_sample(source,x,cz-.0103*arc+slope-.005);upper.append(col);lower.append(col)
    # Smooth texture lighting across columns; a stretched iris sample must not stripe the lid.
    for colors in (upper,lower):
        average=[sum(c[k] for c in colors[5:-5])/len(colors[5:-5]) for k in range(3)]
        colors[:]=[tuple(average[k]*(1-(.15+.85*smooth(.68,1.,abs(i/nx*2-1))))+col[k]*(.15+.85*smooth(.68,1.,abs(i/nx*2-1))) for k in range(3)) for i,col in enumerate(colors)]
    W,H=256,128;pixels=array('f')
    for py in range(H):
        t=py/(H-1)
        for px in range(W):
            q=px/(W-1)*nx;i=min(nx-1,int(q));a=q-i
            col=[]
            for c in range(3):
                top=upper[i][c]*(1-a)+upper[i+1][c]*a;bot=lower[i][c]*(1-a)+lower[i+1][c]*a
                v=top*(1-t*.65)+bot*t*.65
                lash=(0. if is_lower else smooth(.965,.99,t)*(1-smooth(.90,1.0,abs(px/(W-1)*2-1))))
                v=v*(1-lash*.73);col.append(v)
            pixels.extend((*col,1.0))
    im=bpy.data.images.new(('Lily lower lid texture.' if is_lower else 'Lily eyelid skin texture.')+side,width=W,height=H,alpha=False);im.pixels.foreach_set(pixels);im.pack()
    mat=o.data.materials[0];mat.name=('Lily matched lower eyelid.' if is_lower else 'Lily matched eyelid.')+side;node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;mat.node_tree.nodes.active=node;mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

def set_face(actor,jaw=None,round=None,smile=None,blink=None,frame=None):
    f=actor['facial']
    values={'jaw':jaw,'round':round,'smile':smile}
    if blink is not None:values.update(blink_L=blink,blink_R=blink,blink_lower_L=blink,blink_lower_R=blink)
    for name,value in values.items():
        if value is None or name not in f:continue
        k=f[name];k.value=max(0.,min(1.,float(value)))
        if frame is not None:k.keyframe_insert('value',frame=frame)
    if jaw is not None:
        for k in f.get('lower_oral',[]):
            k.value=max(0.,min(1.,float(jaw)))
            if frame is not None:k.keyframe_insert('value',frame=frame)

def profile(actor):
    r=actor['rig'];bpy.context.view_layer.update()
    return {'height':1.70,'forward':[0,-1,0],'mesh_local_scale':list(actor['mesh'].scale),'mesh_world_scale':list(actor['mesh'].matrix_world.to_scale()),'bone_rest_world':{b.name:{'head':list(r.matrix_world@b.head),'tail':list(r.matrix_world@b.tail)} for b in r.pose.bones},'mouth_center':[0,-.103,1.4865],'eye_centers':[[-.0388,-.105,1.5513],[.0388,-.105,1.5513]],'texture':'rig_basecolor, embedded2048² sRGB'}
