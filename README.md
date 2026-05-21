# singing-coach-ai

Feed it a recording of yourself singing, get back actual coaching feedback. Works with audio files (mp3, wav, flac, m4a) and video files (mp4, mov).

Under the hood it uses librosa to pull pitch stability, rhythm, dynamics, and spectral data out of the audio, then sends that analysis to Claude to turn it into readable feedback.

## What it measures

**Pitch** -- fundamental frequency tracking via pyin, stability score, average note, range in semitones, and how much you're drifting (std dev in Hz).

**Rhythm** -- tempo estimate in BPM, beat count, and a regularity score so you can see if you're rushing or dragging.

**Dynamics** -- average and peak levels in dB, dynamic range, and a consistency score.

**Tone** -- spectral centroid and MFCC features that give Claude context about your vocal timbre.

## Setup

```bash
pip install -r requirements.txt
```

For video files you also need ffmpeg:

```bash
# mac
brew install ffmpeg

# ubuntu/debian
apt install ffmpeg
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# analyze and get coaching feedback
python singing_coach.py my_recording.mp3

# video works too
python singing_coach.py practice_session.mp4

# skip the AI, just print the raw numbers
python singing_coach.py my_recording.mp3 --no-ai

# pass the key directly if you don't want to use the env var
python singing_coach.py my_recording.mp3 --api-key sk-ant-...
```

## Example output (--no-ai)

```json
{
  "file": "my_recording.mp3",
  "duration_seconds": 47.3,
  "sample_rate": 44100,
  "pitch": {
    "voiced_frames_pct": 68.2,
    "mean_hz": 220.5,
    "mean_note": "A3",
    "std_hz": 14.3,
    "pitch_range_semitones": 11.8,
    "stability_score": 0.935
  },
  "rhythm": {
    "tempo_bpm": 92.3,
    "beat_count": 71,
    "rhythm_regularity": 0.812
  },
  "dynamics": {
    "mean_db": -18.4,
    "peak_db": -6.1,
    "dynamic_range_db": 22.7,
    "consistency_score": 0.643
  }
}
```

## Requirements

- Python 3.9+
- ffmpeg (video files only)
- Anthropic API key (skip with `--no-ai` if you just want raw numbers)
