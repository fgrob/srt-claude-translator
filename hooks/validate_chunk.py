#!/usr/bin/env python3
"""
Validate translated SRT chunk against original.

Usage: python validate_chunk.py chunks/<chunk> translated/<chunk>

Validates:
- Same number of blocks
- Timestamps unchanged (byte by byte)
- Sequence numbers unchanged
- Text lines <= 45 characters (warning)
- Max 2 text lines per block (error)
- Allows empty text blocks (for removed accessibility aids)

Exit code 0 if OK, 1 if errors found.
"""

import sys
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
    Parse SRT content into structured blocks.
    Returns list of dicts with: seq_num, timestamp, text_lines
    Handles empty text blocks (valid when accessibility aids are removed).
    """
    content = remove_context_section(content)
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

        timestamp = lines[i].rstrip()  # Normalize trailing whitespace
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
                # Peek ahead to see if next line is timestamp
                if i + 1 < len(lines) and ' --> ' in lines[i + 1]:
                    break

            text_lines.append(line)
            i += 1

        # Block is valid even with empty text_lines (accessibility aids removed)
        blocks.append({
            'seq_num': seq_num,
            'timestamp': timestamp,
            'text_lines': text_lines
        })

    return blocks


def validate(original_path, translated_path):
    """
    Validate translated chunk against original.
    Returns tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Read files (utf-8-sig handles BOM, normalize line endings)
    try:
        with open(original_path, 'r', encoding='utf-8-sig') as f:
            original_content = f.read().replace('\r\n', '\n').replace('\r', '\n')
    except Exception as e:
        return False, [f"Error reading original file: {e}"], []

    try:
        with open(translated_path, 'r', encoding='utf-8-sig') as f:
            translated_content = f.read().replace('\r\n', '\n').replace('\r', '\n')
    except Exception as e:
        return False, [f"Error reading translated file: {e}"], []

    # Parse blocks
    original_blocks = parse_blocks(original_content)
    translated_blocks = parse_blocks(translated_content)

    # Validation 1: Same number of blocks
    if len(original_blocks) != len(translated_blocks):
        errors.append(
            f"Block count: original {len(original_blocks)}, "
            f"translated {len(translated_blocks)}"
        )
        return False, errors, warnings

    # Count stats
    empty_blocks = 0

    # Validate each block
    for idx, (orig, trans) in enumerate(zip(original_blocks, translated_blocks), 1):

        # Validation 2: Sequence number unchanged
        if orig['seq_num'] != trans['seq_num']:
            errors.append(
                f"Block {idx}: sequence number modified. "
                f"Original: {orig['seq_num']}, Translated: {trans['seq_num']}"
            )

        # Validation 3: Timestamp unchanged (byte by byte)
        if orig['timestamp'] != trans['timestamp']:
            errors.append(
                f"Block {idx}: timestamp modified. "
                f"Original: '{orig['timestamp']}', Translated: '{trans['timestamp']}'"
            )

        # Track empty blocks (valid, but worth noting)
        if len(trans['text_lines']) == 0:
            empty_blocks += 1

        # Validation 4: Max 2 text lines (only if has text)
        if len(trans['text_lines']) > 2:
            errors.append(
                f"Block {idx}: has {len(trans['text_lines'])} text lines, max 2"
            )

        # Validation 5: Line length (warning only)
        for line_idx, line in enumerate(trans['text_lines'], 1):
            line_len = len(line.rstrip())
            if line_len > 45:
                warnings.append(
                    f"Block {idx}, line {line_idx}: exceeds 45 characters "
                    f"(has {line_len})"
                )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, empty_blocks


def main():
    if len(sys.argv) < 3:
        print("Error: Must specify original and translated files")
        print("Usage: python validate_chunk.py chunks/<chunk> translated/<chunk>")
        sys.exit(1)

    original_path = Path(sys.argv[1])
    translated_path = Path(sys.argv[2])

    if not original_path.exists():
        print(f"Error: Original file '{original_path}' does not exist")
        sys.exit(1)

    if not translated_path.exists():
        print(f"Error: Translated file '{translated_path}' does not exist")
        sys.exit(1)

    result = validate(original_path, translated_path)

    # Handle both old (3-tuple) and new (4-tuple) return format
    if len(result) == 4:
        is_valid, errors, warnings, empty_blocks = result
    else:
        is_valid, errors, warnings = result
        empty_blocks = 0

    # Print warnings first
    for warning in warnings:
        print(f"WARNING: {warning}")

    # Print errors
    for error in errors:
        print(f"ERROR: {error}")

    if is_valid:
        status_parts = []
        if warnings:
            status_parts.append(f"{len(warnings)} warnings")
        if empty_blocks > 0:
            status_parts.append(f"{empty_blocks} empty blocks")

        if status_parts:
            print(f"\nOK ({', '.join(status_parts)})")
        else:
            print("OK")
        sys.exit(0)
    else:
        print(f"\nFAILED: {len(errors)} errors found")
        sys.exit(1)


if __name__ == '__main__':
    main()
