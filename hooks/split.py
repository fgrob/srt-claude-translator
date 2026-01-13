#!/usr/bin/env python3
"""
Split SRT file into chunks for translation.

Usage: python split.py input/<filename.srt>

Generates chunks of ~150 blocks in chunks/ directory.
Each chunk (except the first) includes 5 context blocks from the previous chunk.
"""

import sys
import os
import re
from pathlib import Path

BLOCKS_PER_CHUNK = 150
CONTEXT_BLOCKS = 5

def parse_srt_blocks(content):
    """Parse SRT content into list of blocks."""
    blocks = []
    current_block = []

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines at the start
        if not line.strip() and not current_block:
            i += 1
            continue

        # Check if this is the start of a new block (sequence number)
        if re.match(r'^\d+$', line.strip()) and current_block:
            # Save the previous block
            blocks.append('\n'.join(current_block))
            current_block = []

        current_block.append(line)

        # Check if we hit an empty line (end of block)
        if not line.strip() and current_block:
            # Check if the block has content (not just empty lines)
            block_content = '\n'.join(current_block).strip()
            if block_content and re.match(r'^\d+\s*\n', block_content):
                blocks.append('\n'.join(current_block))
                current_block = []

        i += 1

    # Don't forget the last block
    if current_block:
        block_content = '\n'.join(current_block).strip()
        if block_content:
            blocks.append('\n'.join(current_block))

    return blocks


def parse_srt_blocks_v2(content):
    """Parse SRT content into list of blocks (improved version)."""
    blocks = []

    # Split by double newlines or by detecting block patterns
    # A block is: number, timestamp, text lines, empty line

    lines = content.split('\n')
    current_block_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line is a sequence number (start of new block)
        is_seq_number = re.match(r'^\d+$', line.strip())

        # Check if next line is a timestamp
        next_is_timestamp = False
        if i + 1 < len(lines):
            next_is_timestamp = ' --> ' in lines[i + 1]

        # If we found a sequence number followed by timestamp, and we have a previous block
        if is_seq_number and next_is_timestamp and current_block_lines:
            # Save previous block
            block_text = '\n'.join(current_block_lines)
            if block_text.strip():
                blocks.append(block_text)
            current_block_lines = []

        current_block_lines.append(line)
        i += 1

    # Save last block
    if current_block_lines:
        block_text = '\n'.join(current_block_lines)
        if block_text.strip():
            blocks.append(block_text)

    return blocks


def format_block(block):
    """Ensure block ends with a blank line."""
    block = block.rstrip()
    return block + '\n'


def create_chunks(blocks, output_dir):
    """Create chunk files from blocks."""
    total_blocks = len(blocks)
    chunks = []

    i = 0
    chunk_num = 1

    while i < total_blocks:
        chunk_blocks = []

        # Add context blocks for chunks after the first
        if chunk_num > 1 and i >= CONTEXT_BLOCKS:
            context_start = i - CONTEXT_BLOCKS
            context_blocks = blocks[context_start:i]

            chunk_blocks.append('=== CONTEXT (DO NOT TRANSLATE, only for understanding continuity) ===')
            for block in context_blocks:
                chunk_blocks.append(format_block(block))
            chunk_blocks.append('=== END CONTEXT ===\n')

        # Add blocks for this chunk
        end = min(i + BLOCKS_PER_CHUNK, total_blocks)
        for block in blocks[i:end]:
            chunk_blocks.append(format_block(block))

        # Write chunk file
        chunk_filename = f'chunk_{chunk_num:03d}.srt'
        chunk_path = output_dir / chunk_filename

        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(chunk_blocks))

        chunks.append({
            'filename': chunk_filename,
            'blocks': end - i,
            'start': i + 1,
            'end': end
        })

        i = end
        chunk_num += 1

    return chunks


def main():
    if len(sys.argv) < 2:
        print("Error: Must specify an SRT file")
        print("Usage: python split.py input/<file.srt>")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Error: File '{input_file}' does not exist")
        sys.exit(1)

    # Determine base directory (where the script is run from)
    script_dir = Path(__file__).parent.parent
    chunks_dir = script_dir / 'chunks'

    # Create chunks directory if needed
    chunks_dir.mkdir(exist_ok=True)

    # Clear existing chunks
    for f in chunks_dir.glob('chunk_*.srt'):
        f.unlink()

    # Save source filename for resume detection
    source_file = chunks_dir / '.source'
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(input_file.name)

    # Read and parse input file
    print(f"Reading file: {input_file}")
    with open(input_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        content = f.read()

    # Normalize line endings (CRLF -> LF)
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    blocks = parse_srt_blocks_v2(content)
    total_blocks = len(blocks)

    if total_blocks == 0:
        print("Error: No valid SRT blocks found in file")
        sys.exit(1)

    print(f"Total blocks found: {total_blocks}")

    # Create chunks
    chunks = create_chunks(blocks, chunks_dir)

    # Print summary
    print(f"\nSummary:")
    print(f"  - Total blocks: {total_blocks}")
    print(f"  - Chunks generated: {len(chunks)}")
    print(f"\nChunks created in {chunks_dir}/:")
    for chunk in chunks:
        print(f"  - {chunk['filename']}: blocks {chunk['start']}-{chunk['end']} ({chunk['blocks']} blocks)")


if __name__ == '__main__':
    main()
