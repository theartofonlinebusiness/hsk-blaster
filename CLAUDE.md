# HSK Blaster — Project Context for Claude

This file is auto-loaded by Claude Code at session start. Read it fully before touching any code.

---

## QA & Review Protocol (follow this every session)

### After every session that changes gameplay code:
Run `/qa` before reporting anything as done. Gameplay code = anything touching:
- Wave spawning, targeting, bullet logic, scoring
- Audio (TTS, SFX)
- Character rendering or sizing
- Input handling (typing, space bar, backspace)

**How to run QA for this project:**
1. Ensure `serve.py` is running (`python3 serve.py` from the project dir, serves on port 7777)
2. Run `/qa` — it will open the browser, play the game, and verify core loops work
3. Fix anything it finds before reporting done to the user

### After every 3–4 sessions of feature work:
Run `/code-review` to catch accumulated drift, dead code, broken state resets, undefined variables.

### Before any "this is ready" statement:
- QA must have passed for that session's changes
- No exceptions — the `margin` undefined bug shipped because there was no QA pass

### When to run Office Hours (`/office-hours`):
- At the start of any session where the user describes a new feature direction
- Before building anything the user has described vaguely or in multiple contradictory ways
- When scope is unclear — spend 5 minutes in office hours rather than 30 minutes rebuilding

---

## What This Is

A browser-based Chinese character typing shooter (ZType-style) that also genuinely teaches HSK vocabulary. Single HTML file — `index.html`. No frameworks, no backend, no build step. Open in a browser and play.

The dual mandate: **fun first, education second — but education built into every moment of the fun.**

---

## HSK Version

We use **HSK 3.0 (2021 new standard)**, levels 1–7. This replaced the old 6-level system.

- HSK 1: ~500 words (we have ~130 representative entries)
- HSK 2: ~800 words (~110 entries)
- HSK 3: ~1000 words (~100 entries)
- HSK 4: ~1000 words (~100 entries)
- HSK 5–7: ~55–40 entries each (representative samples)

**Our word lists are NOT complete HSK word lists.** They are curated representative samples. The game is still educationally valid — the most common, high-value words are included.

Each word entry: `[characters, toned_pinyin, english]` → processed into `{c, p, e, t, single}` where `t` = toneless pinyin (for matching), `single` = c.length===1.

**Pinyin input**: toneless (type "ni" for 你, "zhongguo" for 中国). `v` maps to `ü` (Chinese keyboard convention). Toned pinyin is displayed but not required for input.

**Erhua (儿化)**: Words ending in 儿 as a suffix (e.g. 一点儿) auto-complete the 儿 — player only types the preceding syllable.

---

## Game Mechanics Architecture

### Play Area
- **Desktop**: 860px wide, centered on screen. Dark overlay fills sides.
- **Mobile**: 390px wide. Toggle on menu.
- `PLAY_W` (let, not const) and `PLAY_X` (left edge) — both updated on resize and mode toggle.
- All character spawning, clamping, ship position use `PLAY_X` and `PLAY_W`.

### Wave System (count-based, NOT time-based)
```
Wave 1: 6 words total, max 2 simultaneous, 2.4s spawn gap, speedMult=0.75
Each wave: wordsPerWave=4+wave*2, maxSim=min(12, 2+floor(wave/2))
           spawnInterval=max(800, 2400-wave*130), speedMult=0.75+(wave-1)*0.09
```
Wave states: `'fighting'` → `'finishing'` (2.8s clear screen) → `'starting'` (3s 3-2-1 countdown) → `'fighting'`

**Wave names** (in `WAVE_NAMES` dict): Wave 1="First Steps", Wave 5="The Real Test", Wave 10="Master Level", etc. Shown during countdown. Turn numbers into narrative milestones.

### Difficulty Levers
- Wave 1: player feels like a genius (2 slow words)
- Waves 2–4: simultaneous words increase before speed does
- Wave 5+: motherships start appearing (18% chance)
- Wave 2+: golden words start (8% chance, 3× points, faster fall)
- Speed only reaches "base" at wave 4; exceeds base from wave 5 onward

### Character Sizing & Speed
- **Desktop**: `fontSize = 70 + sizeRoll*105` (70–175px)
- **Mobile**: `fontSize = 50 + sizeRoll*50` (50–100px)
- Speed: 3 tiers (30% slow/0.55×, 50% normal/0.90×, 20% fast/1.40×) × sizeSpeedFactor × speedMult
- Big chars fall slower (sizeSpeedFactor = 1.35 - sizeRoll*0.6)

### Targeting System (critical — don't break this)
- **Multi-prefix**: don't lock to one word until typed prefix uniquely identifies it OR a syllable completes
- Multiple candidates all glow while ambiguous; fire bullets toward the lowest (most urgent)
- Lock fires when `candidates.length===1` OR exact syllable match found
- **Space bar** immediately explodes a fully-typed word (mirrors Chinese IME behavior)
- **Enter/Backspace**: clears sylBuf and resets all targeted flags

### Special Characters
- **Golden words** (isGolden): gold shimmer, pulsing halo, 3× points, cultural tip on destruction
- **Motherships** (isMother): orange rect border, arc countdown fills over 10s of screen-time, spawns 2 children sharing first character from allLevelsPool (HSK 1..selHSK), repeats up to 3× (each cycle 2500ms faster), stops if y > H*0.60
- Children: spawn 280–360px to each side, angular velocity fans out, bounce off play area edges

### Audio
- **TTS** (speechSynthesis): cancel() then speak each completed character. Fast typing = only last char plays. `ttsVol` slider in pause menu. Rate=0.72 for tone clarity.
- **SFX** (Web Audio API): `sfxVol` slider. `sfxCountdownBeep()` bypasses sfxVol (always audible).
- Streak pitch scaling: sfxType() pitch rises from 520Hz → 920Hz over 25-streak.

### Education Features
- **Definition flash**: on word destruction, chars + toned pinyin + English float up from explosion
- **Missed word flash**: red, when word reaches bottom (lose life)
- **Wave tips**: cultural micro-lessons shown at wave clear (TikTok formula: emoji + breakdown + surprising fact)
- **Game over**: words commanded count (unique words destroyed), personal best wave (localStorage), accuracy
- **Audio pronunciation**: speaks each character as its syllable completes

---

## Game Psychology Applied

### Arcade Addiction Principles
1. **Variable ratio reward** (Skinner box): golden words appear at 8% random — same reason slot machines work
2. **Near-miss dopamine**: CLUTCH SAVE when word destroyed in bottom 25% of screen
3. **Flow state**: wave difficulty curve keeps player slightly above their skill level (challenge ≈ skill + 10%)
4. **Auditory skill feedback**: pitch rises with streak — you can *hear* yourself getting better
5. **"One more game" loop**: wave names create narrative tension ("I died at 'The Real Test' — I need to reach 'Expert Territory'")
6. **Cascading feedback** (juice): every keypress → bullet + sound + fill reveal + character response
7. **Streak identity labels**: SHARPSHOOTER (10), UNSTOPPABLE (20), GRANDMASTER (30) — identity not just score

### Accomplishment Architecture
- **Personal best wave** tracked in localStorage — "★ NEW RECORD — WAVE 7!" on game over
- **Words commanded** counter: "34 unique HSK 2 words" = real, concrete language progress
- **Perfect wave bonus**: wave × 200 pts for zero misses — rewards precision over speed
- **Wave names**: crossing from "Picking Up Speed" to "The Real Test" is a felt milestone

### Language Learning Psychology (from Creator Research)
Source: analysis of viral Spanish/French native speaker TikTok creators, Dreaming Spanish method

1. **Curiosity gap**: wave tips open with something surprising ("东西 = EAST + WEST — why?") — Zeigarnik effect, brain must resolve it
2. **Cultural initiation**: tips reveal HOW the culture thinks, not just what words mean — tribal belonging
3. **Comprehensible input**: game always operates slightly above current knowledge (you see the toned pinyin, type the toneless — 85% comprehension)
4. **Social currency**: wave tips are facts you want to repeat to someone else ("did you know 马上 literally means 'on horseback'?")
5. **Active recall under pressure**: typing pinyin from memory while stressed > flashcard recognition — highest retention method
6. **Emotional memory anchoring**: words you destroy in CLUTCH saves or that cause life loss are remembered longer (emotion + cognition)
7. **Micro-revelation format**: one cultural insight per wave, emoji-first, specific, funny — not a lesson, a punchline

### Wave Tips Formula
`emoji + WORD = LITERAL-BREAKDOWN. [Surprising cultural fact].`
Examples in WORD_TIPS dict keyed by `word.t` (toneless pinyin).
~40 words covered. HSK 1 words have the most memorable tips.

---

## What We Deliberately Don't Do
- No radical connection hints in-game (explored, deferred — too much cognitive load during action)
- No tone input mode (explored, rejected — gamefeel suffers)
- No mystery characters (tried, removed — confusing, caused deaths without teaching)
- No time-based waves (removed — count-based waves feel more fair and meaningful)
- No word re-queuing within same wave (discussed, rejected — extending waves ruins wave-as-milestone feel)

---

## Files
```
index.html      — entire game (HTML + CSS + JS, ~2500+ lines)
serve.py        — local http server (python3 serve.py)
CLAUDE.md       — this file
.claude/        — Claude Code config
```

---

## Current Known State
- Play area: 860px desktop / 390px mobile, toggle on menu
- HSK levels 1–7 selectable
- 3 game modes: single char / full words / English→Chinese
- Wave difficulty: count-based, 12 named waves before generic numbering
- Accomplishment: best wave record, words commanded, streak identity
- Audio: TTS pronunciation per syllable, SFX, independent volume sliders in pause menu
- Erhua auto-complete, multi-prefix targeting, space bar confirm

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec
