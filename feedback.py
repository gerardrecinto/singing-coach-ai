import json
import anthropic


def generate_feedback(analysis: dict, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)

    pitch = analysis.get("pitch", {})
    rhythm = analysis.get("rhythm", {})
    dynamics = analysis.get("dynamics", {})

    prompt = f"""You are an experienced vocal coach. A student recorded themselves singing and I ran it through audio analysis. Give them honest, specific feedback they can act on.

Recording: {analysis.get("file", "unknown")} — {analysis.get("duration_seconds", 0)} seconds

Pitch:
- Voiced frames: {pitch.get("voiced_frames_pct", 0)}% of the recording
- Average pitch: {pitch.get("mean_hz")} Hz ({pitch.get("mean_note", "unknown")})
- Stability score: {pitch.get("stability_score")} out of 1.0 (1.0 = rock solid, near 0 = drifting constantly)
- Pitch range: {pitch.get("pitch_range_semitones")} semitones
- Pitch wobble (std dev): {pitch.get("std_hz")} Hz

Rhythm:
- Estimated tempo: {rhythm.get("tempo_bpm")} BPM
- Rhythm regularity: {rhythm.get("rhythm_regularity")} out of 1.0

Dynamics:
- Average level: {dynamics.get("mean_db")} dB
- Dynamic range: {dynamics.get("dynamic_range_db")} dB
- Consistency: {dynamics.get("consistency_score")} out of 1.0

Give feedback in plain sections: Pitch, Rhythm, Dynamics, and 2-3 specific things to practice. Be direct. Skip the encouragement filler."""

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def print_raw_analysis(analysis: dict) -> None:
    print(json.dumps(analysis, indent=2))
