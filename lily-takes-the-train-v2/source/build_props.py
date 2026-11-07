from pathlib import Path
import bpy, math
from mathutils import Vector

def material(name,color,rough=.45,metal=0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

def box(name,size,loc,mat,bevel=.01,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Smooth normals','WEIGHTED_NORMAL')
    if parent:o.parent=parent
    return o

def empty(name,loc=(0,0,0)):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.location=loc;return o

def cylinder(name,r,d,loc,mat,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d,location=loc);o=bpy.context.object;o.name=name
    o.data.materials.append(mat)
    b=o.modifiers.new('Edge glint','BEVEL');b.width=.003;b.segments=2
    for p in o.data.polygons:p.use_smooth=True
    if parent:o.parent=parent
    return o

def path(name,points,r,mat,parent=None):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;c.resolution_u=12
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for b,p in zip(s.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);c.materials.append(mat)
    if parent:o.parent=parent
    return o

def text(name,body,loc,size,mat,parent=None,align='CENTER'):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x=align;c.align_y='CENTER';c.size=size;c.extrude=.0001
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);c.materials.append(mat)
    if parent:o.parent=parent
    return o

def make_props():
    cream=material('Canvas · warm cream',(.75,.66,.48),.86)
    edge=material('Canvas · seam',(.51,.43,.30),.9)
    sage=material('Bottle · sea glass',(.27,.52,.45),.28)
    dark=material('Graphite',(.018,.03,.04),.3)
    leather=material('Wallet · terracotta leather',(.32,.12,.065),.65)
    brass=material('Warm brushed brass',(.58,.34,.12),.3,.65)
    white=material('Screen paper',(.92,.96,.94),.4)
    ink=material('Screen navy',(.025,.06,.09),.45)
    green=material('Screen teal',(.035,.36,.28),.35)
    phone=empty('PROP_Phone',(1.04,-.31,.914))
    box('Phone aluminium frame',(.096,.010,.186),(0,0,0),dark,.010,phone)
    box('Phone glass screen',(.086,.001,.170),(0,-.0058,0),white,.006,phone)
    box('Phone app header',(.086,.001,.047),(0,-.0065,.062),ink,.003,phone)
    text('Rail app title','RAIL',(0,-.0073,.074),.013,white,phone)
    text('Rail app route','GREENFIELD',(0,-.0073,.014),.009,ink,phone)
    text('Rail app time','10:30',(0,-.0073,-.016),.024,ink,phone)
    text('Rail app status','ON TIME',(0,-.0073,-.047),.009,green,phone)
    text('Rail app date','TODAY',(0,-.0073,.052),.006,white,phone)
    box('Phone earpiece',(.022,.001,.002),(0,-.0074,.078),dark,.001,phone)
    phone.rotation_euler=(-math.pi/2,0,.17)
    wallet=empty('PROP_Wallet',(1.23,-.37,.917))
    box('Wallet leather',(.114,.016,.083),(0,0,0),leather,.008,wallet)
    box('Wallet clasp',(.030,.009,.023),(.043,-.010,0),leather,.004,wallet)
    button=cylinder('Wallet brass snap',.006,.003,(.043,-.016,0),brass,wallet);button.rotation_euler=(math.pi/2,0,0)
    wallet.rotation_euler=(-math.pi/2,0,-.2)
    bottle=empty('PROP_Bottle',(1.53,-.32,.885))
    cylinder('Reusable water bottle',.042,.225,(0,0,.12),sage,bottle)
    cylinder('Bottle shoulder',.033,.035,(0,0,.242),sage,bottle)
    cylinder('Bottle cap',.034,.037,(0,0,.271),dark,bottle)
    cylinder('Bottle base',.043,.014,(0,0,.014),dark,bottle)
    path('Cap carry loop',[(-.02,0,.29),(-.018,0,.317),(.018,0,.317),(.02,0,.29)],.005,dark,bottle)
    bag=empty('PROP_SmallBag',(1.53,.12,.885))
    verts=[(-.15,-.075,0),(.15,-.075,0),(.15,.075,0),(-.15,.075,0),(-.17,-.09,.27),(.17,-.09,.27),(.17,.09,.27),(-.17,.09,.27)]
    faces=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new('Canvas bag body');me.from_pydata(verts,[],faces);me.materials.append(cream)
    o=bpy.data.objects.new('Small canvas bag',me);bpy.context.scene.collection.objects.link(o);o.parent=bag
    sol=o.modifiers.new('Canvas thickness','SOLIDIFY');sol.thickness=.004
    bev=o.modifiers.new('Soft canvas edges','BEVEL');bev.width=.017;bev.segments=3
    for side in [-1,1]:
        yy=side*.083
        path('Canvas handle',[(-.10,yy,.24),(-.10,yy,.42),(0,yy,.49),(.10,yy,.42),(.10,yy,.24)],.010,cream,bag)
        path('Top stitched rim',[(-.17,yy,.27),(0,yy,.273),(.17,yy,.27)],.003,edge,bag)
    text('Bag label','good day',(0,-.091,.14),.032,edge,bag)
    # A real wall clock reinforces the nine o'clock line.
    clock=empty('PROP_Clock',(1.18,2.43,1.96))
    ring=cylinder('Clock oak rim',.215,.034,(0,0,0),cream,clock);ring.rotation_euler=(math.pi/2,0,0)
    face=cylinder('Clock face',.197,.006,(0,-.022,0),white,clock);face.rotation_euler=(math.pi/2,0,0)
    for i in range(12):
        a=i*math.pi/6
        b=box('Clock hour mark',(.008,.004,.024),(math.sin(a)*.174,-.027,math.cos(a)*.174),ink,.002,clock);b.rotation_euler[1]=a
    # 9:00: minute hand upward, hour hand to viewer left.
    box('Clock minute hand',(.008,.006,.145),(0,-.032,.065),ink,.003,clock)
    box('Clock hour hand',(.116,.006,.010),(-.05,-.034,0),ink,.003,clock)
    pin=cylinder('Clock spindle',.012,.008,(0,-.039,0),brass,clock);pin.rotation_euler=(math.pi/2,0,0)
    return {'phone':phone,'wallet':wallet,'bottle':bottle,'bag':bag,'clock':clock}
