### Project Overview:

`brender` is a **Python-based utility tool designed to automate and simplify the rendering workflow in Blender**, particularly for rendering animations and exporting them into final video files.

---

### Key Features and Purpose:

1. **Automated Rendering Pipeline**:

   - The tool automates the process of:
     - Extracting scene information (frame range, FPS, audio presence).
     - Rendering animation frames in parallel (using multiple CPU cores).
     - Mixing down audio (if present).
     - Combining rendered frames and audio into a final video using `ffmpeg`.

2. **Parallel Frame Rendering**:

   - Splits the frame range into chunks and uses multiple Blender processes (based on available CPU cores) to render frames concurrently, speeding up the process.

3. **Integration with Blender and FFmpeg**:

   - Uses the `blender` command-line interface (`-b` for background mode) to render frames.
   - Uses `ffmpeg` to encode the final video from the rendered frames and mixed audio.

4. **Dynamic Configuration**:

   - Allows customization of:
     - Output directory.
     - Frame format (e.g., PNG).
     - Video codec settings (via `video_args`, e.g., ProRes).
     - Audio settings.
     - Container format (e.g., `.mov`, `.mp4`).
     - Frame skipping (`skip_factor`) for faster test renders.

5. **Pre-render Hooks**:

   - Supports a `prepare(scene)` function (defined in the user script) to modify render settings (like resolution, simplifications, or engine settings) before rendering starts.

6. **Temporary File Management**:

   - Uses temporary directories and files to manage intermediate outputs (frames, audio, scripts).

7. **Blender Binary Management (in tests)**:
   - Includes a test script (`tests/blender`) that automatically downloads and sets up a portable Blender installation if not present — useful for CI or isolated environments.

---

### Example Use Case:

In `tests/render_1.py`, the tool is used to:

- Load a `.blend` file.
- Reduce render complexity (lower resolution, disable motion blur, simplify geometry).
- Set a skip factor (render every 4th frame).
- Automatically render frames, mix audio, and produce a final `.mov` video.

---

### Target Users:

- Blender artists or technical directors who want **scriptable, repeatable, and optimized render pipelines**.
- Users needing **fast test renders** or integration into automated workflows (e.g., CI/CD, batch processing).

---

### Summary:

**`brender` is a lightweight Python helper library to streamline Blender animation rendering using parallel processing and FFmpeg encoding, ideal for automating render tasks with custom preprocessing logic.**
