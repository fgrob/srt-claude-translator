# Subtitle Translation Guide

## Philosophy

Subtitles are for WATCHING a movie, not reading a book. The translation should be invisible: if the viewer notices they're reading subtitles, you failed.

## Principles

### 1. Naturalness over literalness

Translate the MEANING, not the words. If someone says "It's raining cats and dogs", don't write "Están lloviendo gatos y perros".

A good translation sounds like the character actually speaks that language.

### 2. One block = one idea

```
15
00:01:23,000 --> 00:01:26,000
I think we should go
to the store tomorrow.
```

This is ONE sentence: "Creo que deberíamos ir a la tienda mañana." Read both lines together before translating.

### 3. Freedom in form

If the original uses 2 lines but your translation fits in 1: perfect.
If you need 2 lines when the original had 1: also perfect.

What matters is that it fits in the time and reads well.

### 4. Context is everything

Read the entire chunk before translating. Block 47 might change how you translate block 12.

"He's gone" can be:
- "Se fue" (left the room)
- "Murió" (sad context)
- "Está perdido" (can't find him)

### 5. Respect the register

If the character speaks vulgar, translate vulgar.
If they speak formal, translate formal.
If they speak like a child, translate like a child.

Don't "clean up" the dialogue or make it more elegant than it is.

### 6. Conciseness

The viewer has ~2-3 seconds to read. If your translation is longer than the original, find shorter synonyms or rephrase.

"At this precise moment" → "Now"
"With the objective of" → "To"

### 7. Names

- People: DON'T translate (Michael ≠ Miguel)
- Famous places: use judgment (New York → New York, but London → Londres if common in target language)
- Titles: DO translate (Mr. → Sr.)

### 8. Shared context

You read and write to `context.md`. Use it wisely:

**CHECK** before translating:
- If there's an established term, use it (consistency)
- If there are notes about a character, respect them

**ADD** only if useful for future chunks:
- Invented/fictional term that will repeat
- Character with particular way of speaking
- Relevant narrative context

**DON'T add:**
- Obvious translations
- Information that doesn't affect translation
- Everything that comes to mind (moderation)

## Technical Constraints

### Structure — NEVER modify:
- Timestamps (lines with ` --> `)
- Sequence numbers
- Number of blocks
- Block order

### Text limits:
- Maximum 2 lines per block
- Maximum ~42 characters per line (45 absolute)

### Special formatting — keep intact:
- `<i>text</i>`, `<b>`, `<font color="...">`
- `{\an8}` and other ASS codes

## Accessibility Aids

If you are told to **remove** accessibility aids, follow these rules strictly.
DO NOT translate them to the target language. DELETE them entirely.

**REMOVE these** (they describe sounds for hearing-impaired viewers):
- Sound descriptions in parentheses or brackets: `(sighs)`, `(laughs)`, `[door closes]`, `[gunshot]`, `(CHUCKLES)`, `(PANTING)`
- Speaker labels: `- JOHN:`, `- NARRATOR:`, `BRADLEY:`, `[SAM:]`
  - If the label is the ENTIRE line → delete the whole line
  - If the label has dialogue after it → remove ONLY the label, keep the dialogue:
    `- SAM: I need help` → `- I need help`
    `BRADLEY: Whatever` → `Whatever`
- Pure music indicators with no lyrics: `♪♪`, `♪ ♪`
- Descriptions of music/singing: `♪ singing ♪`, `[singing]`, `(humming)`, `[music playing]`

**KEEP and TRANSLATE these** (they are actual content):
- Song lyrics between ♪: `♪ Yesterday, all my troubles ♪` → `♪ Ayer, todos mis problemas ♪`
- The key distinction: **actual words being sung** vs a **description of the action**
  - `[singing in French]` → REMOVE (description)
  - `♪ La vie en rose ♪` → KEEP and translate (lyrics)

**When in doubt:** if it reads like words someone is singing → lyrics → translate. If it reads like a stage direction → accessibility aid → remove.

**If a block becomes empty after removal → leave it empty (DO NOT delete the block)**

**CRITICAL: "Remove" means DELETE, not translate. `(SIGHS)` must become nothing, NOT `(SUSPIRA)`.** A translated aid is just as wrong as a kept aid.
