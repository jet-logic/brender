import inspect
import shlex
from math import ceil
from subprocess import PIPE, Popen
from os import path, cpu_count, environ
from tempfile import NamedTemporaryFile, gettempdir
from pathlib import Path
from json import load
from sys import stderr


def say(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def ffargs(d: dict | list | str):
    if isinstance(d, (list, tuple)):
        for v in d:
            yield str(v)
    elif isinstance(d, str):
        yield from shlex.split(d)
    else:
        for k, v in d.items():
            if k:
                if v is True:
                    yield f"-{k}"
                    continue
                elif v is False:
                    yield f"-no{k}"
                    continue
                else:
                    yield f"-{k}"
                    if v is not None:
                        yield str(v)


def task1(scene_name, dest):
    from json import dump
    import bpy

    scene = bpy.data.scenes[scene_name]
    with open(dest, "w") as w:
        dump(
            {
                "frame_range": [scene.frame_start, scene.frame_end],
                "fps": scene.render.fps,
                "fps_base": scene.render.fps_base,
                "has_audio": any(
                    seq.type == "SOUND"
                    for seq in getattr(scene.sequence_editor, "sequences_all", [])
                ),
            },
            w,
        )


class Render:

    final_video: str
    video_path: str
    audio_path: str
    frames_dir: str
    final_fps: int
    _file_info: dict
    has_audio: bool
    start_frame: int
    end_frame: int
    final_audio: str
    output_dir: str
    blender_bin: str

    def __init__(self, blender_file="", scene_name=""):
        self.blender_file = blender_file or environ.get("BLENDER_FILE")
        self.scene_name = scene_name or environ.get("SCENE") or "Scene"
        self.skip_factor = 1
        self._jobs: list[Popen] = []
        self.workers = max(int(cpu_count() / 4), 2)
        self.with_audio: bool | None = None
        self.audio_suffix = ".wav"
        self.frames_stem = "F######"
        self.frames_strf = "F{!d}"
        self.frames_format = "png"
        self.ffmpeg_bin = "ffmpeg"
        self.output_audio = ""
        self.output_video = ""
        self.container: str = "mov"  # avi, mov, mkv, mp4
        self.video_args: dict | list | str = "-c:v prores_ks -profile:v 5"
        self.audio_args: dict | list | str = ""
        self.sound_mix_args = {"container": "WAV", "codec": "PCM"}
        self.input_file: str = ""

    def __getattr__(self, name):
        f = not name.startswith("_get_") and getattr(self, f"_get_{name}", None)
        if f:
            setattr(self, name, None)
            v = f()
            setattr(self, name, v)
            name.startswith("_") or say(f"{name}: {v}")
            return v
        try:
            m = super().__getattr__
        except AttributeError:
            pass
        else:
            return m(name)
        c = self.__class__
        raise AttributeError(
            f"{c.__module__}.{c.__qualname__} has no attribute '{name}'"
        )

    def _get_blender_bin(self):
        v = environ.get("BLENDER_BIN") or "blender"
        return v

    def _get_output_dir(self):
        return Path(gettempdir()) / Path(self.blender_file).stem

    def _get_frames_dir(self):
        return path.join(self.output_dir, "frames")

    def _get_final_audio(self):
        x = self.output_audio
        if not x:
            x = "//" + self.scene_name
        if x.startswith("//"):
            x = path.join(self.output_dir, x[2:])
        return x + "." + self.sound_mix_args["container"].lower()

    def _get_final_video(self):
        x = self.output_video
        if not x:
            x = "//" + self.scene_name
        if x.startswith("//"):
            x = path.join(self.output_dir, x[2:])
        start_frame = self.start_frame
        end_frame = self.end_frame
        skip_factor = self.skip_factor
        final_fps = self.final_fps
        return (
            x
            + "_"
            + "_".join(
                x
                for x in [
                    str(start_frame),
                    str(end_frame),
                    "" if skip_factor == 1 else str(skip_factor),
                    f"{final_fps:f}".strip("0").strip("."),
                ]
                if x
            )
            + f".{self.container.lower()}"
        )

    def _get_has_audio(self):
        return self._file_info["has_audio"]

    def _get_final_fps(self):
        return (self._file_info["fps"] // self.skip_factor) / self._file_info[
            "fps_base"
        ]

    def _get_start_frame(self):
        return self._file_info["frame_range"][0]

    def _get_end_frame(self):
        return self._file_info["frame_range"][1]

    def _get__file_info(self):
        with NamedTemporaryFile() as msg:
            msg.close()
            with NamedTemporaryFile(mode="w+", prefix="task", delete=False) as tmp2:
                tmp2.write(inspect.getsource(task1))
                tmp2.write(f"\n{task1.__name__}({self.scene_name!r}, {msg.name!r})")
                tmp2.flush()
                Popen(
                    [
                        self.blender_bin,
                        "-b",
                        self.blender_file,
                        "-S",
                        self.scene_name,
                        "-q",
                        "--python",
                        tmp2.name,
                        "--",
                        self.scene_name,
                        msg.name,
                    ],
                ).wait()
            with open(msg.name) as r:
                d = load(r)
                say(f"Frame: {d['frame_range']!r}")
                say(f"Fps: {d['fps']} / {d['fps_base']}")
                return d

    def render_frames(self, **kwargs):
        start_frame = self.start_frame
        end_frame = self.end_frame
        skip_factor = self.skip_factor
        workers = self.workers
        scene_name = self.scene_name
        blender_bin = self.blender_bin
        frame_count = ((end_frame - start_frame) // skip_factor) + 1
        chunk_size = ceil(frame_count / workers)
        frames_dir = self.frames_dir
        frames_stem = self.frames_stem
        frames_format = self.frames_format
        output_path = path.join(frames_dir, f"{frames_stem}.{frames_format}")

        # --- start render chunks ---
        func = None
        try:
            from __main__ import prepare as func
        except ImportError:
            pass

        head = [
            blender_bin,
            "-b",
            self.blender_file,
            "-S",
            scene_name,
            "-o",
            output_path,
        ]
        tail = ["-F", frames_format.upper()]
        if skip_factor != 1:
            tail.extend(["-j", (skip_factor)])
        if func:
            tail += [
                "--python-expr",
                ";".join(
                    [
                        v
                        for v in (
                            f"import bpy",
                            f"scene = bpy.data.scenes['{scene_name}']",
                        )
                        if v
                    ]
                )
                + (
                    ("\n" + inspect.getsource(func) + "\n" + f"{func.__name__}(scene)")
                    if func
                    else ""
                ),
            ]

        tail += ["-a"]
        for i in range(workers):
            s = start_frame + i * chunk_size * skip_factor
            e = min(end_frame, s + (chunk_size - 1) * skip_factor)
            if s > end_frame:
                break
            cmd = [*head, "-s", s, "-e", e, *tail]
            say("Frames:", *cmd)
            self._jobs.append(Popen([str(x) for x in cmd]))
        return self

    def mix_sound(self):
        mix_args = {"filepath": self.final_audio, "container": "WAV", "codec": "PCM"}
        Path(mix_args["filepath"]).parent.mkdir(exist_ok=True)
        cmd = [
            self.blender_bin,
            "-b",
            self.blender_file,
            "-S",
            self.scene_name,
            "--python-expr",
            f"import bpy; kwa={mix_args!r}; bpy.ops.sound.mixdown(**kwa)",
        ]
        say("Audio:", *cmd)
        self._jobs.append(Popen(cmd))
        return self

    def frame_files(self, check_render=False):
        start_frame = self.start_frame
        end_frame = self.end_frame
        skip_factor = self.skip_factor
        frames_dir = self.frames_dir
        frames_format = self.frames_format
        if check_render:
            last = path.join(frames_dir, f"F%06d.{frames_format}" % (start_frame))
            if not path.exists(last):
                self.render_frames().wait()
        p = self.input_file = path.join(frames_dir, f"input.txt")
        i = start_frame
        e = end_frame
        with open(p, "w") as w:
            while i <= e:
                w.write(f"file 'F%06d.{frames_format}'\n" % i)
                i += skip_factor

    def render_video(self, **kwargs):
        cmd = [self.ffmpeg_bin]
        cmd.extend(
            ffargs(
                {
                    "r": f"{self.final_fps:f}".strip("0").strip("."),
                    "hide_banner": True,
                    "y": True,
                    "v": "warning",
                }
            )
        )
        self.wait()
        self.frame_files(check_render=True)

        cmd += [
            "-use_wallclock_as_timestamps",
            "1",
            "-f",
            "concat",
            "-protocol_whitelist",
            "file",
            "-safe",
            "0",
            "-i",
            self.input_file,
        ]

        if self.with_audio is not False and self.has_audio:
            if not path.exists(self.final_audio):
                self.mix_sound().wait()
            cmd += ["-i", self.final_audio]
            cmd += ffargs(self.audio_args)

        cmd.extend(ffargs(self.video_args))
        cmd += [self.final_video]

        say("Video:", shlex.join([str(x) for x in cmd]))
        self._jobs.append(Popen([str(x) for x in cmd]))

        return self

    def wait(self):
        jobs = self._jobs
        while jobs:
            jobs.pop().wait()
