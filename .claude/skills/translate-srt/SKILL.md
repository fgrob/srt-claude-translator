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

When a locale profile is missing, generate it through a 4-stage flow:
**research → mark bets → user audits the bets → save corrections as traps.**

The hardest part of any locale profile is the **profanity system** (section 4):
the translation model tends to grab one local swearword and use it as a universal
stand-in for "fuck/shit", ignoring that each word has a POLARITY (praise vs insult),
a CONTEXT where it works, and TRAPS where it backfires (e.g. in es-CL, *como la
mierda* means "badly", so using it to translate a compliment inverts the meaning).
A native speaker's ear is the only reliable detector of these. So the flow makes the
model do the legwork and mark its uncertain calls, then the user audits ONLY those.

The profile MUST follow the structure in `locales/_TEMPLATE.md`. Read that template
first — it defines all sections, especially 4a–4d.

### Stage 1 — Research & draft (subagent)

**Subagent prompt:**
```
You are a professional linguist specializing in dialectal variation and subtitle translation.

Write a locale profile for: [LOCALE CODE] — [LANGUAGE] as spoken in [COUNTRY/REGION].

Working directory: the root of the srt_claude_translator project.

FIRST: read locales/_TEMPLATE.md. Your output MUST follow its exact structure
(sections 1, 2, 3, 4a, 4b, 4c, 4d, 5). Fill every section.

This file is read by a translation model before translating subtitles. The model
already knows the language fluently. Your job is NOT to teach it — it is to ANCHOR
the dialect so it doesn't drift toward a generic/neighboring variant, AND to warn it
about the specific swearwords/idioms that trick it (section 4c).

RESEARCH: use web search to verify profanity usage, polarity, and traps — do NOT
rely on memory alone for the profanity section. Confirm against multiple sources.

CRITICAL — mark your bets: profanity and idioms have polarity and context that are
easy to get wrong. Any entry you are NOT 100% certain a native speaker would say —
ESPECIALLY in sections 4a–4c — append `⚠️ APUESTA: <why you're unsure>` at the end
of that line. Be honest and over-mark rather than under-mark: these are what the
user will audit. Do NOT declare any single word a universal "fuck" stand-in.

One spelling per word (informal subtitle spelling). Concrete examples only. No filler.

Save the result to: locales/[LOCALE].md

Your final message must list, separately, EVERY line you marked ⚠️ APUESTA, so the
user can audit them without reading the whole file.
```

### Stage 2 — User audits the bets (MANDATORY on first creation)

After the subagent finishes:
1. Show the user the list of ⚠️ APUESTA lines (NOT the whole file) in a compact form:
   > Generé el perfil es-CL. Marqué N apuestas que necesito que audites (tu oído manda):
   > 1. "como la mierda" como elogio — no estoy seguro de la polaridad
   > 2. ...
2. **Do NOT proceed to translation until the user resolves these.** This audit is
   mandatory the first time a locale is created — the profile drives every future
   episode, so the friction is worth it. (Once audited, the profile is trusted and
   this never runs again for that locale.)
3. For each bet, the user confirms ✅ or corrects it. Apply their answer to the file.

### Stage 3 — Save corrections as traps

Every correction the user makes is dialect knowledge worth keeping. For each one,
add (or refine) a row in the **section 4c trap table**: the word, ✅ where it works,
❌ where it doesn't → the correction. Remove the `⚠️ APUESTA` marker once resolved.
This is how the profile learns the user's ear over time.

### Later runs

When a trusted profile already exists, NEVER regenerate or re-audit it. If the user
later reports the model misused a word, just add a new trap row to section 4c — no
full regeneration.

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
