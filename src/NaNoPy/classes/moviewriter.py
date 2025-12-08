"""MovieWriter for exporting animations to MP4 format.

This module provides functionality to record animations and export them as MP4 videos.
It's designed to be memory-efficient by only storing frames when explicitly enabled.
"""

import os
from pathlib import Path
from typing import Optional
from PIL import Image
import subprocess
import tempfile
from NaNoPy.constants import DEFAULT_CODEC

class MovieWriter:
    """Records animation frames and exports them as MP4 video.
    
    This class captures frames during animation and encodes them into an MP4 file
    using ffmpeg. Frames are only stored when recording is explicitly enabled.
    
    Attributes:
        output_path (Path): Path where the MP4 file will be saved
        fps (int): Frames per second for the output video
        frames (list): List of PIL Images captured during recording
        is_recording (bool): Whether frames are currently being recorded
    
    Example:
        >>> movie = MovieWriter("output.mp4", fps=30)
        >>> # In your animation loop:
        >>> if movie.is_recording:
        ...     movie.add_frame(screen_image)
        >>> # After animation:
        >>> movie.save()
    """
    
    def __init__(self, output_path: str, fps: int = 30):
        """Initialize MovieWriter.
        
        Args:
            output_path (str): Path where MP4 will be saved (relative or absolute)
            fps (int): Frames per second for output video. Defaults to 30.
        
        Raises:
            ValueError: If fps is not positive
        """
        if fps <= 0:
            raise ValueError("fps must be positive")
        
        self.output_path = Path(output_path)
        self.fps = fps
        self.frames: list[Image.Image] = []
        self.is_recording = False
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None
        
    def start_recording(self) -> None:
        """Start recording frames. Must be called before adding frames."""
        self.is_recording = True
        self.frames = []
        
    def stop_recording(self) -> None:
        """Stop recording frames."""
        self.is_recording = False
        
    def add_frame(self, frame: Image.Image) -> None:
        """Add a frame to the recording.
        
        Args:
            frame (PIL.Image): The image frame to record
            
        Raises:
            RuntimeError: If recording hasn't been started
        """
        if not self.is_recording:
            raise RuntimeError("Recording not started. Call start_recording() first.")
        
        if not isinstance(frame, Image.Image):
            raise TypeError("Frame must be a PIL Image")
        
        # Store a copy to avoid issues with frame reuse
        self.frames.append(frame.copy())
        
    def _lossless_video_args(self, codec: str) -> list[str]:
        """Return ffmpeg args for lossless/near-lossless output for the codec."""

        # Prefer broadly supported settings while keeping lossless quality
        if codec in {"libx264", "h264"}:  # H.264 lossless
            return ["-c:v", codec, "-preset", "slow", "-crf", "0", "-pix_fmt", "yuv444p"]
        if codec in {"libx265", "h265"}:  # H.265 lossless
            return ["-c:v", codec, "-preset", "slow", "-x265-params", "lossless=1", "-pix_fmt", "yuv444p"]

        # Fallback: use the requested codec without forcing lossless flags
        return ["-c:v", codec, "-pix_fmt", "yuv420p"]

    def save(self, codec: str = DEFAULT_CODEC) -> Path:
        """Encode and save the video.
        
        Args:
            codec (str): FFmpeg codec to use. Defaults to "libx265" (H.265).
                        Other options: "libx264" (H.264), "mpeg4", etc.
        
        Returns:
            Path: Path to the saved MP4 file
            
        Raises:
            RuntimeError: If no frames have been recorded
            RuntimeError: If ffmpeg is not installed or encoding fails
        """
        if not self.frames:
            raise RuntimeError("No frames to save. Recording is empty.")
        
        if not self._is_ffmpeg_available():
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: choco install ffmpeg (or download from ffmpeg.org)"
            )
        
        # Create output directory if it doesn't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use temporary directory for frame files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save frames as temporary images
            frame_pattern = os.path.join(temp_dir, "frame_%08d.png")
            for i, frame in enumerate(self.frames):
                frame.save(os.path.join(temp_dir, f"frame_{i:08d}.png"))
            
            # Encode with ffmpeg
            cmd = [
                "ffmpeg",
                "-framerate", str(self.fps),
                "-i", frame_pattern,
                *self._lossless_video_args(codec),
                "-y",
                str(self.output_path)
            ]
            
            try:
                # Suppress ffmpeg output by redirecting to devnull
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"ffmpeg encoding failed: {e}")
        
        return self.output_path
    
    def save_with_audio(
        self,
        audio_path: str,
        codec: str = DEFAULT_CODEC
    ) -> Path:
        """Encode video with audio track.
        
        Args:
            audio_path (str): Path to audio file (MP3, WAV, etc.)
            codec (str): FFmpeg video codec. Defaults to "libx265" (H.265).
        
        Returns:
            Path: Path to the saved MP4 file
            
        Raises:
            RuntimeError: If no frames recorded or ffmpeg unavailable
            FileNotFoundError: If audio file doesn't exist
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.frames:
            raise RuntimeError("No frames to save. Recording is empty.")
        
        if not self._is_ffmpeg_available():
            raise RuntimeError("ffmpeg not found. Please install ffmpeg.")
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save frames
            frame_pattern = os.path.join(temp_dir, "frame_%08d.png")
            for i, frame in enumerate(self.frames):
                frame.save(os.path.join(temp_dir, f"frame_{i:08d}.png"))
            
            # Encode with audio
            cmd = [
                "ffmpeg",
                "-framerate", str(self.fps),
                "-i", frame_pattern,
                "-i", audio_path,
                *self._lossless_video_args(codec),
                "-c:a", "flac",
                "-shortest",
                "-y",
                str(self.output_path)
            ]
            
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"ffmpeg encoding with audio failed: {e}")
        
        return self.output_path
    
    def clear(self) -> None:
        """Clear all recorded frames from memory."""
        self.frames.clear()
        self.is_recording = False
    
    def frame_count(self) -> int:
        """Return the number of recorded frames."""
        return len(self.frames)
    
    def get_duration(self) -> float:
        """Calculate duration of video in seconds."""
        if self.fps <= 0:
            return 0.0
        return len(self.frames) / self.fps
    
    @staticmethod
    def _is_ffmpeg_available() -> bool:
        """Check if ffmpeg is installed and available."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
