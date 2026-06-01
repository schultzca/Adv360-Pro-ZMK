# AGENTS.md — Adv360 Pro ZMK Keymap

This file captures the context needed to work on this keyboard firmware repository. Read it before making any changes to the keymap.

---

## Repository Purpose

This is firmware for a **Kinesis Advantage 360 Pro** keyboard running ZMK. The owner is a software engineering manager who codes and writes documentation on **macOS exclusively**. The keymap is optimized for:
- Ergonomics (minimal finger travel, thumb-cluster activation)
- Coding efficiency (symbol auto-pairs, compound operators)
- Documentation/Markdown authoring (dedicated Markdown layer)
- Mac-native shortcuts (Spotlight, Mission Control, window management)

---

## Toolchain — How the Keymap Works

**Never edit `config/adv360.keymap` directly.** It is generated.

```
tooling/keymap/keymap.yaml        ← source of truth (edit this)
        ↓
tooling/keymap/generate_keymap.py ← run this to regenerate
        ↓
config/adv360.keymap              ← generated ZMK firmware file
```

To regenerate the keymap after editing `keymap.yaml`:
```bash
uv run python tooling/keymap/generate_keymap.py
```

To regenerate the SVG cheatsheet:
```bash
uv run python tooling/keymap/generate_svg.py
# Output: assets/keymap-cheatsheet.svg
```

---

## Key Format in keymap.yaml

| YAML value | Generated ZMK |
|---|---|
| `A`, `LSHFT`, `N1` | `&kp A`, `&kp LSHFT`, `&kp N1` |
| `mo 2`, `tog 1` | `&mo 2`, `&tog 1` |
| `lt 4 BSPC` | `&lt 4 BSPC` |
| `none`, `trans` | `&none`, `&trans` |
| `bt BT_SEL 0` | `&bt BT_SEL 0` |
| `macro_quotes` | `&macro_quotes` (must be in `MACROS` set) |
| `Mac_Spotlight_Search` | `&Mac_Spotlight_Search` (must be in `MACROS` set) |
| `LG(LEFT)`, `LA(BSPC)` | `&kp LG(LEFT)`, `&kp LA(BSPC)` |
| `&bootloader` | passed through as-is |

**Modifier prefixes:** `LG`=⌘Cmd, `LA`=⌥Option, `LC`=^Ctrl, `LS`=⇧Shift (L/R prefix = left/right).

---

## Key Positions (0–75)

The Advantage 360 Pro has 76 keys. Positions are referenced by integer in `keymap.yaml`.

```
LEFT HAND                              RIGHT HAND
0  1  2  3  4  5  6                7  8  9  10 11 12 13   ← number row
14 15 16 17 18 19 20               21 22 23 24 25 26 27   ← top alpha (QWERTY row)
28 29 30 31 32 33 34   35 36 37 38 39 40 41 42 43 44 45   ← home row + inner thumbs
46 47 48 49 50 51         52 53       54 55 56 57 58 59   ← bottom alpha
60 61 62 63 64      65 66 67 68 69 70    71 72 73 74 75   ← bottom row + thumb clusters
```

**Notable positions:**
- `52` — left middle thumb (Spotlight: `Mac_Spotlight_Search`)
- `53` — right middle thumb (`mo 10` → Symbol layer)
- `65` — left outer thumb (`lt 4 BSPC` → tap=Backspace, hold=Markdown layer)
- `66` — left thumb (`LSHFT`)
- `67` — left thumb (`END`)
- `68` — right outer thumb (`mo 9` → Vim nav layer)
- `69` — right thumb (`ENTER`)
- `70` — right thumb (`SPACE`)

---

## Layer Architecture

| Index | Name | Activation | Purpose |
|---|---|---|---|
| 0 | Base | default | QWERTY base layer |
| 1 | Kp | `tog 1` (Fn layer) | Keypad/numpad |
| 2 | Fn | `mo 2` (pos 60, 75) | Function keys F1–F12 |
| 3 | Mod | `mo 3` (pos 7) | BT, RGB, firmware |
| 4 | Md | hold pos 65 (`lt 4 BSPC`) | Markdown authoring |
| 5–8 | extra2–5 | reserved | ZMK Studio reserved (do not use) |
| 9 | Vim | hold pos 68 (`mo 9`) | Vim-style navigation |
| 10 | Sym | hold pos 53 (`mo 10`) | Symbols and operators |

**Important:** Layers 5–8 are ZMK Studio reserved stubs (`status: reserved`). They have no bindings and create an index gap. The SVG generator (`generate_svg.py`) handles this automatically. Do not insert new active layers at indices 5–8.

---

## Layer Contents

### Markdown Layer (4) — hold left-thumb BSPC
Right hand only; left hand keeps normal base layer access.
- `Y/U/I` (22/23/24) — H1, H2, H3 headings
- `H/J/K/L/;` (40–44) — list item, task item, inline code, link, strikethrough
- `N/M` (54/55) — italic `__`, bold `****`

### Vim Nav Layer (9) — hold right-thumb outer
- Right hand home row `H/J/K/L` — ← ↓ ↑ →
- Right hand top row `Y/U/I/O/P` — line-start, word-left, word-right, line-end, del
- Right hand bottom `N/M` — PgUp, PgDn
- Left hand home row `A/S/D/F/G` — SelectAll, top-of-doc (⌘↑), bottom-of-doc (⌘↓), delete-word (⌥⌫), delete-to-line-start (⌘⌫)
- Left hand bottom `Z/X/C/V` — Undo, Cut, Copy, Paste
- Left hand top `T` (19) — Spotlight search (easy bi-manual trigger)

### Symbol Layer (10) — hold right-thumb middle
- Left hand top row `Q/W/E/R/T` — `''`, `""`, `[]`, `{}`, `()`
- Left hand home row `A/S/D/F/G` — `@`, `#`, `$`, `|`, `` ` ``
- Left hand bottom `Z/X/C/V/B` — `~`, `%`, `^`, `\`, `!`
- Right hand top row `Y/U/I/O/P/\` — `<>`, `*`, `/`, `?`, `+`, ⌘\` (cycle windows)
- Right hand home row `H/J/K/L/;/'` — `-`, `_`, `=`, `:`, `&`, `=>`
- Right hand bottom `N/M/,/./` — `!=`, `==`, `<=`, `>=`, `->`

### Mod Layer (3) — hold right-hand mod key (pos 7)
- Number row: BT device select (0–4)
- Top row right: `Y`=Mission Control, `U`=Screenshot, `P`=Quit app
- `bootloader` at pos 20/21, `studio_unlock` at pos 28
- RGB, backlight, battery controls on bottom row

---

## Macros

All macros are defined in `config/macros.dtsi`. **Every macro name must also be registered in the `MACROS` set in `tooling/keymap/generate_keymap.py`** — otherwise the generator will incorrectly prefix it with `&kp`.

### Auto-pair macros (type both chars, cursor moves between them)
- `macro_quotes` — `''` with cursor inside
- `macro_dquotes` — `""` with cursor inside
- `macro_braces` — `{}` with cursor inside
- `macro_parens` — `()` with cursor inside
- `macro_brackets` — `[]` with cursor inside
- `macro_angle` — `<>` with cursor inside

### Compound operator macros
- `macro_arrow` — `->`
- `macro_fat_arrow` — `=>`
- `macro_neq` — `!=`
- `macro_deq` — `==`
- `macro_lte` — `<=`
- `macro_gte` — `>=`

### Markdown macros
- `macro_md_h1/h2/h3` — `# `, `## `, `### `
- `macro_md_bold` — `****` cursor between pairs
- `macro_md_italic` — `__` cursor inside
- `macro_md_code_inline` — ` `` ` cursor inside
- `macro_md_link` — `[]()` cursor on link text
- `macro_md_listitem` — `- `
- `macro_md_taskitem` — `- [ ] `

### Mac utility macros
- `Mac_Spotlight_Search` — `LG(SPACE)`
- `Mac_Mission_Control` — `LC(UP_ARROW)`
- `Mac_Snip_Tool` — `LC(LG(LS(NUMBER_4)))`
- `Mac_Close_Program` — `LG(Q)`
- `Mac_Strike_Through_Text` — `LG(LS(X))`
- `Mac_Cut/Copy/Paste/Undo/Select_All` — standard ⌘X/C/V/Z/A

---

## Adding a New Macro

1. Add the macro definition to `config/macros.dtsi` following the existing pattern
2. Add the macro name to the `MACROS` set in `tooling/keymap/generate_keymap.py`
3. Reference it by name in `tooling/keymap/keymap.yaml`
4. Run `uv run python tooling/keymap/generate_keymap.py`
5. Run `uv run python tooling/keymap/generate_svg.py`

---

## Adding a New Layer

New active layers must be placed **after index 10** (never at indices 5–8). Add at the end of the `layers` list in `keymap.yaml`. The activation binding in an existing layer must reference the correct ZMK index.

---

## SVG Generation Notes

The SVG generator (`tooling/keymap/generate_svg.py`) works around a `keymap-drawer` limitation: the tool cannot parse `adv360.keymap` directly because the reserved layers at indices 5–8 cause an index gap that breaks `mo 9` and `mo 10` references. The generator instead reads `keymap.yaml` directly, builds a keymap-drawer-compatible YAML from the active layers only, and feeds it to `keymap draw -j config/info.json`. The output is `assets/keymap-cheatsheet.svg`.

The `keymap-drawer` binary is invoked as:
```bash
uv tool run --from keymap-drawer keymap draw ...
```
