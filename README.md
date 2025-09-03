# `brender` – Blender Render Helper

Automate and streamline your Blender animation rendering workflow with `brender`, a lightweight Python tool that handles parallel frame rendering, audio mixing, and video encoding using `ffmpeg`.

Perfect for artists and technical directors who want fast, scriptable renders with preprocessing control—ideal for test renders, batch jobs, or CI/CD pipelines.

## 🚀 Features

- ✅ **Parallel rendering** using multiple Blender instances
- 🎧 **Automatic audio mixing** from Blender’s sequencer
- 🎬 **Video assembly** via `ffmpeg` (supports ProRes, H.264, and more)
- ⚙️ **Customizable output**: format, codec, resolution, skip frames
- 🔧 **Pre-render hooks** to modify scene settings (e.g., simplify, lower res)
- 💾 **Smart temp file management** and output naming
- 🐍 **Pure Python** – works alongside your existing scripts

## ☕ Support

If you find this project helpful, consider supporting me:

## [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B01E8SY7)

## 📦 Installation

```bash
pip install brender
```

---

## ⚙️ Requirements

- [Blender](https://www.blender.org/download/) (installed or available in `PATH`)
- [`ffmpeg`](https://ffmpeg.org/download.html) (must be in `PATH` or set via `.ffmpeg_bin`)
- Python 3.9+

Optional: Set custom Blender binary path:

```bash
export BLENDER_BIN="/path/to/blender"
```

---

## 🖼️ Basic Usage

Create a render script (e.g., `render.py`) in your project directory:

```python
from brender import Render

# Define preprocessing logic (optional)
def prepare(scene):
    scene.render.resolution_percentage = 25   # Render at 25% resolution
    scene.render.use_simplify = True           # Enable simplifications
    scene.render.simplify_child_particles = 0.1
    scene.render.use_motion_blur = False       # Disable expensive effects

# Initialize renderer
r = Render()

# Set your .blend file
r.blender_file = "path/to/your/animation.blend"

# Optional: Skip every Nth frame (great for preview renders)
r.skip_factor = 4  # Render every 4th frame

# Optional: Customize output
r.output_dir = "/tmp/my_render"                # Custom output folder
r.container = "mp4"                            # Output format
r.video_args = "-c:v libx264 -crf 23 -pix_fmt yuv420p"
r.audio_args = "-c:a aac -b:a 192k"

# Start rendering!
r.render_video()  # Renders frames + mixes audio + encodes video
r.wait()          # Wait for all processes to finish

print("Final video:", r.final_video)
```

Run it:

```bash
python render.py
```

Output will go to:

```
/tmp/my_render/Scene_1_100_4_6.mp4
```

> (Scene name, start-end frame, skip factor, effective FPS)

---

## 🔍 How It Works

1. **Inspect Scene**: Reads frame range, FPS, and checks for audio.
2. **Render Frames**: Splits the timeline across CPU cores and renders in parallel.
3. **Mix Audio**: Exports audio mix from Blender’s sequencer (if present).
4. **Encode Video**: Uses `ffmpeg` to combine frames and audio into final video.

All intermediate files (frames, audio) are stored under a temp directory named after your `.blend` file.

---

## 🛠️ Configuration Options

| Attribute       | Default                         | Description                                  |
| --------------- | ------------------------------- | -------------------------------------------- |
| `blender_file`  | `BLENDER_FILE` env              | Path to `.blend` file                        |
| `scene_name`    | `"Scene"`                       | Name of the scene to render                  |
| `skip_factor`   | `1`                             | Render every Nth frame (1 = all frames)      |
| `workers`       | `max(2, cpu_count // 4)`        | Number of parallel Blender processes         |
| `container`     | `"mov"`                         | Output container: `mov`, `mp4`, `avi`, `mkv` |
| `video_args`    | `"-c:v prores_ks -profile:v 5"` | FFmpeg video encoding args                   |
| `audio_args`    | `""`                            | FFmpeg audio encoding args                   |
| `frames_format` | `"png"`                         | Frame format: `png`, `jpg`, `exr`, etc.      |
| `output_dir`    | `/tmp/<blend-name>`             | Root output directory                        |
| `ffmpeg_bin`    | `"ffmpeg"`                      | Path to `ffmpeg` executable                  |

Example: Fast preview with H.264:

```python
r.container = "mp4"
r.video_args = "-c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p"
r.audio_args = "-c:a aac -b:a 128k"
r.skip_factor = 2
```

---

## 🤝 Feedback & Contributions

Have ideas or issues? Open an issue or PR on [Github](https://github.com/jet-logic/brender/)!

> `brender` – because rendering should be simple and fast.
