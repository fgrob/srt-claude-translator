---
name: translate-srt
description: Translates SRT subtitle files to other languages. Use this skill when the user wants to translate subtitles, .srt files, or requests video/movie translation.
---

# Skill: Translate SRT

## 1. INITIAL SETUP

Before starting:

1. **Load defaults**: Read `config.yml` for default settings (language, variant, country, accessibility aids)
2. **File**: List `input/*.srt` and ask which one to translate
3. **Show defaults**: Display current config in a compact summary, e.g.:
   > Configuración: Español latinoamericano (Chile), eliminar ayudas de accesibilidad
4. **Ask once**: "¿Cambiar algo?" — only ask follow-up questions if the user wants to change something
5. **Check for previous chunks**: If `chunks/` has files, ask right away: "Hay chunks de una traducción anterior. ¿Retomar o empezar de cero?" — don't spend time checking `.source` or analyzing first

Save the final answers to pass them to subagents.

## 2. PROCESS

```
1. If not resuming, clean from previous process: empty chunks/, translated/, create fresh context.md with:
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

REMOVE these (they describe sounds for hearing-impaired viewers):
- Sound descriptions: `(sighs)`, `(laughs)`, `[door closes]`, `[gunshot]`
- Speaker labels: `- JOHN:`, `- NARRATOR:`
- Pure music indicators with no lyrics: `♪♪`, `♪ ♪`
- Descriptions of music/singing: `♪ singing ♪`, `[singing]`, `(humming)`, `[music playing]`

KEEP and TRANSLATE these (they are actual content):
- Song lyrics between ♪: `♪ Yesterday, all my troubles ♪` → `♪ Ayer, todos mis problemas ♪`
- Song lyrics in any format — the key distinction is whether the text contains **actual words being sung** vs a **description of the action of singing/music**. Examples:
  - `[singing in French]` → REMOVE (description of action)
  - `♪ La vie en rose ♪` → KEEP and translate (actual lyrics)
  - `# When the morning comes #` → KEEP and translate (lyrics, `#` is sometimes used instead of `♪`)
- When in doubt: if it reads like words someone is singing, it's lyrics → translate. If it reads like a stage direction, it's an accessibility aid → remove.

If a block becomes empty after removal → leave it empty (DO NOT delete the block)

## 5. RESUME WORK

Handled in step 1.5 of INITIAL SETUP: if `chunks/` has files, ask the user directly whether to resume or start fresh. No need to check `.source` first — just ask.

- If **RESUME**: first verify that chunks match an existing file in `input/` by checking `chunks/.source`. If the source file no longer exists in `input/`, inform the user and start fresh instead. If it matches, validate existing translated chunks and continue from first invalid/missing.
- If **START FRESH**: clean everything and proceed normally
