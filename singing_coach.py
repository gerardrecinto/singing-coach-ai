#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

from analyze import analyze_audio
from feedback import generate_feedback, print_raw_analysis


def main():
    parser = argparse.ArgumentParser(
        description="Singing Coach AI -- analyze a vocal recording and get feedback"
    )
    parser.add_argument("file", help="Audio or video file to analyze (mp3, wav, mp4, mov, etc.)")
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Print raw analysis numbers only, skip Claude feedback",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {path.name}...")

    try:
        analysis = analyze_audio(str(path))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.no_ai:
        print_raw_analysis(analysis)
        return

    if not args.api_key:
        print(
            "No ANTHROPIC_API_KEY found. Set it as an env var or pass --api-key.\n"
            "To get just the raw numbers, use --no-ai.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Generating feedback...\n")

    try:
        feedback = generate_feedback(analysis, api_key=args.api_key)
        print(feedback)
    except Exception as e:
        print(f"Feedback generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
