# SRT Translator

A translation tool powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code) for SRT subtitle files. Not fast, but remarkably effective.

## What it does

Translates large SRT files (~8000+ lines) without losing context or quality.

**The magic:** As it translates, it builds a shared context file with terminology, character speech patterns, and story notes. Each chunk reads this before translating, so fictional terms stay consistent throughout, and if a character speaks formally in chunk 1, they'll speak formally in chunk 12.

## How it works

1. **Ask**: Target language, regional variant, whether to remove accessibility aids like `(sighs)` or `[gunshot]`
2. **Split**: Large SRT → chunks of ~150 blocks (with 5 overlap blocks for continuity)
3. **Translate**: Sequential subagents (not parallel), each reading and enriching `context.md` so later chunks benefit from earlier discoveries
4. **Validate**: Python scripts verify timestamps unchanged, block count matches
5. **Join**: All chunks → single translated SRT

If interrupted, it can resume from the last validated chunk.

**Note:** Sequential processing means a full movie can take 20+ minutes. This is intentional—parallel would be faster but lose context consistency.

## Usage

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI.

```bash
# Clone and enter
git clone https://github.com/fgrob/srt-translator
cd srt-translator

# Put your subtitle in input/
cp movie.srt input/

# Run Claude Code
claude

# Then just ask:
# "translate the subtitle to Spanish"

# Result will be in output/
```

## Contributing

Open to suggestions on translation quality, chunk sizing, context strategy. Open an issue or PR.

## License

MIT
