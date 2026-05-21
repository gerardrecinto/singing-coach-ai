# analyze your voice recordings
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import librosa

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"}


def extract_audio_from_video(video_path: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    subprocess.run(
        [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "22050", "-ac", "1",
            tmp.name, "-y",
        ],
        check=True,
        capture_output=True,
    )
    return tmp.name


def analyze_pitch(y: np.ndarray, sr: int) -> dict:
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
    )

    voiced_f0 = f0[voiced_flag]

    if len(voiced_f0) == 0:
        return {
            "voiced_frames_pct": 0.0,
            "mean_hz": None,
            "mean_note": None,
            "std_hz": None,
            "pitch_range_semitones": None,
            "stability_score": None,
        }

    mean_hz = float(np.mean(voiced_f0))
    std_hz = float(np.std(voiced_f0))
    midi_notes = librosa.hz_to_midi(voiced_f0)
    pitch_range = float(np.max(midi_notes) - np.min(midi_notes))
    # 1.0 = perfectly locked in, drops toward 0 as wobble increases
    stability = max(0.0, 1.0 - (std_hz / mean_hz))

    return {
        "voiced_frames_pct": round(float(len(voiced_f0) / len(f0) * 100), 1),
        "mean_hz": round(mean_hz, 2),
        "mean_note": librosa.hz_to_note(mean_hz),
        "std_hz": round(std_hz, 2),
        "pitch_range_semitones": round(pitch_range, 1),
        "stability_score": round(stability, 3),
    }


def analyze_rhythm(y: np.ndarray, sr: int) -> dict:
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    if len(beats) < 2:
        return {
            "tempo_bpm": round(float(tempo), 1),
            "beat_count": int(len(beats)),
            "rhythm_regularity": None,
        }

    beat_times = librosa.frames_to_time(beats, sr=sr)
    intervals = np.diff(beat_times)
    regularity = 1.0 - (float(np.std(intervals)) / float(np.mean(intervals)))

    return {
        "tempo_bpm": round(float(tempo), 1),
        "beat_count": int(len(beats)),
        "rhythm_regularity": round(max(0.0, regularity), 3),
    }


def analyze_dynamics(y: np.ndarray, sr: int) -> dict:
    rms = librosa.feature.rms(y=y)[0]
    db = librosa.amplitude_to_db(rms)

    return {
        "mean_db": round(float(np.mean(db)), 1),
        "peak_db": round(float(np.max(db)), 1),
        "dynamic_range_db": round(float(np.max(db) - np.min(db)), 1),
        # closer to 1 means very flat/consistent; lower means more expression/variation
        "consistency_score": round(max(0.0, 1.0 - float(np.std(db)) / 40.0), 3),
    }


def analyze_tone(y: np.ndarray, sr: int) -> dict:
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

    return {
        "spectral_centroid_mean_hz": round(float(np.mean(spectral_centroid)), 1),
        "spectral_rolloff_mean_hz": round(float(np.mean(spectral_rolloff)), 1),
        "mfcc_means": [round(float(m), 3) for m in np.mean(mfccs, axis=1)],
    }


def analyze_audio(file_path: str) -> dict:
    path = Path(file_path)
    ext = path.suffix.lower()

    tmp_path = None
    audio_path = file_path

    if ext in VIDEO_EXTENSIONS:
        print("Extracting audio from video...")
        audio_path = extract_audio_from_video(file_path)
        tmp_path = audio_path
    elif ext not in AUDIO_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    try:
        y, sr = librosa.load(audio_path, sr=None, mono=True)
        duration = float(librosa.get_duration(y=y, sr=sr))

        return {
            "file": path.name,
            "duration_seconds": round(duration, 2),
            "sample_rate": sr,
            "pitch": analyze_pitch(y, sr),
            "rhythm": analyze_rhythm(y, sr),
            "dynamics": analyze_dynamics(y, sr),
            "tone": analyze_tone(y, sr),
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
