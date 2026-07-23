"""Stream animation frames to FFmpeg and export them as a video."""

import os
from pathlib import Path
import secrets
import stat
import subprocess
import threading
from typing import Optional

from PIL import Image

from NaNoPy.constants import DEFAULT_CODEC


class MovieWriter:
    """Encode animation frames with one long-lived FFmpeg process.

    FFmpeg starts when the first frame establishes the video dimensions. Each
    subsequent frame is converted to RGBA and written directly to FFmpeg's stdin,
    so recordings do not retain a frame list or create a temporary PNG sequence.

    Args:
        output_path: Path where the encoded video will be saved.
        fps: Frames per second for the output video.
        codec: FFmpeg video encoder. Because encoding happens while frames arrive,
            the codec must be selected when the writer is created.
    """

    _FINALIZE_TIMEOUT_SECONDS = 60
    _STDERR_JOIN_TIMEOUT_SECONDS = 5

    def __init__(self, output_path: str, fps: int = 30, codec: str = DEFAULT_CODEC):
        if fps <= 0:
            raise ValueError("fps must be positive")
        if not codec:
            raise ValueError("codec must not be empty")

        self.output_path = Path(output_path)
        self._target_path = self.output_path.absolute()
        self.fps = fps
        self.codec = codec
        self.is_recording = False

        self._process: Optional[subprocess.Popen] = None
        self._stream_path: Optional[Path] = None
        self._stderr_buffer = bytearray()
        self._stderr_thread: Optional[threading.Thread] = None
        self._frame_size: Optional[tuple[int, int]] = None
        self._frame_count = 0
        self._finalized = False

    def start_recording(self) -> None:
        """Start accepting frames for a new recording."""
        if self.is_recording:
            raise RuntimeError("Recording is already active.")
        if self._process is not None:
            raise RuntimeError("The previous FFmpeg process has not been finalized.")
        if self._stream_path is not None:
            raise RuntimeError("Save or clear the finalized recording before starting again.")
        if not self._is_ffmpeg_available():
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: choco install ffmpeg (or download from ffmpeg.org)"
            )

        self._frame_size = None
        self._frame_count = 0
        self._finalized = False
        self.is_recording = True

    def stop_recording(self) -> None:
        """Stop accepting frames and finalize the video stream."""
        if not self.is_recording:
            return

        self.is_recording = False
        if self._process is not None:
            self._finalize_video()

    def add_frame(self, frame: Image.Image) -> None:
        """Write one Pillow image to the active FFmpeg stream."""
        if not self.is_recording:
            raise RuntimeError("Recording not started. Call start_recording() first.")
        if not isinstance(frame, Image.Image):
            raise TypeError("Frame must be a PIL Image")

        if self._frame_size is None:
            self._start_ffmpeg(frame.size)
            self._frame_size = frame.size
        elif frame.size != self._frame_size:
            raise ValueError(
                f"Frame size changed from {self._frame_size} to {frame.size}. "
                "All frames in a recording must have identical dimensions."
            )

        rgba_frame = frame if frame.mode == "RGBA" else frame.convert("RGBA")
        self._write_bytes(rgba_frame.tobytes())
        self._frame_count += 1

    def _start_ffmpeg(self, frame_size: tuple[int, int]) -> None:
        """Start FFmpeg after the first frame establishes width and height."""
        width, height = frame_size
        if width <= 0 or height <= 0:
            raise ValueError("Frame dimensions must be positive")

        try:
            self._target_path.parent.mkdir(parents=True, exist_ok=True)
            self._stream_path = self._create_staging_path("video")
        except (OSError, RuntimeError) as exc:
            self._stream_path = None
            self.is_recording = False
            raise RuntimeError(f"Unable to prepare ffmpeg output: {exc}") from exc

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-video_size",
            f"{width}x{height}",
            "-framerate",
            str(self.fps),
            "-i",
            "pipe:0",
            *self._lossless_video_args(self.codec),
            "-y",
            str(self._stream_path),
        ]

        try:
            # Unbuffered stdin ensures each frame is handed to FFmpeg immediately.
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                bufsize=0,
            )
            if self._process.stderr is not None:
                self._stderr_buffer.clear()
                self._stderr_thread = threading.Thread(
                    target=MovieWriter._drain_stderr,
                    args=(self._process.stderr, self._stderr_buffer),
                    daemon=True,
                )
                self._stderr_thread.start()
        except OSError as exc:
            if self._stream_path is not None:
                self._stream_path.unlink(missing_ok=True)
                self._stream_path = None
            self.is_recording = False
            raise RuntimeError(f"Unable to start ffmpeg: {exc}") from exc

    @staticmethod
    def _drain_stderr(stream, buffer: bytearray) -> None:
        """Drain FFmpeg diagnostics so its stderr pipe cannot block encoding."""
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            buffer.extend(chunk)
            if len(buffer) > 65536:
                del buffer[:-65536]

    def _finish_stderr_reader(self, process: subprocess.Popen) -> bytes:
        if self._stderr_thread is not None:
            self._stderr_thread.join(timeout=self._STDERR_JOIN_TIMEOUT_SECONDS)
            if self._stderr_thread.is_alive() and process.stderr is not None:
                process.stderr.close()
                self._stderr_thread.join(timeout=1)
            self._stderr_thread = None
        if process.stderr is not None:
            process.stderr.close()
        stderr = bytes(self._stderr_buffer)
        self._stderr_buffer.clear()
        return stderr

    def _write_bytes(self, data: bytes) -> None:
        process = self._process
        if process is None or process.stdin is None:
            raise RuntimeError("ffmpeg did not start correctly")

        if process.poll() is not None:
            self.is_recording = False
            self._finalize_video(write_error=BrokenPipeError("ffmpeg exited before receiving the frame"))

        remaining = memoryview(data)
        try:
            while remaining:
                written = process.stdin.write(remaining)
                if not written:
                    raise BrokenPipeError("ffmpeg stopped accepting frame data")
                remaining = remaining[written:]
        except (BrokenPipeError, OSError) as exc:
            self.is_recording = False
            self._finalize_video(write_error=exc)

    def _finalize_video(self, write_error: Optional[BaseException] = None) -> None:
        process = self._process
        if process is None:
            return

        close_error: Optional[BaseException] = None
        if process.stdin is not None:
            try:
                process.stdin.close()
            except (BrokenPipeError, OSError) as exc:
                close_error = exc

        timed_out = False
        try:
            return_code = process.wait(timeout=self._FINALIZE_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            return_code = process.wait()
        stderr = self._finish_stderr_reader(process)
        self._process = None

        failure = write_error or (close_error if return_code != 0 else None)
        if timed_out or return_code != 0 or failure is not None:
            self._finalized = False
            if self._stream_path is not None:
                self._stream_path.unlink(missing_ok=True)
                self._stream_path = None
            detail = stderr.decode(errors="replace").strip()
            if timed_out:
                message = f"ffmpeg encoding timed out after {self._FINALIZE_TIMEOUT_SECONDS} seconds"
            else:
                message = f"ffmpeg encoding failed with exit code {return_code}"
            if detail:
                message += f": {detail}"
            elif failure is not None:
                message += f": {failure}"
            raise RuntimeError(message) from failure

        self._finalized = True

    def _lossless_video_args(self, codec: str) -> list[str]:
        """Return the existing lossless/near-lossless settings for ``codec``."""
        if codec in {"libx264", "h264"}:
            return ["-c:v", codec, "-preset", "slow", "-crf", "0", "-pix_fmt", "yuv444p"]
        if codec in {"libx265", "h265"}:
            return [
                "-c:v",
                codec,
                "-preset",
                "slow",
                "-x265-params",
                "lossless=1",
                "-pix_fmt",
                "yuv444p",
            ]

        return ["-c:v", codec, "-pix_fmt", "yuv420p"]

    def _validate_save_codec(self, codec: Optional[str]) -> None:
        if codec is not None and codec != self.codec:
            raise ValueError(
                f"This recording is already encoded with {self.codec!r}. "
                "Select a codec in MovieWriter(..., codec=...) or "
                "canvas.start_recording(..., codec=...) before adding frames."
            )

    def _create_staging_path(self, purpose: str) -> Path:
        """Securely reserve a sibling path with normal user-file permissions."""
        suffix = self._target_path.suffix or ".mp4"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY

        for _ in range(100):
            token = secrets.token_hex(8)
            candidate = self._target_path.parent / f".{self._target_path.stem}-{purpose}-{token}{suffix}"
            try:
                descriptor = os.open(candidate, flags, 0o666)
            except FileExistsError:
                continue
            os.close(descriptor)
            return candidate

        raise RuntimeError(f"Unable to reserve a temporary {purpose} output path")

    def _replace_output(self, staging_path: Path) -> None:
        """Atomically replace the destination, retaining an existing file mode."""
        try:
            existing_mode = stat.S_IMODE(self._target_path.stat().st_mode)
        except FileNotFoundError:
            existing_mode = None
        if existing_mode is not None:
            staging_path.chmod(existing_mode)
        os.replace(staging_path, self._target_path)

    def _ensure_finalized(self) -> None:
        """Finish the encoder while keeping its private output unpublished."""
        if self._frame_count == 0:
            raise RuntimeError("No frames to save. Recording is empty.")

        if self.is_recording:
            self.stop_recording()
        elif self._process is not None:
            self._finalize_video()

        if not self._finalized:
            raise RuntimeError("The recording could not be finalized.")

    def save(self, codec: Optional[str] = None) -> Path:
        """Finalize and atomically publish the encoded video.

        ``codec`` remains accepted for compatibility when it matches the codec
        selected at construction time. A different codec cannot be selected here
        because frames have already been encoded.
        """
        self._validate_save_codec(codec)
        self._ensure_finalized()
        if self._stream_path is not None:
            self._replace_output(self._stream_path)
            self._stream_path = None
        return self._target_path

    def save_with_audio(self, audio_path: str, codec: Optional[str] = None) -> Path:
        """Finalize video and mux it with a lossless FLAC audio stream.

        Audio is supplied after recording in the existing API, so a second FFmpeg
        command stream-copies the encoded video and adds audio without changing
        video quality.
        """
        audio = Path(audio_path).absolute()
        if not audio.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self._validate_save_codec(codec)
        self._ensure_finalized()
        video_input = self._stream_path or self._target_path

        temporary_path: Optional[Path] = None
        try:
            temporary_path = self._create_staging_path("audio")

            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video_input),
                "-i",
                str(audio),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "flac",
                "-shortest",
                "-y",
                str(temporary_path),
            ]
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            except subprocess.CalledProcessError as exc:
                detail = (exc.stderr or "").strip()
                message = "ffmpeg audio muxing failed"
                if detail:
                    message += f": {detail}"
                raise RuntimeError(message) from exc
            except OSError as exc:
                raise RuntimeError(f"Unable to start ffmpeg for audio muxing: {exc}") from exc

            self._replace_output(temporary_path)
            temporary_path = None
            if self._stream_path is not None:
                self._stream_path.unlink(missing_ok=True)
                self._stream_path = None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        return self._target_path

    def clear(self) -> None:
        """Abort an active stream and reset recording state."""
        process = self._process
        self._process = None

        if process is not None:
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            self._finish_stderr_reader(process)

        if self._stream_path is not None:
            self._stream_path.unlink(missing_ok=True)
            self._stream_path = None

        self._frame_size = None
        self._frame_count = 0
        self._finalized = False
        self.is_recording = False

    def has_pending_output(self) -> bool:
        """Return whether a finalized or active recording still needs handling."""
        return self._process is not None or self._stream_path is not None

    def frame_count(self) -> int:
        """Return the number of frames written to FFmpeg."""
        return self._frame_count

    def get_duration(self) -> float:
        """Return the encoded duration implied by frame count and FPS."""
        return self._frame_count / self.fps

    def __del__(self):
        # Best-effort protection for direct MovieWriter users who leave an
        # encoder running or abandon a finalized staging file.
        try:
            if getattr(self, "_process", None) is not None or getattr(self, "_stream_path", None) is not None:
                self.clear()
        except Exception:
            pass

    @staticmethod
    def _is_ffmpeg_available() -> bool:
        """Return whether a working ``ffmpeg`` executable is available on PATH."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
