#!/usr/bin/env python3
"""
Join translated SRT chunks into a single file.

Usage: python join.py

Reads all chunk_XXX.srt files from translated/ directory,
removes context sections, re-numbers blocks, and outputs
to output/ directory.

Preserves empty blocks (for removed accessibility aids) to maintain sync.
"""

import sys
import os
import re
from pathlib import Path


def remove_context_section(content):
    """Remove the context section from chunk content."""
    lines = content.split('\n')
    result = []
    in_context = False

    for line in lines:
        if '=== CONTEXT' in line:
            in_context = True
            continue
        if '=== END CONTEXT ===' in line:
            in_context = False
            continue
        if not in_context:
            result.append(line)

    return '\n'.join(result)


def parse_blocks(content):
    """
    Parse SRT content into list of blocks.
    Each block is a dict with: seq_num, timestamp, text_lines
    Preserves empty blocks (valid when accessibility aids removed).
    """
    blocks = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        # Skip empty lines between blocks
        while i < len(lines) and not lines[i].strip():
            i += 1

        if i >= len(lines):
            break

        # Check for sequence number
        if not re.match(r'^\d+$', lines[i].strip()):
            i += 1
            continue

        seq_num = lines[i].strip()
        i += 1

        if i >= len(lines):
            break

        # Check for timestamp
        if ' --> ' not in lines[i]:
            continue

        timestamp = lines[i]
        i += 1

        # Collect text lines until empty line or next block
        text_lines = []
        while i < len(lines):
            line = lines[i]

            # Empty line marks end of block
            if not line.strip():
                i += 1
                break

            # Check if this is the start of a new block
            if re.match(r'^\d+$', line.strip()):
                if i + 1 < len(lines) and ' --> ' in lines[i + 1]:
                    break

            text_lines.append(line)
            i += 1

        # Keep block even if text_lines is empty (accessibility aids removed)
        blocks.append({
            'seq_num': seq_num,
            'timestamp': timestamp,
            'text_lines': text_lines
        })

    return blocks


def format_output(blocks):
    """Format blocks into SRT output, renumbering sequentially."""
    output_lines = []
    empty_count = 0

    for idx, block in enumerate(blocks, 1):
        # Add sequence number (renumbered)
        output_lines.append(str(idx))

        # Add timestamp
        output_lines.append(block['timestamp'])

        # Add text lines (may be empty)
        if block['text_lines']:
            for line in block['text_lines']:
                output_lines.append(line)
        else:
            empty_count += 1

        # Empty line to separate blocks
        output_lines.append('')

    return '\n'.join(output_lines), empty_count


def get_original_filename():
    """Try to determine the original filename from input directory."""
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / 'input'

    srt_files = list(input_dir.glob('*.srt'))
    if len(srt_files) == 1:
        return srt_files[0].name
    elif len(srt_files) > 1:
        # Return most recently modified
        srt_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return srt_files[0].name
    else:
        return 'translated.srt'


def main():
    script_dir = Path(__file__).parent.parent
    translated_dir = script_dir / 'translated'
    output_dir = script_dir / 'output'

    # Check translated directory exists
    if not translated_dir.exists():
        print("Error: Directory 'translated/' does not exist")
        sys.exit(1)

    # Get all chunk files sorted
    chunk_files = sorted(translated_dir.glob('chunk_*.srt'))

    if not chunk_files:
        print("Error: No chunk_*.srt files found in translated/")
        sys.exit(1)

    print(f"Found {len(chunk_files)} translated chunks")

    # Process all chunks
    all_blocks = []

    for chunk_file in chunk_files:
        print(f"  Processing: {chunk_file.name}")

        with open(chunk_file, 'r', encoding='utf-8-sig') as f:
            content = f.read().replace('\r\n', '\n').replace('\r', '\n')

        # Remove context section
        content = remove_context_section(content)

        # Parse blocks
        blocks = parse_blocks(content)
        all_blocks.extend(blocks)

    print(f"\nTotal blocks collected: {len(all_blocks)}")

    # Format output
    output_content, empty_count = format_output(all_blocks)

    # Create output directory if needed
    output_dir.mkdir(exist_ok=True)

    # Determine output filename
    output_filename = get_original_filename()
    output_path = output_dir / output_filename

    # Write output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    # Summary
    print(f"\nSummary:")
    print(f"  - Chunks processed: {len(chunk_files)}")
    print(f"  - Blocks in final file: {len(all_blocks)}")
    if empty_count > 0:
        print(f"  - Empty blocks (removed aids): {empty_count}")
    print(f"  - Generated file: {output_path}")


if __name__ == '__main__':
    main()
