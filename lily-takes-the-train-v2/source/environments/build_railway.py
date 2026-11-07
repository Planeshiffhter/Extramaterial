from pathlib import Path
"""Lily V2: detailed small-town station, platform and regional train.

Blender 4.3, metres, no add-ons or downloaded assets.  All objects are nested
under Rail_Set.  The home scene is never touched.  See STAGING and CAMERAS.
"""
import bpy, math, random
from mathutils import Vector

ROOT = None
COL = None
M = {}
COLLECTIONS = {}
FONT = None

STAGING = {
    'platform_talking': (0, 0, 0),
    'checking_departures': (-1.6, -.45, 0),
    'station_exterior': (-7.3, -4.8, -.01),
    'concourse': (-7.0, -1.6, 0),
    'boarding': (2.4, 2.05, 0),
    'door_threshold': (2.4, 3.05, .50),
    'interior_seat': (-.40, 4.98, 1.01),
}
CAMERAS = {
    'exterior_wide': {'location': (-1.2, -12.7, 3.25), 'target': (-6.9, -.8, 1.6), 'lens': 37},
    'platform_wide': {'location': (8.9, -6.5, 2.65), 'target': (1.0, 2.45, 1.50), 'lens': 36},
    'platform_medium': {'location': (0, -3.8, 1.55), 'target': (0, .35, 1.35), 'lens': 49},
    'departures': {'location': (-1.8, -4.4, 2.80), 'target': (-1.8, .57, 2.80), 'lens': 46},
    'concourse': {'location': (-7.0, -3.00, 1.65), 'target': (-7.0, .55, 1.7), 'lens': 29},
    'boarding': {'location': (5.5, -.5, 1.8), 'target': (2.4, 3.0, 1.42), 'lens': 43},
    'train_interior': {'location': (1.35, 3.63, 1.9), 'target': (-.45, 4.95, 1.45), 'lens': 27},
    'window_close': {'location': (-1.80, 3.75, 1.78), 'target': (-.4, 4.98, 1.55), 'lens': 40},
    'greenfield_town': {'location': (1.0, 9.7, 2.20), 'target': (.4, 15.0, 2.55), 'lens': 31},
}

def link(ob, name):
    ob.name = 'Rail_' + name
    for c in list(ob.users_collection): c.objects.unlink(ob)
    COL.objects.link(ob)
    return ob

def collection(name):
    global COL
    c=bpy.data.collections.new('Rail_'+name);ROOT.children.link(c);COL=c;COLLECTIONS[name]=c;return c

def material(name,color,rough=.5,metal=0,noise=0):
    m=bpy.data.materials.new('Rail_'+name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if noise:
        n=m.node_tree.nodes; l=m.node_tree.links
        tc=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=85;tex.inputs['Detail'].default_value=2
        l.new(tc.outputs['Generated'],tex.inputs['Vector'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=noise;bump.inputs['Distance'].default_value=.009
        l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return m

def stone_tiles(name,c1,c2,width=.60,height=.40):
    m=material(name,c1,.73);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    tc=n.new('ShaderNodeTexCoord');brick=n.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1
    brick.inputs['Color1'].default_value=(*c1,1);brick.inputs['Color2'].default_value=(*c2,1)
    brick.inputs['Mortar'].default_value=(.20,.19,.16,1);brick.inputs['Mortar Size'].default_value=.009
    brick.inputs['Brick Width'].default_value=width;brick.inputs['Row Height'].default_value=height
    l.new(tc.outputs['Object'],brick.inputs['Vector']);l.new(brick.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.013
    l.new(brick.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal']);return m

def glass(name,color,alpha=.18):
    m=material(name,color,.15,.1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=alpha
    p.inputs['IOR'].default_value=1.45;m.diffuse_color=(*color,alpha)
    if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
    return m

def cube(name,loc,size,mat,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=link(bpy.context.object,name);o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if mat:o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Manufactured rounded edges','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def cyl(name,loc,radius,depth,mat,rot=(0,0,0),verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc,rotation=rot)
    o=link(bpy.context.object,name);o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    b=o.modifiers.new('Rim bevel','BEVEL');b.width=min(.012,radius*.08);b.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def sphere(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=loc)
    o=link(bpy.context.object,name);o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def line(name,pts,radius,mat):
    cu=bpy.data.curves.new('Rail_'+name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    ob=bpy.data.objects.new('Rail_'+name,cu);COL.objects.link(ob);cu.materials.append(mat);return ob

def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new('Rail_'+name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new('Rail_'+name,me);COL.objects.link(ob);me.materials.append(mat);return ob

def text(name,string,loc,size,mat,align='LEFT',rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new('Rail_'+name,'FONT');cu.body=string;cu.size=size;cu.align_x=align;cu.extrude=.0007;cu.bevel_depth=.0003
    if FONT:cu.font=FONT
    ob=bpy.data.objects.new('Rail_'+name,cu);COL.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;cu.materials.append(mat);return ob

def empty(name,loc=(0,0,0)):
    o=bpy.data.objects.new('Rail_'+name,None);COL.objects.link(o);o.location=loc;return o

def parent_keep(ob,parent):
    world=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=world

def planter(name,loc,size=.55):
    x,y,z=loc
    cube(name+' stone planter',(x,y,z+size*.36),(size,size,size*.72),M['planter'],.045)
    cube(name+' soil',(x,y,z+size*.73),(size*.83,size*.83,.028),M['earth'],.01)
    for i in range(9):
        a=i*2.4;r=size*(.16+.05*(i%3))
        sphere(name+' foliage',(x+math.cos(a)*r,y+math.sin(a)*r,z+size*(1.00+.08*(i%3))),
               (size*.23,size*.22,size*.33),M['leaf2'] if i%3 else M['leaf'])
    for i in range(5):
        a=i*1.256
        sphere(name+' small bloom',(x+math.cos(a)*size*.28,y+math.sin(a)*size*.28,z+size*1.3),(.035,.035,.025),M['flower'])

def bench(name,loc,length=1.9,rot=0):
    x,y,z=loc;group=empty(name+' root',loc)
    pieces=[]
    for j in range(5):pieces.append(cube(name+' seat slat',(x,y-.22+j*.105,z+.47),(length,.085,.06),M['wood'],.015))
    for j in range(4):pieces.append(cube(name+' back slat',(x,y+.30,z+.64+j*.115),(length,.045,.085),M['wood'],.012))
    for xx in [x-length*.40,x+length*.40]:
        pieces.append(line(name+' iron foot',[(xx,y-.28,z+.025),(xx,y-.20,z+.46),(xx,y+.27,z+.46),(xx,y+.33,z+1.02)],.027,M['iron']))
        pieces.append(line(name+' armrest',[(xx,y-.22,z+.47),(xx,y-.22,z+.70),(xx,y+.26,z+.70)],.023,M['iron']))
    bpy.context.view_layer.update()
    for ob in pieces:parent_keep(ob,group)
    group.rotation_euler[2]=rot;return group

def board(name,loc,width=3.5):
    x,y,z=loc;h=1.0
    cube(name+' case',(x,y,z),(width,.13,h),M['iron'],.045)
    cube(name+' screen',(x,y-.075,z),(width-.10,.012,h-.09),M['screen'],.012)
    text(name+' header','DEPARTURES',(x-width/2+.16,y-.087,z+.30),.135,M['muted'])
    text(name+' platform','PLATFORM 2',(x+width/2-.14,y-.087,z+.30),.105,M['white'],'RIGHT')
    cube(name+' divider',(x,y-.09,z+.17),(width-.30,.006,.009),M['muted'],0)
    text(name+' time','10:30',(x-width/2+.16,y-.09,z-.10),.225,M['amber'])
    text(name+' destination','GREENFIELD',(x-width/2+1.05,y-.09,z-.09),.165,M['white'])
    text(name+' on time','On time',(x+width/2-.16,y-.09,z-.10),.135,M['greenlight'],'RIGHT')
    text(name+' service','Direct service  /  Regional train',(x-width/2+.16,y-.09,z-.34),.105,M['muted'])

def clock(name,loc,r=.38):
    x,y,z=loc
    cyl(name+' housing',loc,r,.10,M['iron'],(math.pi/2,0,0),64)
    cyl(name+' face',(x,y-.056,z),r*.91,.012,M['white'],(math.pi/2,0,0),64)
    for i in range(12):
        a=i*math.tau/12
        ob=cube(name+' mark',(x+math.sin(a)*r*.76,y-.067,z+math.cos(a)*r*.76),(.018,.009,.05),M['ink'],.002)
        ob.rotation_euler[1]=a
    # 9:00, keeping the morning time stated in the script.
    cube(name+' hour hand',(x-r*.22,y-.080,z),(r*.45,.012,.022),M['ink'],.006)
    cube(name+' minute hand',(x,y-.084,z+r*.29),(.016,.012,r*.59),M['ink'],.004)
    cyl(name+' pin',(x,y-.095,z),.023,.012,M['brass'],(math.pi/2,0,0),20)

def build_architecture():
    collection('Architecture')
    # An open, glazed little station concourse with genuine wall openings.
    cube('concourse foundation',(-8,-1.4,-.11),(8.4,4.6,.20),M['stone'],.035)
    cube('concourse floor',(-8,-1.4,-.01),(8.08,4.24,.06),M['tiles_inside'],.012)
    cube('rear wall left',(-10.95,.79,1.6),(2.15,.20,3.2),M['plaster'],.035)
    cube('rear wall middle',(-7.75,.79,1.6),(3.90,.20,3.2),M['plaster'],.035)
    cube('rear wall right',(-4.35,.79,1.6),(.70,.20,3.2),M['plaster'],.035)
    cube('platform exit lintel',(-5.12,.79,2.91),(.86,.20,.58),M['plaster'],.025)
    cube('left side wall',(-12.05,-1.40,1.6),(.20,4.4,3.2),M['plaster'],.025)
    cube('front facade stone base',(-8,-3.58,.32),(8.2,.23,.64),M['stone'],.025)
    # Facade piers between clear glazed bays and a central entrance.
    for x,w in [(-12,.28),(-10.2,.25),(-8.95,.23),(-7.05,.23),(-5.8,.25),(-4,.28)]:
        cube('facade pier',(x,-3.58,1.63),(w,.28,2.07),M['plaster'],.025)
        cube('pier stone cap',(x,-3.58,.75),(w+.12,.37,.13),M['stone'],.02)
    for x,w in [(-11.1,1.48),(-9.58,1.04),(-6.42,1.04),(-4.90,1.48)]:
        cube('concourse glass',(x,-3.56,1.68),(w,.016,1.82),M['clear_glass'],.003)
        for xx in [x-w/2,x+w/2]:cube('window brass upright',(xx,-3.61,1.68),(.035,.05,1.87),M['iron'],.005)
        for zz in [.77,2.59]:cube('window brass rail',(x,-3.61,zz),(w,.05,.035),M['iron'],.005)
    # Glass entry doors.
    for x in [-8.46,-7.54]:
        cube('entry door glass',(x,-3.58,1.28),(.84,.018,2.45),M['clear_glass'],.006)
        for xx in [x-.43,x+.43]:cube('entry door stile',(xx,-3.61,1.28),(.04,.065,2.51),M['iron'],.007)
        for zz in [.04,2.53]:cube('entry door rail',(x,-3.61,zz),(.89,.065,.04),M['iron'],.005)
        line('entry pull handle',[(x+.25,-3.67,.95),(x+.25,-3.70,1.35)],.014,M['brass'])
    cube('facade upper frieze',(-8,-3.58,2.93),(8.3,.28,.56),M['plaster'],.025)
    cube('facade name plate',(-8,-3.745,2.95),(4.7,.08,.42),M['iron'],.025)
    text('station name','RIVERSIDE  STATION',(-8,-3.792,2.86),.245,M['white'],'CENTER')
    cube('building cornice',(-8,-1.4,3.26),(8.45,4.65,.17),M['stone'],.03)
    cube('concourse ivory ceiling',(-8,-1.4,3.16),(8.05,4.20,.075),M['interior_white'],.025)
    for x in [-11.3,-8,-4.7]:cube('concourse ceiling timber',(x,-1.4,3.09),(.12,4.12,.12),M['wood'],.015)
    # Hipped slate roof, with a subtle ridge and copper drain line.
    verts=[(-12.35,-3.88,3.34),(-3.65,-3.88,3.34),(-3.65,1.08,3.34),(-12.35,1.08,3.34),
           (-11.2,-1.40,4.18),(-4.8,-1.40,4.18)]
    mesh('slate hipped roof',verts,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)],M['slate'])
    line('roof ridge',[(-11.25,-1.40,4.2),(-4.75,-1.40,4.2)],.045,M['iron'])
    for y in [-3.9,1.1]:line('roof gutter',[(-12.35,y,3.30),(-3.65,y,3.30)],.045,M['iron'])
    line('rain downpipe',[(-11.90,-3.80,3.30),(-11.90,-3.80,.15),(-11.7,-3.90,.05)],.036,M['iron'])
    # Exterior clock on a bracket, projecting into the forecourt.
    clock('exterior clock',(-4.42,-3.77,2.35),.36)
    # Concourse ticket desk and warm timber details.
    cube('ticket desk timber',(-10.45,-.05,.52),(2.0,.73,1.04),M['wood'],.045)
    cube('ticket desk stone top',(-10.45,-.05,1.07),(2.15,.85,.08),M['stone'],.025)
    cube('ticket window frame',(-10.45,.38,1.91),(2.1,.08,1.40),M['iron'],.02)
    cube('ticket window glass',(-10.45,.32,1.92),(1.91,.014,1.20),M['clear_glass'],.01)
    text('tickets label','TICKETS',(-10.45,.262,2.34),.17,M['white'],'CENTER')
    text('ticket service label','Good morning. How can we help?',(-10.45,-.43,.78),.085,M['ink'],'CENTER')
    # Back wall departures and platform wayfinding.
    board('concourse departures',(-7.5,.655,2.21),3.9)
    text('platform exit label','PLATFORM 2  →',(-5.12,.651,2.73),.12,M['iron'],'CENTER')
    bench('concourse bench',(-7.6,-.32,0),2.1)
    planter('concourse fern',(-4.62,-2.95,0),.47)
    # Notice board with layered travel posters, more visual texture than flat walls.
    cube('noticeboard frame',(-11.92,-1.48,1.76),(.08,1.50,1.08),M['wood'],.02)
    cube('noticeboard cork',(-11.87,-1.48,1.76),(.012,1.38,.95),M['cork'],.005)
    for yy,zz in [(-1.83,1.90),(-1.35,1.86),(-1.60,1.48)]:
        cube('notice paper',(-11.85,yy,zz),(.009,.39,.36),M['paper'],.003)

def build_platform():
    collection('Platform')
    cube('platform stone mass',(0,-.40,-.25),(34,6.4,.50),M['stone'],.035)
    cube('platform paving',(0,-.42,.005),(33.9,6.37,.045),M['tiles'],.004)
    cube('platform coping',(0,2.72,.055),(34,.24,.12),M['edge'],.014)
    cube('yellow safety strip',(0,2.43,.034),(33.8,.19,.013),M['yellow'],.003)
    # Tactile bumps in long repeated rails: visible close up, inexpensive geometry.
    for y in [2.33,2.39,2.45,2.51]:
        for x in range(-16,17):
            cube('tactile raised dash',(x,y,.046),(.32,.022,.012),M['yellow'],.006)
    # Canopy: stepped column bases, cast-iron posts, decorative arched brackets.
    for x in [-13,-8,-3,3,8,13]:
        cube('canopy column stone foot',(x,.62,.10),(.34,.34,.20),M['stone'],.025)
        cube('canopy column iron base',(x,.62,.28),(.19,.19,.20),M['iron'],.02)
        cyl('canopy fluted column',(x,.62,1.88),.067,3.1,M['iron'])
        cyl('canopy column collar',(x,.62,3.27),.106,.10,M['brass'])
        cube('canopy cross beam',(x,.75,3.44),(.14,3.70,.17),M['iron'],.018)
        for sign in [-1,1]:
            line('curved cast bracket',[(x,.62,2.68),(x,.62+sign*.26,3.05),(x,.62+sign*1.15,3.35)],.038,M['iron'])
            line('bracket scroll',[(x,.62+sign*.20,3.12),(x,.62+sign*.43,3.13),(x,.62+sign*.48,2.99),(x,.62+sign*.34,2.94)],.016,M['iron'])
    for y in [-1.05,2.52]:cube('canopy long fascia',(0,y,3.57),(29,.13,.27),M['iron'],.025)
    cube('canopy roof',(0,.74,3.70),(29.3,3.85,.14),M['slate'],.025)
    for x in range(-14,15,2):cube('canopy rafter',(x,.74,3.57),(.07,3.75,.10),M['iron'],.008)
    for x in [-10,-5,0,5,10]:
        cube('canopy ceiling light',(x,.7,3.41),(1.22,.18,.045),M['lightglass'],.025)
    # Main departures board leaves the character's face clear below it.
    board('platform departures',(-1.8,.57,2.80),3.65)
    for xx in [-3.1,-.5]:line('board suspension',[(xx,.57,3.34),(xx,.57,3.58)],.018,M['iron'])
    # Platform identification with a large clock.
    for x in [6.2,-11.0]:
        cube('platform sign pole',(x,1.42,1.42),(.055,.055,2.84),M['iron'],.009)
        cube('platform sign plaque',(x,1.42,2.74),(2.20,.10,.49),M['iron'],.02)
        text('destination sign','TO GREENFIELD',(x,1.359,2.67),.165,M['white'],'CENTER')
        cube('platform number',(x-1.20,1.42,2.74),(.40,.11,.49),M['iron'],.015)
        text('platform number text','2',(x-1.2,1.353,2.62),.28,M['white'],'CENTER')
    clock('platform clock',(3.0,.49,2.74),.28)
    for loc in [(-5.3,1.42,0),(10.3,1.35,0)]:bench('platform bench',loc,2.25)
    for loc in [(-3.7,1.5,0),(8.9,1.4,0),(-13.8,-.5,0)]:planter('platform flowers',loc,.58)
    # Travel poster with picture-like mountain forms.
    cube('travel poster stand',(-5.5,-1.05,.91),(.78,.09,1.78),M['iron'],.018)
    cube('travel poster paper',(-5.5,-1.107,1.03),(.66,.006,1.36),M['paper'],.002)
    text('travel poster title','GREENFIELD',(-5.5,-1.113,1.52),.084,M['iron'],'CENTER')
    text('travel poster tagline','A little closer to home',(-5.5,-1.113,.51),.044,M['iron'],'CENTER')
    mesh('poster hills',[(-5.81,-1.115,.70),(-5.81,-1.115,1.0),(-5.58,-1.115,1.21),(-5.39,-1.115,.95),(-5.17,-1.115,1.15),(-5.17,-1.115,.70)],[(0,1,2,3,4,5)],M['leaf2'])
    # Rubbish bin and brass rim, shaded rather than brightly colored.
    cyl('platform bin',(-9.6,.94,.47),.23,.94,M['iron'],verts=40)
    cyl('bin lid',(-9.6,.94,.96),.25,.065,M['chrome'],verts=40)
    cube('bin slot',(-9.6,.709,.78),(.30,.012,.11),M['ink'],.018)

def build_tracks():
    collection('Tracks')
    cube('ballast bed',(0,4.26,-.42),(42,3.1,.27),M['ballast'],.04)
    for x in range(-21,22):
        cube('timber sleeper',(x*.96,4.2,-.24),(.24,2.18,.14),M['sleeper'],.022)
    for y in [3.48,4.92]:
        cube('rail foot',(0,y,-.145),(42,.14,.035),M['steel'],.008)
        cube('rail web',(0,y,-.09),(42,.055,.095),M['steel'],.006)
        cube('polished rail head',(0,y,-.032),(42,.09,.045),M['chrome'],.011)
    # Second track beyond adds real station depth.
    cube('far ballast bed',(0,8.5,-.44),(42,3.1,.24),M['ballast'],.02)
    for x in range(-20,21):cube('far sleeper',(x,8.5,-.26),(.22,2.18,.12),M['sleeper'],.015)
    for y in [7.78,9.22]:cube('far rail',(0,y,-.12),(42,.09,.12),M['steel'],.008)

def train_side(y,near=True):
    windows=[(-7.1,-5.9),(-5.1,-3.9),(-3.1,-1.9),(-1.1,.1),(4.2,5.7),(6.1,7.3)]
    door=(1.7,3.1)
    holes=sorted(windows+[door]);start=-7.75
    # Lower body genuinely omits the open doorway.
    for a,b in [(-7.75,door[0]),(door[1],7.75)]:
        cube('train lower body',((a+b)/2,y,.85),(b-a,.105,.70),M['train_body'],.035)
        cube('train teal belt',((a+b)/2,y+(-.058 if near else .058),.91),(b-a,.014,.20),M['train_teal'],.005)
    cube('train upper window rail',(0,y,2.55),(15.5,.11,.42),M['train_body'],.035)
    for a,b in holes+[(7.75,7.75)]:
        if a>start:
            cube('train window pillar',((start+a)/2,y,1.77),(a-start,.11,1.19),M['train_body'],.035)
        start=b
    for a,b in windows:
        x=(a+b)/2;w=b-a
        # Fine dark rubber gasket and a slightly recessed transparent pane.
        for xx in [a,b]:cube('window vertical gasket',(xx,y,1.77),(.045,.14,1.16),M['rubber'],.014)
        for z in [1.20,2.34]:cube('window horizontal gasket',(x,y,z),(w,.14,.045),M['rubber'],.014)
        cube('train window',(x,y,1.77),(w-.055,.012,1.10),M['train_glass'],.016)
        cube('window lower bright trim',(x,y+(-.076 if near else .076),1.18),(w+.04,.02,.035),M['chrome'],.008)
    # Sliding leaves are parked against their side pockets: a true open aperture.
    for side,xc in [('L',1.39),('R',3.41)]:
        pivot=empty('TrainDoor_'+side+(('_far') if not near else ''),(xc,y,.5))
        leaf=cube('sliding door '+side,(xc,y-(.04 if near else -.04),1.48),(.70,.10,1.95),M['train_teal'],.035)
        pane=cube('door window '+side,(xc,y-(.098 if near else -.098),1.81),(.44,.009,.78),M['train_glass'],.025)
        pull=cube('door edge '+side,(xc+(.30 if side=='L' else -.30),y-(.105 if near else -.105),1.44),(.018,.018,1.75),M['chrome'],.004)
        bpy.context.view_layer.update()
        for ob in [leaf,pane,pull]:parent_keep(ob,pivot)

def build_train():
    collection('Train')
    train_root=empty('TrainRoot')
    before=set(COL.objects)
    # Underframe and slightly convex manufactured body components.
    cube('train dark underframe',(0,4.2,.37),(16.1,2.28,.27),M['undercarriage'],.09)
    cube('train floor',(0,4.2,.51),(15.6,2.34,.12),M['interior_floor'],.035)
    train_side(2.98,True);train_side(5.42,False)
    # Arched roof: actual curved cross-section extruded along the train.
    section=[(2.94,2.71),(2.98,2.86),(3.16,3.00),(3.54,3.10),(4.20,3.15),(4.86,3.10),(5.24,3.00),(5.42,2.86),(5.46,2.71)]
    verts=[(x,y,z) for x in [-7.85,7.85] for y,z in section]
    faces=[(i,i+1,i+1+len(section),i+len(section)) for i in range(len(section)-1)]
    roof=mesh('train curved roof',verts,faces,M['train_roof'])
    sol=roof.modifiers.new('Roof metal thickness','SOLIDIFY');sol.thickness=.06
    for p in roof.data.polygons:p.use_smooth=True
    for x in [-5.5,-1.6,4.6]:cube('rooftop HVAC',(x,4.2,3.22),(1.25,.98,.20),M['train_roof'],.09)
    # Cab ends with beveled panels and inset windows.
    for sign in [-1,1]:
        x=sign*7.88
        cube('cab end',(x,4.2,1.59),(.70,2.36,2.10),M['train_body'],.19)
        cube('cab windshield',(x+sign*.357,4.2,2.07),(.017,1.80,.76),M['windshield'],.07)
        cube('cab lower fascia',(x+sign*.36,4.2,.94),(.045,2.05,.29),M['train_teal'],.07)
        for y in [3.47,4.93]:
            sphere('cab headlight',(x+sign*.398,y,1.20),(.018,.15,.085),M['lightglass'])
        cube('cab coupling',(x+sign*.69,4.2,.44),(.38,.23,.17),M['undercarriage'],.03)
    # Bogies: wheels, axle, hubs, springs, and equipment boxes.
    for bx in [-5.6,5.6]:
        cube('bogie frame',(bx,4.2,.33),(2.2,1.95,.24),M['undercarriage'],.035)
        for xx in [bx-.70,bx+.70]:
            cyl('train axle',(xx,4.2,.30),.08,1.75,M['steel'],(math.pi/2,0,0))
            for yy in [3.45,4.95]:
                cyl('steel wheel',(xx,yy,.30),.33,.14,M['wheel'],(math.pi/2,0,0),40)
                cyl('wheel hub',(xx,yy-(.085 if yy<4.2 else -.085),.30),.15,.035,M['steel'],(math.pi/2,0,0),32)
                line('bogie coil spring',[(xx-.15,yy,.48),(xx+.15,yy,.49)],.045,M['steel'])
    for x in [-3.6,-.8,3.3]:cube('underfloor equipment',(x,4.2,.20),(1.45,1.25,.27),M['undercarriage'],.04)
    # Door step and yellow handrails at the open platform-side doorway.
    for y,z,depth in [(2.82,.15,.25),(2.99,.32,.26),(3.14,.49,.22)]:
        cube('boarding tread',(2.4,y,z),(1.34,depth,.055),M['steel'],.012)
        cube('tread yellow nosing',(2.4,y-depth/2-.005,z+.022),(1.32,.022,.012),M['yellow'],.003)
    for x in [1.64,3.16]:line('boarding handrail',[(x,3.20,.63),(x,3.20,2.22),(x,3.36,2.30)],.025,M['yellow'])
    # Exterior destination display faces the platform and remains readable.
    cube('train destination screen',(.35,2.907,2.58),(2.25,.025,.22),M['screen'],.012)
    text('train destination','GREENFIELD  •  10:30',(.35,2.889,2.524),.106,M['amber'],'CENTER')
    text('train regional logo','REGIONAL',(-6.0,2.909,.77),.090,M['train_teal'],'CENTER')
    bpy.context.view_layer.update()
    for ob in set(COL.objects)-before:
        if ob.parent is None:parent_keep(ob,train_root)
    # Interior is separate for camera-specific visibility and render optimization.
    collection('Interior')
    before=set(COL.objects)
    cube('interior ceiling',(0,4.2,2.80),(15.4,2.20,.08),M['interior_white'],.06)
    for y in [3.37,5.03]:
        cube('interior ceiling light',(0,y,2.74),(14.8,.10,.025),M['lightglass'],.012)
        line('overhead grab rail',[(-7.3,y,2.42),(7.3,y,2.42)],.022,M['chrome'])
    for x in [-6.5,-4.5,-2.5,-.5,4.7,6.7]:
        for y in [3.51,4.96]:
            cube('seat pedestal',(x,y,.72),(.37,.42,.29),M['steel'],.04)
            cube('padded train seat',(x,y,1.00),(.71,.68,.15),M['seat_fabric'],.085)
            back=cube('padded seat back',(x+.34,y,1.40),(.13,.69,.84),M['seat_fabric'],.085)
            back.rotation_euler[1]=math.radians(-7)
            cube('seat headrest',(x+.39,y,1.74),(.15,.60,.20),M['headrest'],.06)
            for yy in [y-.36,y+.36]:
                line('seat armrest',[(x-.27,yy,1.13),(x-.19,yy,1.25),(x+.28,yy,1.25)],.022,M['chrome'])
                cube('armrest pad',(x+.02,yy,1.26),(.34,.065,.045),M['rubber'],.02)
            # A fine contrast seam gives fabric a tailored shape.
            line('seat piping',[(x-.30,y-.28,1.07),(x-.30,y+.28,1.07),(x+.28,y+.28,1.07)],.006,M['seat_seam'])
    # Wall tables and a luggage rack frame close-up narrative actions.
    for x in [-3.5,5.7]:
        cube('window side table',(x,5.07,1.20),(.67,.61,.055),M['wood'],.045)
        cyl('table support',(x,5.07,.88),.035,.60,M['chrome'])
    for y in [3.45,4.95]:
        for z in [2.28,2.46]:line('luggage rack outer rail',[(-7.2,y,z),(7.1,y,z)],.016,M['chrome'])
        for x in range(-7,8):line('luggage rack crossbar',[(x,y-.20,2.29),(x,y+.20,2.29)],.010,M['chrome'])
    cube('interior route panel',(2.4,5.33,2.40),(1.12,.02,.23),M['interior_white'],.015)
    text('interior route text','NEXT STOP: GREENFIELD',(2.4,5.311,2.35),.069,M['ink'],'CENTER')
    bpy.context.view_layer.update()
    for ob in set(COL.objects)-before:
        if ob.parent is None:parent_keep(ob,train_root)

def build_landscape():
    collection('Landscape')
    cube('forecourt paving',(-6.5,-7,-.12),(25,6.8,.18),M['forecourt'],.02)
    cube('forecourt curb',(-6.5,-10.35,-.08),(25,.18,.22),M['stone'],.02)
    cube('station access path',(-.8,-3.9,-.06),(4.6,1.0,.13),M['forecourt'],.012)
    cube('distant grass',(0,13,-.53),(65,18,.12),M['grass'],.03)
    # Town architecture beyond the train windows: layered actual 3D forms.
    for i,(x,y,w,h) in enumerate([(-15,14,4.2,5.0),(-9.5,15.5,4.8,6.0),(-3.7,14.3,4.1,4.8),(2.0,15.4,4.5,5.6),(8.0,14.4,4.8,6.0),(14.0,16,4.3,5.0)]):
        wall=M['town1'] if i%2 else M['town2']
        cube('town house',(x,y,h/2-.4),(w,3.2,h),wall,.035)
        roofverts=[(x-w*.56,y-1.8,h-.4),(x+w*.56,y-1.8,h-.4),(x+w*.56,y+1.8,h-.4),(x-w*.56,y+1.8,h-.4),(x,y-1.8,h+.75),(x,y+1.8,h+.75)]
        mesh('town pitched roof',roofverts,[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4)],M['terracotta'])
        for xx in [x-w*.29,x+w*.29]:
            for zz in [1.3,2.8,4.2]:
                if zz<h-.5:
                    cube('town sash window',(xx,y-1.615,zz),(.71,.035,1.10),M['town_glass'],.02)
                    for dx in [-.39,.39]:cube('town window trim',(xx+dx,y-1.64,zz),(.055,.04,1.20),M['paper'],.005)
                    cube('town window sill',(xx,y-1.67,zz-.59),(.88,.11,.07),M['paper'],.008)
        cube('town front door',(x,y-1.625,.65),(.83,.045,2.15),M['iron'],.025)
        cube('town doorway lintel',(x,y-1.67,1.77),(1.01,.12,.12),M['paper'],.012)
        sphere('town brass doorknob',(x+.27,y-1.665,.61),(.035,.018,.035),M['brass'])
    # Destination-town insert can be filmed beyond the railway without showing
    # the origin's station facade or introducing a contradictory station name.
    for x in [-.2,2.2]:cube('Greenfield welcome sign post',(x,12.9,.39),(.085,.085,1.73),M['wood'],.015)
    cube('Greenfield welcome sign',(1,12.9,.99),(2.9,.13,.68),M['iron'],.045)
    text('Greenfield welcome name','GREENFIELD',(1,12.821,1.05),.27,M['white'],'CENTER')
    text('Greenfield welcome subtitle','Welcome home',(1,12.821,.80),.11,M['white'],'CENTER')
    # Forecourt planters, real tree trunks and overlapping soft leaf masses.
    for loc in [(-11,-5.0,-.02),(-4.5,-5.0,-.02)]:planter('entry flowers',loc,.73)
    rng=random.Random(21)
    for x,y,scale in [(-15,0,1.0),(14,1,1.1),(-13,10,.9),(-6,11,1.1),(5,11,.95),(12,10,1.0)]:
        cyl('tree trunk',(x,y,1.3*scale-.35),.13*scale,2.6*scale,M['bark'])
        for j in range(12):
            a=j*2.4;r=(.3+.15*(j%3))*scale
            sphere('tree leafy crown',(x+math.cos(a)*r,y+math.sin(a)*r,2.7*scale+(j%4)*.22),
                   ((.65+rng.random()*.20)*scale,(.60+rng.random()*.15)*scale,(.70+rng.random()*.3)*scale),M['leaf'] if j%3 else M['leaf2'])
    # A clipped hedge and iron station fence at the far edge.
    cube('far hedge',(0,11.5,.42),(38,.65,1.25),M['leaf'],.25)
    for x in range(-18,19):
        cyl('far fence post',(x,10.75,.45),.025,1.7,M['iron'],verts=12)
    for z in [.3,.95]:line('far fence rail',[(-19,10.75,z),(19,10.75,z)],.018,M['iron'])

def build_lighting():
    collection('Lighting')
    # Warm broad morning key, cooler sky fill, a large soft platform bounce.
    for name,loc,target,energy,size,color in [
        ('morning key',(-7,-6,10),(0,2,0),1800,7,(1,.86,.69)),
        ('platform fill',(5,-6,6),(1,1.5,1.4),1000,6,(.78,.87,1)),
        ('concourse softbox',(-7,-1.5,3.0),(-8,-.2,.5),240,4,(1,.90,.78)),
        ('train interior bounce',(0,4.2,2.60),(0,4.2,.8),220,5,(1,.92,.82))]:
        d=bpy.data.lights.new('Rail_'+name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new('Rail_'+name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.lights.new('Rail_Morning Sun','SUN');d.energy=2.0;d.angle=math.radians(11);d.color=(1,.89,.74)
    o=bpy.data.objects.new('Rail_Morning Sun',d);COL.objects.link(o);o.rotation_euler=(math.radians(26),math.radians(-20),math.radians(-35))

def build_cameras():
    collection('Cameras')
    for name,spec in CAMERAS.items():
        d=bpy.data.cameras.new('Rail_Camera_'+name);o=bpy.data.objects.new('Rail_Camera_'+name,d);COL.objects.link(o)
        o.location=spec['location'];o.rotation_euler=(Vector(spec['target'])-o.location).to_track_quat('-Z','Y').to_euler();d.lens=spec['lens']
        d.clip_start=.05;d.clip_end=200
    for name,loc in STAGING.items():empty('ActorMark_'+name,loc)

def build_station():
    """Return a dictionary of owned collections. Existing non-Rail scenes stay intact."""
    global ROOT,COL,M,FONT,COLLECTIONS
    old=bpy.data.collections.get('Rail_Set')
    if old:
        for ob in list(old.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
        for c in list(old.children_recursive):bpy.data.collections.remove(c)
        bpy.data.collections.remove(old)
    ROOT=bpy.data.collections.new('Rail_Set');bpy.context.scene.collection.children.link(ROOT);COLLECTIONS={'Root':ROOT}
    try:FONT=bpy.data.fonts.load(str(Path(__file__).with_name('DejaVuSans.ttf')),check_existing=True)
    except RuntimeError:FONT=None
    M={
      'plaster':material('Warm limestone plaster',(.66,.61,.51),.80,noise=.10),
      'stone':material('Cut limestone',(.48,.46,.39),.75,noise=.12),
      'tiles':stone_tiles('Platform stone paving',(.41,.43,.41),(.49,.49,.45),.65,.45),
      'tiles_inside':stone_tiles('Concourse sandstone',(.53,.48,.39),(.61,.56,.47),.55,.55),
      'forecourt':stone_tiles('Forecourt warm pavers',(.40,.34,.28),(.48,.41,.33),.42,.22),
      'edge':material('Pale platform edge',(.67,.66,.59),.65,noise=.1),
      'iron':material('Deep petrol cast iron',(.035,.085,.084),.32,.5,noise=.04),
      'wood':material('Oiled warm oak',(.32,.18,.075),.40,noise=.16),
      'brass':material('Aged brass details',(.42,.29,.10),.28,.8),
      'slate':material('Charcoal slate roofing',(.075,.095,.098),.66,noise=.18),
      'clear_glass':glass('Concourse clear glass',(.69,.82,.81),.12),
      'train_glass':glass('Slightly tinted train glazing',(.28,.43,.45),.15),
      'windshield':material('Cab windshield',(.027,.070,.079),.12,.45),
      'train_body':material('Regional train ivory enamel',(.68,.72,.69),.25,.28,noise=.025),
      'train_teal':material('Regional train teal enamel',(.055,.22,.22),.25,.35),
      'train_roof':material('Train roof satin grey',(.30,.36,.35),.43,.6),
      'interior_floor':material('Train rubber floor',(.17,.20,.19),.75,noise=.16),
      'interior_white':material('Interior warm white panels',(.76,.76,.69),.40),
      'seat_fabric':material('Woven deep sage upholstery',(.10,.23,.22),.87,noise=.30),
      'seat_seam':material('Seat contrasting seam',(.22,.37,.31),.85),
      'headrest':material('Headrest warm grey',(.43,.48,.45),.80,noise=.20),
      'undercarriage':material('Weathered undercarriage',(.055,.065,.062),.66,.35,noise=.16),
      'wheel':material('Wheel steel dark',(.075,.085,.080),.38,.8),
      'steel':material('Brushed metal',(.30,.34,.33),.33,.8),
      'chrome':material('Polished steel highlights',(.52,.58,.55),.20,.9),
      'rubber':material('Black rubber',(.020,.027,.025),.62),
      'yellow':material('Desaturated safety yellow',(.67,.46,.08),.52),
      'white':material('Warm lettering white',(.87,.87,.78),.4),
      'muted':material('Display secondary text',(.39,.51,.47),.6),
      'screen':material('Display screen black',(.008,.021,.020),.35),
      'amber':material('Amber LED lettering',(.88,.49,.12),.45),
      'greenlight':material('On time lettering',(.37,.71,.42),.4),
      'ink':material('Soft black ink',(.028,.040,.036),.65),
      'lightglass':material('Warm fixture diffuser',(.88,.86,.69),.25),
      'planter':material('Stone flower planter',(.43,.39,.31),.75,noise=.18),
      'earth':material('Dark earth',(.055,.039,.022),1,noise=.3),
      'leaf':material('Deep natural green',(.075,.16,.055),.74),
      'leaf2':material('Sunlit natural foliage',(.20,.30,.08),.72),
      'flower':material('Pale yellow flowers',(.80,.65,.27),.7),
      'bark':material('Tree bark',(.13,.085,.040),.9,noise=.3),
      'grass':material('Dry meadow green',(.20,.27,.11),.9,noise=.25),
      'ballast':material('Rail ballast aggregate',(.20,.21,.19),.95,noise=.6),
      'sleeper':material('Old railway sleepers',(.11,.09,.065),.88,noise=.4),
      'cork':material('Notice cork',(.40,.25,.12),.9,noise=.2),
      'paper':material('Cream paper',(.78,.75,.65),.84),
      'town1':material('Town pale ochre',(.62,.53,.38),.78,noise=.1),
      'town2':material('Town warm limestone',(.65,.63,.53),.78,noise=.1),
      'town_glass':material('Distant window blue',(.14,.25,.30),.35,.2),
      'terracotta':material('Town terracotta roofs',(.30,.14,.09),.75,noise=.16),
    }
    for key in ['amber','greenlight','lightglass']:
        p=M[key].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=M[key].diffuse_color;p.inputs['Emission Strength'].default_value=.45 if key!='lightglass' else .65
    for label,fn in [('architecture',build_architecture),('platform',build_platform),('tracks',build_tracks),
                     ('train and interior',build_train),('landscape',build_landscape),('lighting',build_lighting),('cameras',build_cameras)]:
        fn();print('RAIL_BUILD: '+label+' complete',flush=True)
    bpy.context.view_layer.update()
    return COLLECTIONS

def preview():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    build_station();sc=bpy.context.scene
    world=bpy.data.worlds.new('Rail_LookdevWorld');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.50,.65,.81,1);world.node_tree.nodes['Background'].inputs[1].default_value=.42;sc.world=world
    sc.camera=bpy.data.objects['Rail_Camera_platform_wide']
    sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16
    sc.render.resolution_x=640;sc.render.resolution_y=360;sc.render.resolution_percentage=100
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0
    sc.render.image_settings.file_format='PNG';sc.render.filepath='/workspace/work/v2/environments/station_lookdev.png'
    bpy.ops.wm.save_as_mainfile(filepath='/workspace/work/v2/environments/station.blend')
    bpy.ops.render.render(write_still=True)

if __name__=='__main__':preview()
