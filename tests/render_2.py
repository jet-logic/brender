from brender import Render
from os.path import join, dirname
from tempfile import gettempdir


def prepare(scene):
    scene.render.resolution_percentage = 25


r = Render()
d = dirname(__file__)
r.blender_file = join(d, "repeat_zone_flower_by_MiRA.blend")
r.output_dir = join(gettempdir(), "render2")
r.render_video()
r.wait()
