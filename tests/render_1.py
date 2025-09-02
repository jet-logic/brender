from brender import Render
from os.path import join, dirname
from os import environ


def prepare(scene):
    scene.render.resolution_percentage = 25
    # Simplify
    scene.render.use_simplify = True
    scene.render.simplify_subdivision_render = 0
    scene.render.simplify_child_particles = 0.1
    scene.render.simplify_volumes = 0.5
    scene.render.film_transparent = True
    # Disable costly effects
    scene.render.use_motion_blur = False
    # scene.eevee.use_gtao = False
    # scene.eevee.use_bloom = False
    # scene.eevee.use_ssr = False
    # Cycles (if switched manually)
    if scene.render.engine == "CYCLES":
        cycles = scene.cycles
        cycles.device = "GPU"
        cycles.samples = 32
        cycles.use_adaptive_sampling = True
        cycles.max_bounces = 3
        cycles.preview_samples = 16
        cycles.use_denoising = True
    # Simplify
    scene.render.use_simplify = True
    scene.render.simplify_subdivision_render = 0
    scene.render.simplify_child_particles = 0.1
    scene.render.simplify_volumes = 0.5


r = Render()
d = dirname(__file__)
r.blender_file = join(d, "repeat_zone_flower_by_MiRA.blend")
r.blender_bin = environ.get("BLENDER_BIN") or "blender"
r.skip_factor = 4
# r.render_frames()
r.render_video()
r.wait()
# r.final_video
