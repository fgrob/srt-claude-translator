---
name: translate-srt
description: Translates SRT subtitle files to other languages. Use this skill when the user wants to translate subtitles, .srt files, or requests video/movie translation.
---

# Skill: Translate SRT

## 1. INITIAL QUESTIONS

Before starting, ask:

1. **File**: List `input/*.srt` and ask which one to translate
2. **Target language**: What language?
   - If "Spanish" → Spain or Latin America?
   - If Latin American → Country preference for tiebreakers? (only used when choosing between equally valid regional variants)
3. **Accessibility aids**: Remove `(sighs)`, `[gunshot]`, `♪ music ♪`?
   - Remove (recommended) / Keep

Save the answers to pass them to subagents.

## 2. PROCESS

```
1. Clean from previous process: empty chunks/, translated/, create fresh context.md with:
   ```
   # Shared Context

   ## Terms

   ## Characters

   ## Notes
   ```
2. python hooks/split.py input/<file>
3. For each chunk in chunks/ (SEQUENTIALLY):
   → Launch SUBAGENT to translate that chunk
   → Wait for it to finish and validate
   → If fails 3 times, abort
4. python hooks/join.py
5. Report: file ready in output/
   (chunks/, translated/ and context.md remain for review)
```

## 3. TRANSLATION SUBAGENT

For each chunk, launch a subagent with this prompt:

```
You are a subtitle translator. Your task is to translate ONE chunk of an SRT file.

CONFIGURATION:
- Target language: [language chosen by user]
- Variant: [spain/latin + country if applicable]
- Accessibility aids: [remove/keep]

BEFORE TRANSLATING, READ:
1. .claude/skills/translate-srt/TRANSLATION_GUIDE.md (translation principles)
2. context.md (terms, characters and notes from previous chunks)
3. The chunk: chunks/[chunk_name]

TRANSLATE:
- Follow the guide's principles
- Use terms from context if they appear
- If you discover something future chunks SHOULD know (special term, how a character speaks, etc.), add it to context.md
- DON'T overdo it: only truly useful information

SAVE:
- Translation in: translated/[same_chunk_name]
- If you added info, update context.md

VALIDATE:
- Run: python hooks/validate_chunk.py chunks/[chunk] translated/[chunk]
- If it fails, correct and retry (max 3 attempts)
- Report OK or the final error
```

## 4. TECHNICAL CONSTRAINTS

**NEVER modify:**
- Timestamps (lines with ` --> `)
- Sequence numbers
- Number of blocks
- Block order

**Text limits:**
- Maximum 2 lines per block
- Maximum ~42 characters per line (45 absolute)

**Special formatting - keep intact:**
- `<i>text</i>`, `<b>`, `<font color="...">`
- `{\an8}` and other ASS codes

**If removing accessibility aids:**
- Remove `(text)`, `[text]`, `♪ text ♪`, `- NAME:`
- If block becomes empty → leave it empty (DO NOT delete the block)

## 5. RESUME WORK

If there are chunks in `chunks/`:
1. Check `chunks/.source` to see which file they came from
2. If DIFFERENT file (or .source missing) → clean everything and start fresh
3. If SAME file → ask user: "Resume previous translation or start fresh?"
   - If RESUME: validate existing translated chunks, continue from first invalid/missing
   - If START FRESH: clean everything
