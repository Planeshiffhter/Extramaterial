import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parent
mesh=bpy.data.objects['Lily_Actor_Mesh']
fixed=0
for mat in mesh.data.materials:
    if not mat.use_nodes:continue
    nodes=mat.node_tree.nodes
    sweep=next((n for n in nodes if n.label=='Continuous dark front sweep'),None)
    if not sweep:continue
    # Generated coordinates avoid imported rig/object scale differences.
    mask=sweep.inputs[0].links[0].from_node
    zmap=mask.inputs[0].links[0].from_node
    assert zmap.type=='MAP_RANGE'
    xyz=zmap.inputs['Value'].links[0].from_node
    tc=xyz.inputs[0].links[0].from_node
    mat.node_tree.links.new(tc.outputs['Generated'],xyz.inputs[0])
    zmap.inputs['From Min'].default_value=.895
    zmap.inputs['From Max'].default_value=.908
    zmap.label='Dark frontal hair — normalized height'
    satmap=mask.inputs[1].links[0].from_node
    satmap.inputs['From Min'].default_value=.86
    satmap.inputs['From Max'].default_value=.94
    fixed+=1
assert fixed, 'Expected front-sweep material node missing'
path=bpy.data.filepath
bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
print('FRINGE_METRE_COORDINATES_FIXED',fixed,flush=True)
if '--preview' in sys.argv:
    scene=bpy.data.scenes['01 Home — Reference Lookdev']
    for other in list(bpy.data.scenes):
        if other!=scene:bpy.data.scenes.remove(other)
    bpy.data.orphans_purge(do_recursive=True)
    bpy.context.window.scene=scene
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False
    scene.render.resolution_x=640;scene.render.resolution_y=360
    scene.render.use_simplify=True;scene.render.simplify_subdivision_render=1
    scene.render.filepath=str(root/'previews/fringe_check.exr')
    bpy.ops.render.render(write_still=True)
