# Architecture

## Data Flow

```mermaid
flowchart TD
    A[audio/video file] --> B{video?}
    B -- yes --> C[ffmpeg: extract audio]
    B -- no --> D[librosa load]
    C --> D
    D --> E[pyin pitch analysis]
    D --> F[beat_track rhythm]
    D --> G[rms dynamics]
    D --> H[mfcc tone/spectral]
    E & F & G & H --> I[structured JSON]
    I --> J[Claude API]
    J --> K[coaching feedback]
```

## Analysis Pipeline Sequence

```mermaid
sequenceDiagram
    participant User
    participant singing_coach.py
    participant analyze.py
    participant ffmpeg
    participant librosa
    participant feedback.py
    participant Claude API

    User->>singing_coach.py: python singing_coach.py recording.mp3
    singing_coach.py->>analyze.py: analyze_audio(path)
    analyze.py->>ffmpeg: extract audio (if video)
    ffmpeg-->>analyze.py: temp .wav
    analyze.py->>librosa: pitch/rhythm/dynamics/tone analysis
    librosa-->>analyze.py: raw arrays
    analyze.py-->>singing_coach.py: structured dict

    alt --no-ai flag
        singing_coach.py->>stdout: raw JSON
    else default
        singing_coach.py->>feedback.py: generate_feedback(analysis)
        feedback.py->>Claude API: analysis + coaching prompt
        Claude API-->>feedback.py: coaching text
        feedback.py-->>singing_coach.py: coaching string
        singing_coach.py->>stdout: print coaching
    end
```

## Signal Analysis Map

```mermaid
flowchart LR
    W[Audio waveform]
    W --> P[pyin]
    W --> B[beat_track]
    W --> R[rms]
    W --> M[mfcc]

    P --> P1[pitch Hz]
    P --> P2[stability score]
    P --> P3[pitch range semitones]

    B --> B1[tempo BPM]
    B --> B2[rhythm regularity]

    R --> R1[dynamics dB mean/peak]
    R --> R2[dynamic range dB]
    R --> R3[consistency score]

    M --> M1[spectral centroid Hz]
    M --> M2[spectral rolloff Hz]
    M --> M3[MFCC means — tone quality]
```

## Design Decisions

**Why librosa over other libraries**
librosa is the de-facto standard for audio ML in Python. Its `pyin` algorithm is a probabilistic refinement of the YIN pitch estimator — it returns per-frame voiced/unvoiced flags alongside F0 estimates, which is exactly what you need to separate singing from silence and measure pitch stability without manual thresholding.

**Why Claude for coaching instead of rule-based thresholds**
Rule-based logic can compute numbers (stability score 0.72, range 14 semitones) but cannot turn them into actionable singing advice. Claude understands musical context: it knows that a 0.72 stability score on a long sustained note means something different than on a fast run, and it can frame feedback the way a real vocal coach would.

**Why `--no-ai` mode**
Separating analysis from feedback lets engineers run the analysis pipeline without an API key — useful for CI batch jobs, automated regression tests, or debugging the signal processing layer in isolation. The structured JSON output is deterministic and diff-able.

**Why structured JSON as the intermediate representation**
The analysis layer (`analyze.py`) is deterministic and fully unit-testable. The feedback layer (`feedback.py`) is non-deterministic AI. Keeping them separate behind a clean dict interface means you can test the analysis math precisely, mock the Claude call in tests, and swap out either layer independently.
