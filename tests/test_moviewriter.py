import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from PIL import Image

from NaNoPy.classes.moviewriter import MovieWriter


class FakeStdin:
    def __init__(self, max_write: int | None = None) -> None:
        self.data = bytearray()
        self.max_write = max_write
        self.closed = False

    def write(self, data: bytes | memoryview) -> int:
        if self.closed:
            raise BrokenPipeError("closed")
        size = len(data) if self.max_write is None else min(len(data), self.max_write)
        self.data.extend(data[:size])
        return size

    def close(self) -> None:
        self.closed = True


class FakeProcess:
    def __init__(self, *, return_code: int = 0, stderr: bytes = b"", max_write: int | None = None) -> None:
        self.stdin = FakeStdin(max_write=max_write)
        self.stderr = io.BytesIO(stderr)
        self.return_code = return_code
        self.exited = False
        self.terminated = False
        self.killed = False
        self.wait_calls = 0

    def poll(self) -> int | None:
        return self.return_code if self.exited else None

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        self.exited = True
        return self.return_code

    def terminate(self) -> None:
        self.terminated = True
        self.exited = True

    def kill(self) -> None:
        self.killed = True
        self.exited = True


class TimeoutProcess(FakeProcess):
    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        if timeout is not None and not self.killed:
            raise subprocess.TimeoutExpired(["ffmpeg"], timeout)
        self.exited = True
        return -9


class MovieWriterTests(unittest.TestCase):
    def make_started_writer(
        self,
        output: Path,
        process: FakeProcess,
        *,
        fps: int = 24,
        codec: str = "libx265",
    ) -> tuple[MovieWriter, list[tuple[list[str], dict[str, object]]]]:
        writer = MovieWriter(str(output), fps=fps, codec=codec)
        popen_calls = []

        def fake_popen(command: list[str], **kwargs: object) -> FakeProcess:
            popen_calls.append((command, kwargs))
            return process

        available = patch.object(MovieWriter, "_is_ffmpeg_available", return_value=True)
        popen = patch("NaNoPy.classes.moviewriter.subprocess.Popen", side_effect=fake_popen)
        available.start()
        popen.start()
        self.addCleanup(available.stop)
        self.addCleanup(popen.stop)
        writer.start_recording()
        return writer, popen_calls

    def test_constructor_rejects_non_integer_or_non_positive_fps(self) -> None:
        for fps in (True, 1.5, "30", None):
            with self.subTest(fps=fps):
                invalid_fps = cast("Any", fps)
                with self.assertRaisesRegex(TypeError, "fps must be an integer"):
                    MovieWriter("movie.mp4", fps=invalid_fps)

        for fps in (0, -1):
            with self.subTest(fps=fps):
                expected_message = "fps must be positive"
                with self.assertRaisesRegex(ValueError, expected_message):
                    MovieWriter("movie.mp4", fps=fps)

    def test_constructor_rejects_invalid_codec_values(self) -> None:
        for codec in (None, 123):
            with self.subTest(codec=codec):
                invalid_codec = cast("Any", codec)
                with self.assertRaisesRegex(TypeError, "codec must be a string"):
                    MovieWriter("movie.mp4", codec=invalid_codec)

        for codec in ("", "libx264 -y", "$(touch unexpected)", "-version"):
            with self.subTest(codec=codec):
                expected_message = "FFmpeg encoder name"
                with self.assertRaisesRegex(ValueError, expected_message):
                    MovieWriter("movie.mp4", codec=codec)

    def test_output_path_is_passed_as_one_argv_element_without_a_shell(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie;not-a-command.mp4")
            process = FakeProcess()
            writer, popen_calls = self.make_started_writer(output, process)

            writer.add_frame(Image.new("RGBA", (2, 2)))
            command, options = popen_calls[0]

            self.assertIn(";not-a-command", command[-1])
            self.assertIs(options["shell"], False)
            writer.clear()

    def test_streams_rgba_frames_to_one_lazy_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"existing")
            process = FakeProcess(max_write=3)
            writer, popen_calls = self.make_started_writer(output, process, fps=12)

            self.assertEqual(popen_calls, [])
            first = Image.new("RGBA", (2, 1), (1, 2, 3, 4))
            second = Image.new("L", (2, 1), 9)
            writer.add_frame(first)
            writer.add_frame(second)

            self.assertEqual(len(popen_calls), 1)
            command, options = popen_calls[0]
            self.assertIn(["-f", "rawvideo"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-pix_fmt", "rgba"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-video_size", "2x1"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-framerate", "12"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn("pipe:0", command)
            self.assertIn("lossless=1", command)
            self.assertIn("yuv444p", command)
            self.assertEqual(options["bufsize"], 0)
            self.assertNotEqual(Path(command[-1]), output)
            self.assertEqual(output.read_bytes(), b"existing")

            expected = first.tobytes() + second.convert("RGBA").tobytes()
            self.assertEqual(bytes(process.stdin.data), expected)
            self.assertEqual(writer.frame_count(), 2)
            self.assertAlmostEqual(writer.get_duration(), 2 / 12)
            self.assertFalse(hasattr(writer, "frames"))

            writer.stop_recording()
            self.assertTrue(process.stdin.closed)
            self.assertEqual(process.wait_calls, 1)
            self.assertEqual(writer.save(), output)
            self.assertNotEqual(output.read_bytes(), b"existing")

    def test_dimension_change_does_not_increment_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            process = FakeProcess()
            writer, _ = self.make_started_writer(Path(directory, "movie.mp4"), process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            mismatched_frame = Image.new("RGBA", (3, 2))

            with self.assertRaisesRegex(ValueError, "Frame size changed"):
                writer.add_frame(mismatched_frame)

            self.assertEqual(writer.frame_count(), 1)
            writer.clear()

    def test_clear_aborts_staging_without_touching_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"keep me")
            process = FakeProcess()
            writer, popen_calls = self.make_started_writer(output, process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            staging = Path(popen_calls[0][0][-1])
            self.assertTrue(staging.exists())

            writer.clear()

            self.assertEqual(output.read_bytes(), b"keep me")
            self.assertFalse(staging.exists())
            self.assertEqual(writer.frame_count(), 0)
            self.assertFalse(writer.is_recording)
            self.assertTrue(process.terminated)

    def test_encoder_failure_reports_stderr_and_preserves_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"keep me")
            process = FakeProcess(return_code=1, stderr=b"encoder exploded")
            writer, popen_calls = self.make_started_writer(output, process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            staging = Path(popen_calls[0][0][-1])

            with self.assertRaisesRegex(RuntimeError, "encoder exploded"):
                writer.stop_recording()

            self.assertEqual(output.read_bytes(), b"keep me")
            self.assertFalse(staging.exists())

    def test_encoder_timeout_is_killed_and_cleaned_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"keep me")
            process = TimeoutProcess()
            writer, popen_calls = self.make_started_writer(output, process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            staging = Path(popen_calls[0][0][-1])

            with self.assertRaisesRegex(RuntimeError, "encoding timed out"):
                writer.stop_recording()

            self.assertTrue(process.killed)
            self.assertFalse(staging.exists())
            self.assertEqual(output.read_bytes(), b"keep me")

    def test_audio_mux_copies_video_and_atomically_publishes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"old output")
            audio = Path(directory, "audio.mp3")
            audio.write_bytes(b"audio")
            process = FakeProcess()
            writer, _ = self.make_started_writer(output, process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            writer.stop_recording()
            stream_path = writer._stream_path
            assert stream_path is not None
            stream_path.write_bytes(b"encoded video")
            mux_commands = []

            def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
                mux_commands.append(command)
                Path(command[-1]).write_bytes(b"muxed output")
                return subprocess.CompletedProcess(command, 0)

            with patch("NaNoPy.classes.moviewriter.subprocess.run", side_effect=fake_run):
                result = writer.save_with_audio(str(audio))

            self.assertEqual(result, output)
            self.assertEqual(output.read_bytes(), b"muxed output")
            self.assertFalse(stream_path.exists())
            command = mux_commands[0]
            self.assertIn(["-c:v", "copy"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn(["-c:a", "flac"], [command[index : index + 2] for index in range(len(command) - 1)])
            self.assertIn("-shortest", command)

    def test_audio_mux_failure_preserves_existing_and_retry_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "movie.mp4")
            output.write_bytes(b"old output")
            audio = Path(directory, "audio.mp3")
            audio.write_bytes(b"audio")
            process = FakeProcess()
            writer, _ = self.make_started_writer(output, process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            writer.stop_recording()
            stream_path = writer._stream_path
            assert stream_path is not None
            stream_path.write_bytes(b"encoded video")
            failure = subprocess.CalledProcessError(1, ["ffmpeg"], stderr="mux exploded")
            audio_path = str(audio)

            with patch("NaNoPy.classes.moviewriter.subprocess.run", side_effect=failure):
                expected_message = "mux exploded"
                with self.assertRaisesRegex(RuntimeError, expected_message):
                    writer.save_with_audio(audio_path)

            self.assertEqual(output.read_bytes(), b"old output")
            self.assertEqual(stream_path.read_bytes(), b"encoded video")
            self.assertTrue(writer.has_pending_output())
            self.assertEqual(list(Path(directory).glob(".*-audio-*.mp4")), [])
            writer.clear()

    def test_late_codec_change_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            process = FakeProcess()
            writer, _ = self.make_started_writer(Path(directory, "movie.mp4"), process)
            writer.add_frame(Image.new("RGBA", (2, 2)))
            with self.assertRaisesRegex(ValueError, "already encoded"):
                writer.save(codec="libx264")
            writer.clear()

    def test_empty_recording_and_unavailable_ffmpeg(self) -> None:
        writer = MovieWriter("unused.mp4")
        with patch.object(MovieWriter, "_is_ffmpeg_available", return_value=False):
            expected_message = "ffmpeg not found"
            with self.assertRaisesRegex(RuntimeError, expected_message):
                writer.start_recording()

        with patch.object(MovieWriter, "_is_ffmpeg_available", return_value=True):
            writer.start_recording()
        with self.assertRaisesRegex(RuntimeError, "No frames"):
            writer.save()
        writer.clear()

    def test_setup_failure_resets_recording_state(self) -> None:
        writer = MovieWriter("movie.mp4")
        with patch.object(MovieWriter, "_is_ffmpeg_available", return_value=True):
            writer.start_recording()
        with (
            patch.object(writer, "_create_staging_path", side_effect=PermissionError("denied")),
        ):
            frame = Image.new("RGBA", (2, 2))
            with self.assertRaisesRegex(RuntimeError, "Unable to prepare"):
                writer.add_frame(frame)

        self.assertFalse(writer.is_recording)
        self.assertIsNone(writer._frame_size)
        self.assertFalse(writer.has_pending_output())

    def test_relative_output_is_anchored_when_working_directory_changes(self) -> None:
        original_directory = Path.cwd()
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            try:
                os.chdir(first)
                process = FakeProcess()
                writer, _ = self.make_started_writer(Path("movie.mp4"), process)
                writer.add_frame(Image.new("RGBA", (2, 2)))
                os.chdir(second)
                result = writer.save()
            finally:
                os.chdir(original_directory)

            self.assertEqual(result, Path(first, "movie.mp4"))
            self.assertTrue(Path(first, "movie.mp4").exists())
            self.assertFalse(Path(second, "movie.mp4").exists())


if __name__ == "__main__":
    unittest.main()
