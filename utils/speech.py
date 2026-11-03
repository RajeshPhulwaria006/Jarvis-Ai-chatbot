"""Hybrid speech I/O for Jarvis.

Cloud-first:
- STT: Groq Whisper Large V3 Turbo
- TTS: Edge neural voices

Fallbacks:
- STT: faster-whisper tiny multilingual model (loaded only when needed)
- TTS: existing pyttsx3 voice

Audio capture uses sounddevice + a lightweight RMS silence detector.
"""
from __future__ import annotations

import asyncio
import os
import re
import tempfile
import time
import wave
from pathlib import Path
from threading import Lock

import numpy as np
import sounddevice as sd

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    from playsound3 import playsound
except ImportError:
    playsound = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


SAMPLE_RATE = 16_000
CHANNELS = 1
BLOCK_SIZE = 1_024
MAX_RECORD_SECONDS = float(os.getenv("JARVIS_MAX_RECORD_SECONDS", "12"))
END_SILENCE_SECONDS = float(os.getenv("JARVIS_END_SILENCE_SECONDS", "0.9"))
CLOUD_STT_MODEL = os.getenv("JARVIS_STT_MODEL", "whisper-large-v3-turbo")
LOCAL_STT_MODEL = os.getenv("JARVIS_LOCAL_STT_MODEL", "tiny")
EDGE_ENGLISH_VOICE = os.getenv("JARVIS_EDGE_EN_VOICE", "en-IN-PrabhatNeural")
EDGE_HINDI_VOICE = os.getenv("JARVIS_EDGE_HI_VOICE", "hi-IN-MadhurNeural")

_groq_client = None
_local_whisper = None
_local_tts_engine = None
_tts_lock = Lock()


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        if Groq is None:
            raise RuntimeError("The groq package is not installed.")
        # Groq() reads GROQ_API_KEY from the environment.
        _groq_client = Groq()
    return _groq_client


def _capture_wav(path: str) -> bool:
    """Record one utterance until silence, with a hard maximum duration."""
    print("Jarvis: Listening... (speak now)")
    chunks: list[np.ndarray] = []
    started = False
    silence_blocks = 0
    max_blocks = int(MAX_RECORD_SECONDS * SAMPLE_RATE / BLOCK_SIZE)
    end_silence_blocks = max(1, int(END_SILENCE_SECONDS * SAMPLE_RATE / BLOCK_SIZE))

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=BLOCK_SIZE,
        ) as stream:
            # Brief ambient calibration; avoid an overly high threshold.
            ambient = []
            for _ in range(6):
                block, overflowed = stream.read(BLOCK_SIZE)
                ambient.append(block.copy())

            noise_rms = float(np.mean([
                np.sqrt(np.mean(np.square(b.astype(np.float32))))
                for b in ambient
            ]))
            threshold = max(260.0, noise_rms * 2.7)
            pre_roll = ambient[-2:]
            chunks.extend(pre_roll)

            for _ in range(max_blocks):
                block, overflowed = stream.read(BLOCK_SIZE)
                block = block.copy()
                rms = float(np.sqrt(np.mean(np.square(block.astype(np.float32)))))
                if rms >= threshold:
                    started = True
                    silence_blocks = 0
                    chunks.append(block)
                elif started:
                    chunks.append(block)
                    silence_blocks += 1
                    if silence_blocks >= end_silence_blocks:
                        break
                else:
                    # Keep only a short pre-roll before speech starts.
                    chunks.append(block)
                    if len(chunks) > 4:
                        chunks.pop(0)

        if not started:
            print("Jarvis: I didn't hear speech. Please try again.")
            return False

        audio = np.concatenate(chunks, axis=0).astype(np.int16)
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio.tobytes())
        return True
    except Exception as exc:
        print(f"Jarvis microphone error: {exc}")
        print("Check microphone permissions and your input device.")
        return False


def _transcribe_cloud(wav_path: str) -> str:
    client = _get_groq_client()
    with open(wav_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=(Path(wav_path).name, audio_file.read()),
            model=CLOUD_STT_MODEL,
            # Do not force a language: this helps Hindi/English code-switching.
            response_format="text",
            temperature=0.0,
            prompt=(
                "Transcribe the speaker's words faithfully. The speaker may use "
                "English, Hindi, or Hinglish, including Indian names and commands. "
                "Do not translate; preserve the spoken language."
            ),
        )
    if isinstance(result, str):
        return result.strip()
    return str(getattr(result, "text", "")).strip()


def _transcribe_local(wav_path: str) -> str:
    """Lazy-load a compact multilingual model only after cloud STT fails."""
    global _local_whisper
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Local STT fallback is not installed. Run: "
            "pip install faster-whisper"
        ) from exc

    if _local_whisper is None:
        print("Jarvis: Cloud transcription failed; loading local Whisper model...")
        _local_whisper = WhisperModel(
            LOCAL_STT_MODEL,
            device="cpu",
            compute_type="int8",
            cpu_threads=max(1, min(4, os.cpu_count() or 2)),
        )

    segments, info = _local_whisper.transcribe(
        wav_path,
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(segment.text.strip() for segment in segments).strip()


def listen() -> str:
    """Record a spoken command and return its transcript, or an empty string."""
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name

        if not _capture_wav(temp_path):
            return ""

        try:
            text = _transcribe_cloud(temp_path)
            if text:
                print(f"You (voice): {text}")
                return text
            raise RuntimeError("Cloud transcription returned empty text.")
        except Exception as cloud_error:
            print(f"Jarvis: Cloud STT unavailable ({cloud_error}).")
            try:
                text = _transcribe_local(temp_path)
                if text:
                    print(f"You (local voice): {text}")
                    return text
                print("Jarvis: Local transcription returned no speech.")
                return ""
            except Exception as local_error:
                print(f"Jarvis: Local STT fallback unavailable ({local_error}).")
                print("Type your command instead, or restore internet/API access.")
                return ""
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _edge_voice_for(text: str) -> str:
    # Devanagari text gets a Hindi neural voice. Romanized Hinglish uses Indian English.
    if re.search(r"[\u0900-\u097F]", text):
        return EDGE_HINDI_VOICE
    return EDGE_ENGLISH_VOICE


async def _save_edge_audio(text: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, voice=_edge_voice_for(text))
    await communicate.save(output_path)


def _speak_local(text: str) -> bool:
    global _local_tts_engine
    if pyttsx3 is None:
        return False
    try:
        with _tts_lock:
            if _local_tts_engine is None:
                _local_tts_engine = pyttsx3.init()
                _local_tts_engine.setProperty("rate", 175)
            _local_tts_engine.say(text)
            _local_tts_engine.runAndWait()
        return True
    except Exception as exc:
        print(f"Jarvis local TTS error: {exc}")
        return False


def clean_for_speech(text: str) -> str:
    """Convert common Markdown formatting into speech-friendly text."""
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"(?<!\w)[*_]([^*_]+)[*_](?!\w)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"https?://\S+", " link ", text)
    text = re.sub(r"[*_~#|>`]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def say(text: str) -> None:
    """Speak using Edge neural TTS; fall back to pyttsx3 on failure."""
    text = clean_for_speech(text.strip())
    if not text:
        return

    print(f"Jarvis: {text}")
    if edge_tts is not None and playsound is not None:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_path = tmp.name
            asyncio.run(_save_edge_audio(text, temp_path))
            playsound(temp_path, block=True)
            return
        except Exception as exc:
            print(f"Jarvis: Edge TTS unavailable ({exc}); using local voice.")
        finally:
            if temp_path:
                # Playback may keep the file open briefly on some platforms.
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    if not _speak_local(text):
        print("Jarvis: No working TTS engine found; response is shown above.")
