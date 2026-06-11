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
5. **Check locale profile**: Derive the locale code from language+country using BCP 47 format (language tag + region tag): Spanish+Chile → `es-CL`, Spanish+Argentina → `es-AR`, Spanish+Mexico → `es-MX`, English+US → `en-US`, Portuguese+Brazil → `pt-BR`, French+France → `fr-FR`. Check if `locales/<locale>.md` exists.
   - If it **exists**: silently use it (mention it in the config summary, e.g. "Perfil de localización: es-CL ✓")
   - If it **doesn't exist**: tell the user and offer to generate it before proceeding:
     > No tengo perfil de localización para es-CL. ¿Lo genero ahora? (recomendado)
     - If yes → run the **LOCALE GENERATION** flow below, then continue
     - If no → proceed without locale profile (translation will be less precise)
6. **Check for previous chunks**: If `chunks/` has files, ask right away with numbered options:
   > Hay chunks anteriores. ¿0: nuevo, 1: retomar?

Save the final answers to pass them to subagents.

## 1.5 LOCALE GENERATION

When a locale profile is missing, generate it with a subagent:

**Subagent prompt:**
```
You are a professional linguist specializing in dialectal variation and subtitle translation.

Write a compact locale profile for: [LOCALE CODE] — [LANGUAGE] as spoken in [COUNTRY/REGION].

This file is read by a translation model before translating subtitles. The model already knows the language fluently. Your job is NOT to teach it — it is to ANCHOR the 4–5 dialectal axes that distinguish this locale from others, so the model doesn't drift toward a generic or neighboring variant.

Structure the profile around these linguistic axes:

## 1. Pronominal system
Which second-person pronoun (tú / vos / usted)? Any register exceptions? One or two lines max.

## 2. Discourse markers
The 3–5 oral markers that immediately signal this locale to a native ear. Discourse markers are functional words that signal turn-taking, register, or conversational rhythm — not content words or culturally untranslatable nouns. For each: the word/phrase, what it means, and one-line guidance on when to use it in subtitles (sparingly? freely? only in highly colloquial exchanges?).

## 3. High-frequency lexical anchors
The 8–10 words that come up constantly in informal dialogue and have a locale-specific form. Don't list obvious vocabulary — only words where the model might default to a different region's variant. For each: the correct local word and what NOT to use instead. Only include words where a wrong regional variant exists — if a word simply has no translation, it doesn't belong here.

## 4. Profanity system
Don't list translations of English swearwords. Instead: describe HOW profanity works in this locale. What is the most versatile/central swearword? What is the strongest? How is intensity signaled? Are there words that shift meaning entirely based on tone?

For every word you mention: give the spelling to use in subtitles — one spelling only, the correct one for informal written dialogue. Do not mention alternative spellings, formal spellings, or academic spellings. One word, one form.

Only include words you are certain are specific to this locale. If a word is generic Latin American or pan-Hispanic, omit it — do not pad the list.

## 5. What NOT to do
List 5–8 specific words or constructions from neighboring/related variants that would immediately sound wrong to a native of this locale. Just the words — no need to explain why.

Total length: 30–40 lines. No filler. No introductions. No conclusions. Concrete examples only.

Save the result to: locales/[LOCALE].md
Working directory: the root of the srt_claude_translator project
```

After the subagent finishes:
- Show the user a brief summary of what was generated
- Ask: "¿Quieres revisar o ajustar algo antes de continuar?"
- If yes → show the file content and let them edit; if no → proceed

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
5. Delete chunks/ and translated/ contents (the join succeeded — nothing to resume)
6. Report: file ready in output/
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
1. .claude/skills/translate-srt/TRANSLATION_GUIDE.md (translation principles AND technical constraints)
2. locales/[LOCALE].md — locale profile: pronominal system, discourse markers, lexical anchors, profanity system, and what NOT to use. This file anchors the dialect — follow it strictly.
3. context.md (terms, characters and notes from previous chunks)
4. The chunk: chunks/[chunk_name]

[IF ACCESSIBILITY AIDS = REMOVE, INCLUDE THIS BLOCK:]
ACCESSIBILITY AIDS — REMOVE:
You MUST delete all accessibility aids. Do NOT translate them to the target language.
- Delete sound descriptions: (sighs), (PANTING), [door closes], (CHUCKLES), etc.
- Delete speaker labels: - JOHN:, BRADLEY:, - NARRATOR:, [SAM:]
  - If label has dialogue after it, remove ONLY the label, keep the dialogue: "- SAM: I need help" → "- I need help"
- Delete pure music indicators: ♪♪, ♪ ♪
- Delete music/singing descriptions: [singing], (humming), [music playing]
- KEEP and translate actual song lyrics: ♪ words being sung ♪
- If a block becomes empty after removal, leave it empty (do NOT delete the block)
- CRITICAL: "Remove" means DELETE completely. (SIGHS) must become nothing, NOT (SUSPIRA). A translated aid is still a failure.
[END BLOCK]

TRANSLATE:
- Follow the guide's principles
- Use terms from context if they appear
- If you discover something future chunks SHOULD know (special term, how a character speaks, etc.), add it to context.md
- DON'T overdo it: only truly useful information

SAVE:
- Translation in: translated/[same_chunk_name]
- If you added info, update context.md

VALIDATE:
- Run: python hooks/validate_chunk.py chunks/[chunk] translated/[chunk] [add --check-aids if accessibility aids = remove]
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
