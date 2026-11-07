from pathlib import Path
"""Cozy kitchen set for Lily. Blender 4.3; units metres, character origin (0,0,0).

Use: import build_environment; build_environment.build_environment()
The optional command-line execution saves environment.blend and preview.png.
"""
import bpy, math
from mathutils import Vector

COL = None
M = {}

def relink(ob):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    COL.objects.link(ob)
    return ob

def mat(name, color, rough=.5, metal=0):
    m=bpy.data.materials.new('Env_'+name); m.diffuse_color=(*color,1)
    m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m

def grain(name, color):
    m=mat(name,color,.48); n=m.node_tree.nodes; l=m.node_tree.links
    p=n.get('Principled BSDF'); tex=n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=5; tex.inputs['Detail'].default_value=2
    tc=n.new('ShaderNodeTexCoord'); vm=n.new('ShaderNodeVectorMath'); vm.operation='MULTIPLY'
    vm.inputs[1].default_value=(2,28,3); l.new(tc.outputs['Generated'],vm.inputs[0]); l.new(vm.outputs[0],tex.inputs[0])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.15; ramp.color_ramp.elements[0].color=(*[c*.65 for c in color],1)
    ramp.color_ramp.elements[1].position=.9; ramp.color_ramp.elements[1].color=(*[min(c*1.2,1) for c in color],1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.10; bump.inputs['Distance'].default_value=.015
    l.new(tex.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],p.inputs['Normal'])
    return m

def cube(name, loc, size, material, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=relink(bpy.context.object); o.name='Env_'+name
    o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL'); b.width=bevel; b.segments=3
        b=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def cyl(name, loc, radius, depth, material, vertices=32, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=relink(bpy.context.object);o.name='Env_'+name
    if rotation:o.rotation_euler=rotation
    if material:o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    b=o.modifiers.new('Rounded rim','BEVEL');b.width=.008;b.segments=2
    o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def uv(name,loc,size,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc)
    o=relink(bpy.context.object);o.name='Env_'+name;o.scale=size
    if material:o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def curve(name,points,thick,material):
    cu=bpy.data.curves.new('Env_'+name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=thick;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for b,co in zip(sp.bezier_points,points):b.co=co;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    ob=bpy.data.objects.new('Env_'+name,cu);COL.objects.link(ob)
    if material:cu.materials.append(material)
    return ob

def torus(name,loc,major,minor,material,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=10,location=loc,rotation=rot)
    o=relink(bpy.context.object);o.name='Env_'+name;o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def plant(name,loc,scale=1):
    x,y,z=loc
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.105*scale,radius2=.135*scale,depth=.23*scale,location=(x,y,z+.115*scale))
    pot=relink(bpy.context.object);pot.name='Env_'+name+'_pot';pot.data.materials.append(M['ceramic'])
    cyl(name+'_soil',(x,y,z+.225*scale),.119*scale,.015*scale,M['soil'])
    for i in range(10):
        a=i*2.3999; r=(.10+.025*(i%3))*scale; h=(.30+.045*(i%4))*scale
        tip=(x+math.cos(a)*r,y+math.sin(a)*r,z+h)
        curve(name+'_stem'+str(i),[(x,y,z+.20*scale),tip],.006*scale,M['leaf'])
        le=uv(name+'_leaf'+str(i),tip,(.055*scale,.02*scale,.13*scale),M['leaflight'] if i%2 else M['leaf'])
        le.rotation_euler=(math.sin(a)*.7,math.cos(a)*.7,a)

def handle(name,x,y,z,width=.14):
    # Cabinet fronts face towards negative Y.
    for xx in [-width/2,width/2]:cyl(name+'_fix',(x+xx,y+.016,z),.012,.035,M['brass'],rotation=(math.pi/2,0,0))
    return curve(name,[(x-width/2,y,z),(x-width/2,y-.025,z),(x+width/2,y-.025,z),(x+width/2,y,z)],.011,M['brass'])

def cabinet(x,width,drawers=False):
    cube('cabinet carcass',(x,2.075,.43),(width-.014,.70,.84),M['sage'],.015)
    cube('cabinet toe',(x,2.09,.065),(width-.025,.56,.13),M['dark_sage'],.008)
    if drawers:
        for i in range(3):
            z=.21+i*.255
            cube('drawer frame',(x,1.704,z),(width-.035,.036,.235),M['sage'],.009)
            cube('drawer recessed panel',(x,1.681,z),(width-.12,.015,.155),M['sage_panel'],.006)
            handle('drawer pull',x,1.65,z+.04)
    else:
        for xx in [x-width/4,x+width/4]:
            cube('shaker door',(xx,1.704,.48),(width/2-.025,.036,.69),M['sage'],.008)
            cube('shaker inset',(xx,1.681,.48),(width/2-.105,.016,.58),M['sage_panel'],.006)
            handle('door pull',xx,1.652,.72,.115)

def area(name,loc,power,size,color,target):
    d=bpy.data.lights.new('Env_'+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new('Env_'+name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def build_environment():
    global COL,M
    old=bpy.data.collections.get('Home_Set')
    if old:
        for ob in list(old.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(old)
    COL=bpy.data.collections.new('Home_Set');bpy.context.scene.collection.children.link(COL)
    M={
       'wall':mat('Warm plaster',(.78,.755,.67),.85),
       'trim':mat('Ivory enamel',(.87,.86,.79),.38),
       'sage':mat('Sage cabinet paint',(.29,.40,.33),.42),
       'sage_panel':mat('Sage recessed panel',(.26,.36,.30),.45),
       'dark_sage':mat('Cabinet toe shadow',(.15,.21,.17),.65),
       'wood':grain('Honey oak',(.64,.44,.24)),
       'floor':grain('Pale oak floor',(.48,.34,.21)),
       'brass':mat('Aged brass',(.46,.32,.14),.28,.75),
       'chrome':mat('Brushed steel',(.52,.57,.55),.23,.9),
       'stove':mat('Oven charcoal',(.035,.045,.042),.3,.28),
       'glass':mat('Dark oven glass',(.035,.055,.06),.15,.35),
       'ceramic':mat('Ivory stoneware',(.76,.70,.56),.4),
       'leaf':mat('Deep foliage',(.09,.22,.07),.6),
       'leaflight':mat('Sunlit foliage',(.22,.36,.08),.6),
       'soil':mat('Potting soil',(.055,.034,.018),1),
       'terracotta':mat('Terracotta',(.57,.25,.13),.65),
       'kettle':mat('Sage enamel kettle',(.35,.52,.43),.24,.3),
       'linen':mat('Oat linen',(.73,.68,.53),.95),
       'fruit':mat('Golden citrus',(.92,.51,.055),.48),
       'apple':mat('Soft red apple',(.62,.105,.055),.4),
       'door':mat('Door taupe',(.48,.47,.41),.55),
       'black':mat('Rubber',(.025,.03,.026),.65)
    }
    # Floorboards, long direction Y, restrained groove contrast.
    for ix in range(20):
        x=-2.85+ix*.30
        for iy in range(3):
            y=-3.55+iy*2.12+(1.06 if ix%2 else 0)
            cube('oak plank',(x,y,-.045),(.297,2.115,.08),M['floor'],.003)
    cube('back wall',(0,2.53,1.6),(6.2,.16,3.2),M['wall'],.005)
    cube('left wall',(-3.07,-.5,1.6),(.14,6.1,3.2),M['wall'],.005)
    cube('right wall front',(3.07,-1.9,1.6),(.14,3.3,3.2),M['wall'],.005)
    cube('right wall rear',(3.07,2.0,1.6),(.14,.9,3.2),M['wall'],.005)
    cube('right wall above door',(3.07,.8,2.75),(.14,1.5,.9),M['wall'],.005)
    for loc,sz in [((0,2.425,.08),(6,.045,.16)),((-2.975,-.5,.08),(.045,6,.16))]:cube('baseboard',loc,sz,M['trim'],.006)

    # Tiled backsplash with true narrow grout lines; gentle surface variation.
    tile=mat('Cream subway tiles',(.76,.77,.70),.24)
    grout=mat('Warm tile grout',(.54,.54,.48),.8)
    cube('backsplash grout',(0,2.422,1.23),(5.8,.027,.62),grout,.002)
    for row in range(4):
        for col in range(19):
            x=-2.9+col*.32+(row%2)*.16
            if x>2.9:continue
            cube('subway tile',(x,2.397,1.004+row*.154),(.313,.024,.147),tile,.006)

    # Lower cabinets, continuous oak counter with a sink cutout.
    cabinet(-2.42,.95,True);cabinet(-1.35,1.16);cabinet(-.27,.95,True);cabinet(.66,.84)
    cabinet(2.39,.94,True)
    # Countertop segments leave a real inset sink instead of a solid block.
    cube('countertop left',(-2.40,2.035,.905),(.99,.82,.065),M['wood'],.025)
    cube('countertop right',(.96,2.035,.905),(3.84,.82,.065),M['wood'],.025)
    cube('sink counter front',(-1.40,1.735,.905),(1.02,.22,.065),M['wood'],.018)
    cube('sink counter back',(-1.40,2.345,.905),(1.02,.20,.065),M['wood'],.018)
    # Undermount sink bowl walls and dark basin.
    cube('sink basin',(-1.4,2.025,.79),(.82,.45,.06),M['chrome'],.06)
    for x in [-1.83,-.97]:cube('sink side',(x,2.025,.85),(.045,.48,.17),M['chrome'],.015)
    for y in [1.78,2.27]:cube('sink edge',(-1.4,y,.87),(.91,.045,.13),M['chrome'],.015)
    cyl('sink drain',(-1.4,2.025,.825),.035,.004,M['black'])
    curve('gooseneck faucet',[(-1.4,2.34,.94),(-1.4,2.34,1.22),(-1.4,2.18,1.33),(-1.4,2.02,1.20)],.021,M['chrome'])
    cyl('tap base',(-1.4,2.34,.965),.045,.04,M['chrome'])
    curve('tap lever',[(-1.30,2.34,.96),(-1.27,2.34,1.03),(-1.25,2.34,1.08)],.013,M['chrome'])

    # Oven and hob.
    cube('oven body',(1.48,2.07,.44),(.86,.69,.86),M['chrome'],.025)
    cube('oven black fascia',(1.48,1.706,.72),(.80,.035,.18),M['stove'],.012)
    cube('oven glazed door',(1.48,1.688,.37),(.72,.043,.48),M['glass'],.018)
    handle('oven wide handle',1.48,1.63,.62,.59)
    for x in [1.22,1.40,1.59,1.77]:cyl('oven knob',(x,1.663,.75),.036,.037,M['chrome'],rotation=(math.pi/2,0,0))
    cube('hob',(1.48,2.035,.95),(.85,.70,.035),M['stove'],.013)
    for x in [1.27,1.69]:
        for y in [1.86,2.20]:
            cyl('hob burner',(x,y,.976),.10,.012,M['black'])
            torus('burner ring',(x,y,.985),.075,.008,M['chrome'])
            for a in [0,math.pi/2]:
                o=cube('hob pan support',(x,y,1.003),(.24,.016,.019),M['stove'],.005);o.rotation_euler[2]=a
    # Rounded little kettle and arched handle.
    uv('kettle body',(1.70,2.20,1.115),(.13,.13,.135),M['kettle'])
    cyl('kettle lid',(1.70,2.20,1.24),.085,.018,M['kettle'])
    uv('kettle lid knob',(1.70,2.20,1.268),(.025,.025,.02),M['black'])
    curve('kettle handle',[(1.55,2.20,1.15),(1.54,2.20,1.38),(1.84,2.20,1.38),(1.85,2.20,1.15)],.020,M['black'])
    curve('kettle spout',[(1.61,2.10,1.10),(1.54,2.01,1.17),(1.52,1.98,1.23)],.035,M['kettle'])

    # Sunlit sash window left of centre. Bright exterior is geometry beyond glass.
    frame=M['trim']; wx=-1.45; wy=2.33; wz=2.01; ww=2.55; wh=1.68
    sky=mat('Daylight beyond window',(.71,.84,.91),1)
    p=sky.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.65,.79,.88,1);p.inputs['Emission Strength'].default_value=.65
    cube('daylight view',(wx,2.405,wz),(ww,.014,wh),sky,0)
    # A few softly colored out-of-focus town forms and trees behind the window.
    for x,z,w,h in [(-2.4,1.7,.34,.65),(-1.87,1.6,.41,.45),(-.58,1.55,.47,.46),(-.2,1.7,.4,.60)]:
        cube('distant house',(x,2.386,z),(w,.014,h),M['ceramic'],.01)
        roof=cube('distant roof',(x,2.372,z+h*.50),(w*.78,.02,.13),M['terracotta'],.01);roof.rotation_euler[1]=math.radians(17)
    for x,z in [(-2.63,1.7),(-1.0,1.65),(-.35,1.5)]:
        uv('distant treetop',(x,2.35,z),(.18,.016,.35),M['leaflight'])
    for x in [wx-ww/2,wx+ww/2]:cube('window jamb',(x,wy,wz),(.07,.14,wh+.1),frame,.009)
    for z in [wz-wh/2,wz+wh/2]:cube('window rail',(wx,wy,z),(ww+.1,.14,.075),frame,.009)
    cube('window middle mullion',(wx,wy-.01,wz),(.044,.15,wh),frame,.005)
    cube('window middle rail',(wx,wy-.01,wz),(ww,.15,.047),frame,.005)
    cube('window sill',(wx,2.22,1.14),(ww+.18,.40,.08),frame,.014)
    plant('window herb',(-2.40,2.19,1.19),.65)
    # Pale loosely gathered curtain panels, lightly corrugated.
    for xbase in [-2.91,-.02]:
        for i in range(7):
            x=xbase+(i-3)*.025
            cube('linen curtain pleat',(x,2.16+(i%2)*.012,2.0),(.037,.028,1.72),M['linen'],.012)
    curve('curtain rail',[(-3.0,2.16,2.94),(.10,2.16,2.94)],.014,M['brass'])

    # Upper cupboards and stainless range hood on right side.
    for x,w in [(.58,.72),(2.44,.84)]:
        cube('upper cabinet box',(x,2.23,2.16),(w,.40,1.02),M['trim'],.014)
        cube('upper shaker frame',(x,2.007,2.16),(w-.022,.035,.99),M['trim'],.008)
        cube('upper shaker inset',(x,1.985,2.16),(w-.13,.016,.85),M['wall'],.006)
        handle('upper cabinet handle',x,1.956,1.77,.12)
    cube('hood chimney',(1.48,2.27,2.65),(.38,.33,.69),M['chrome'],.01)
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=.68,radius2=.27,depth=.32,location=(1.48,2.15,2.23),rotation=(0,0,math.pi/4))
    o=relink(bpy.context.object);o.name='Env_Range hood';o.scale.y=.65;o.data.materials.append(M['chrome'])
    cube('hood lip',(1.48,2.15,2.055),(.99,.66,.04),M['chrome'],.013)

    # Counter still life: utensils, chopping boards, ceramic bowl, fruit, mug.
    board=cube('oak cutting board',(.10,2.36,1.19),(.32,.045,.45),M['wood'],.045);board.rotation_euler[0]=math.radians(8)
    cyl('board handle',(.10,2.31,1.45),.038,.10,M['wood'])
    cyl('utensil crock',(.40,2.15,1.05),.083,.25,M['ceramic'])
    for i in range(5):
        x=.36+i*.021;y=2.15+(i%2)*.025
        curve('wood spoon handle',[(x,y,1.08),(x+(i-2)*.018,y,1.46)],.009,M['wood'])
        uv('spoon bowl',(x+(i-2)*.018,y,1.48),(.023,.011,.042),M['wood'])
    uv('fruit bowl',(-2.43,1.98,1.01),(.24,.18,.075),M['ceramic'])
    for i,(x,y) in enumerate([(-2.52,1.94),(-2.35,2.01),(-2.44,2.07)]):uv('fresh fruit',(x,y,1.085),(.065,.065,.067),M['fruit'] if i%2 else M['apple'])
    cyl('ceramic cup',(-.46,2.10,1.02),.066,.16,M['ceramic'])
    torus('cup handle',(-.38,2.10,1.03),.047,.013,M['ceramic'],(math.pi/2,0,0))
    plant('counter plant',(2.55,2.08,.94),.88)
    # Hand towel on oven side.
    towel=cube('hanging linen towel',(1.21,1.63,.47),(.22,.025,.36),M['linen'],.006)
    for xx in [1.14,1.19,1.24,1.29]:cube('towel woven stripe',(xx,1.614,.45),(.009,.002,.29),M['sage_panel'],.001)

    # Entry door in right wall. Pivot is animatable around Z.
    hinge=bpy.data.objects.new('Env_DoorPivot',None);COL.objects.link(hinge);hinge.location=(2.97,1.35,0)
    door=cube('entry door',(2.96,.80,1.10),(.075,1.06,2.20),M['door'],.015)
    for z in [.64,1.58]:
        panel=cube('door inset',(2.912,.80,z),(.018,.82,.78),M['wall'],.009)
        panel.parent=hinge;panel.matrix_parent_inverse=hinge.matrix_world.inverted()
    for y in [.24,1.36]:cube('door casing',(2.91,y,1.13),(.09,.075,2.32),M['trim'],.008)
    cube('door casing header',(2.91,.80,2.28),(.09,1.22,.075),M['trim'],.008)
    knob=cyl('door rosette',(2.90,.37,1.03),.035,.035,M['brass'],rotation=(0,math.pi/2,0))
    lever=curve('door lever',[(2.868,.37,1.03),(2.85,.37,1.03),(2.85,.24,1.03)],.014,M['brass'])
    for ob in [door,knob,lever]:ob.parent=hinge;ob.matrix_parent_inverse=hinge.matrix_world.inverted()

    # Small travel prep table. Its near corner is beyond the character staging area.
    cube('travel table top',(1.34,-.20,.85),(1.08,.79,.065),M['wood'],.032)
    for x in [.91,1.77]:
        for y in [-.48,.08]:
            leg=cube('travel table leg',(x,y,.41),(.065,.065,.82),M['wood'],.013)
    cube('table apron front',(1.34,-.55,.745),(.99,.045,.14),M['wood'],.01)

    # Small wall art by the door and restrained pendant lamp.
    cube('wall print frame',(2.91,1.88,1.67),(.06,.40,.53),M['wood'],.012)
    cube('wall print paper',(2.87,1.88,1.67),(.009,.34,.47),M['trim'],.001)
    uv('print sun',(2.86,1.88,1.74),(.006,.085,.085),M['terracotta'])
    curve('pendant cable',[(.15,.60,3.08),(.15,.60,2.68)],.009,M['black'])
    bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.24,radius2=.09,depth=.20,location=(.15,.60,2.58))
    ob=relink(bpy.context.object);ob.name='Env_Pendant shade';ob.data.materials.append(M['sage'])
    uv('pendant glow',(.15,.60,2.49),(.075,.075,.035),M['trim'])

    # Large, soft lights make the scene readable without expensive GI.
    area('Key daylight',(-3.0,-.6,4.4),650,4.5,(1.0,.88,.72),(0,1,1))
    area('Front fill',(1.0,-4.0,3.4),340,4.0,(.82,.90,1.0),(0,.6,1.2))
    area('Window bounce',(-1.5,2.0,2.7),180,2.1,(1.0,.91,.77),(0,0,1))
    world=bpy.context.scene.world
    if world is None:world=bpy.data.worlds.new('Env_World');bpy.context.scene.world=world
    world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.60,.70,.82,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.35
    return COL

def preview():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    build_environment();sc=bpy.context.scene
    camd=bpy.data.cameras.new('Env_PreviewCamera');cam=bpy.data.objects.new('Env_PreviewCamera',camd);COL.objects.link(cam)
    cam.location=(.25,-5.4,1.8);target=Vector((0,1.1,1.40));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    camd.lens=29;sc.camera=cam
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16;sc.cycles.use_denoising=False;sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.filepath=str(Path(__file__).with_name('preview.png'))
    sc.render.film_transparent=False;sc.view_settings.view_transform='AgX'
    sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.5
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).with_name('environment.blend')))
    bpy.ops.render.render(write_still=True)

if __name__=='__main__':preview()
