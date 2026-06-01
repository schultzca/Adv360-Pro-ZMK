#!/usr/bin/env python3
"""
Generate keymap-cheatsheet.svg (and optionally a desktop wallpaper PNG)
from keymap.yaml via keymap-drawer.

Usage:
    python generate_svg.py [--output FILE]
    python generate_svg.py --wallpaper [--wallpaper-output FILE]
                           [--width W] [--height H]

Reads keymap.yaml, converts it to keymap-drawer YAML format (handling the
Advantage 360 Pro's reserved-layer index gap), then calls keymap-drawer to
produce the SVG. With --wallpaper, also renders a landscape PNG at the
requested resolution with all layers arranged in a single row.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ── constants ──────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
KEYMAP_YAML = SCRIPT_DIR / "keymap.yaml"
INFO_JSON = REPO_ROOT / "config" / "info.json"
DEFAULT_OUTPUT = REPO_ROOT / "assets" / "keymap-cheatsheet.svg"
DEFAULT_WALLPAPER_OUTPUT = REPO_ROOT / "assets" / "keymap-wallpaper.png"
DEFAULT_WALLPAPER_WIDTH = 2304
DEFAULT_WALLPAPER_HEIGHT = 1296

# Human-readable labels for common ZMK keycodes
KEY_LABELS: dict[str, str] = {
    # Modifiers
    "LSHFT": "⇧Sft", "RSHFT": "⇧Sft", "LCTRL": "Ctrl", "RCTRL": "Ctrl",
    "LALT": "Alt", "RALT": "AltGr", "LGUI": "⌘Gui", "RGUI": "⌘Gui",
    # Navigation / editing
    "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "BSPC": "⌫", "DEL": "⌦", "ESC": "Esc", "TAB": "⇥Tab",
    "ENTER": "↵", "SPACE": "Space", "CAPS": "Caps",
    # Function
    **{f"F{n}": f"F{n}" for n in range(1, 13)},
    # Numbers
    **{f"N{n}": str(n) for n in range(0, 10)},
    # Special
    "EQUAL": "=", "MINUS": "-", "BSLH": "\\", "GRAVE": "`",
    "LBKT": "[", "RBKT": "]", "SEMI": ";", "SQT": "'",
    "COMMA": ",", "DOT": ".", "FSLH": "/",
    # Symbols (shift chars)
    "AT": "@", "HASH": "#", "DOLLAR": "$", "PRCNT": "%", "CARET": "^",
    "AMPS": "&", "STAR": "*", "LPAR": "(", "RPAR": ")",
    "LBRC": "{", "RBRC": "}", "LT": "<", "GT": ">",
    "EXCL": "!", "QMARK": "?", "PLUS": "+", "UNDER": "_",
    "TILDE": "~", "PIPE": "|", "COLON": ":", "BSPC": "⌫",
    "EXCLAMATION": "!", "GREATER_THAN": ">",
    # Keypad
    "KP_NUM": "NumLk", "KP_EQUAL": "=", "KP_DIVIDE": "÷", "KP_MULTIPLY": "×",
    "KP_MINUS": "-", "KP_PLUS": "+", "KP_ENTER": "↵", "KP_DOT": ".",
    **{f"KP_N{n}": str(n) for n in range(0, 10)},
    # Bluetooth
    "BT_CLR": "BT\nClr",
    **{f"BT_SEL {n}": f"BT{n}" for n in range(5)},
    # Macros — compact display names
    "macro_quotes": "''", "macro_dquotes": '""', "macro_braces": "{}",
    "macro_parens": "()", "macro_brackets": "[]", "macro_angle": "<>",
    "macro_arrow": "->", "macro_fat_arrow": "=>",
    "macro_neq": "!=", "macro_deq": "==",
    "macro_lte": "<=", "macro_gte": ">=",
    "macro_md_h1": "# H1", "macro_md_h2": "## H2", "macro_md_h3": "### H3",
    "macro_md_bold": "**bold**", "macro_md_italic": "_ital_",
    "macro_md_code_inline": "`code`", "macro_md_link": "[lnk]()",
    "macro_md_listitem": "- list", "macro_md_taskitem": "- [ ]",
    "Mac_Spotlight_Search": "⌘Spc\nSpot",
    "Mac_Cut": "⌘X", "Mac_Copy": "⌘C", "Mac_Paste": "⌘V",
    "Mac_Undo": "⌘Z", "Mac_Select_All": "⌘A",
    "Mac_Mission_Control": "MCont", "Mac_Snip_Tool": "Snip",
    "Mac_Close_Program": "⌘Q", "Mac_Strike_Through_Text": "Strike",
    "Win_Cut": "^X", "Win_Copy": "^C", "Win_Paste": "^V",
    "Win_Undo": "^Z", "Win_Select_All": "^A",
    "Win_Desktop": "⊞D", "Win_File_Explorer": "⊞E",
    "Win_Snip_Tool": "Snip", "Win_Show_All_Windows": "⊞Tab",
    "Win_Close_Program": "AltF4", "Win_Settings_Menu": "⊞I",
    "Win_Lock_PC": "⊞L",
    "Win_Tile_Left": "⊞←", "Win_Tile_Right": "⊞→",
    "Win_Tile_Up": "⊞↑", "Win_Tile_Down": "⊞↓",
    "Double_Click": "DblClk",
    "macro_ver": "Ver",
    "macro_kinesis": "Kine-sis",
}

# ── helpers ────────────────────────────────────────────────────────────────────

_MOD_RE = re.compile(r"^(L[ACGS]|R[ACGS])\((.+)\)$")


def _modifier_label(mod: str, key: str) -> str:
    mod_map = {
        "LC": "^", "RC": "^", "LA": "⌥", "RA": "⌥",
        "LG": "⌘", "RG": "⌘", "LS": "⇧", "RS": "⇧",
    }
    return f"{mod_map.get(mod, mod)}{_kp_label(key)}"


def _kp_label(raw: str) -> str:
    """Convert a bare keycode (no &kp prefix) to a display label."""
    raw = raw.strip()
    if not raw:
        return ""
    # Handle modifier wrapping: LA(LEFT), LG(SPACE), LS(LG(NUMBER_4)) etc.
    m = _MOD_RE.match(raw)
    if m:
        mod, inner = m.group(1), m.group(2)
        # nested mods: LS(LG(X)) → ⇧⌘X
        inner_label = _kp_label(inner)
        mod_map = {
            "LC": "^", "RC": "^", "LA": "⌥", "RA": "⌥",
            "LG": "⌘", "RG": "⌘", "LS": "⇧", "RS": "⇧",
        }
        return f"{mod_map.get(mod, mod)}{inner_label}"
    # NUMBER_4 → 4
    if raw.startswith("NUMBER_"):
        return raw[7:]
    return KEY_LABELS.get(raw, raw)


def binding_to_label(binding: str, layer_names: list[str]) -> dict:
    """Convert a ZMK binding string to a keymap-drawer key dict."""
    b = binding.strip()

    if b in ("&none", ""):
        return {"t": ""}
    if b == "&trans":
        return {"t": "▽", "type": "trans"}

    # &mo N  / &tog N / &to N / &sl N
    mo_m = re.match(r"^&(mo|tog|to|sl) (\d+)$", b)
    if mo_m:
        kind, idx = mo_m.group(1), int(mo_m.group(2))
        label = layer_names[idx] if idx < len(layer_names) else f"L{idx}"
        type_ = "held" if kind == "mo" else "toggle"
        return {"t": label, "type": type_}

    # &lt N KEY  (layer-tap)
    lt_m = re.match(r"^&lt (\d+) (.+)$", b)
    if lt_m:
        idx, key = int(lt_m.group(1)), lt_m.group(2).strip()
        layer_label = layer_names[idx] if idx < len(layer_names) else f"L{idx}"
        return {"t": _kp_label(key), "h": layer_label}

    # &hm MOD KEY
    hm_m = re.match(r"^&hm (\S+) (.+)$", b)
    if hm_m:
        return {"t": _kp_label(hm_m.group(2)), "h": _kp_label(hm_m.group(1))}

    # &kp KEY or &kp MOD(KEY)
    kp_m = re.match(r"^&kp (.+)$", b)
    if kp_m:
        return {"t": _kp_label(kp_m.group(1))}

    # macros / raw
    raw_m = re.match(r"^&(\S+)(.*)$", b)
    if raw_m:
        name, rest = raw_m.group(1), raw_m.group(2).strip()
        if name in KEY_LABELS:
            return {"t": KEY_LABELS[name]}
        # bt BT_SEL 0
        full = f"{name} {rest}".strip() if rest else name
        return {"t": KEY_LABELS.get(full, full.replace("_", " "))}

    return {"t": b}


def build_drawer_yaml(config: dict) -> str:
    """Convert keymap.yaml config to keymap-drawer YAML format."""
    raw_layers = config.get("layers", [])

    # Build index → display_name map (all layers including reserved stubs)
    all_layer_names: list[str] = []
    for layer in raw_layers:
        all_layer_names.append(layer.get("display_name", layer["name"]))

    # Collect active (non-reserved) layers
    active_layers = [l for l in raw_layers if l.get("status") != "reserved"]

    from tooling_generate import bindings_from_dict, expand_shorthand, TOTAL_KEYS  # noqa: F401

    result_layers: dict[str, list] = {}
    for layer in active_layers:
        name = layer.get("display_name", layer["name"])
        bindings_raw = layer.get("bindings")

        expanded = expand_shorthand(bindings_raw)
        if expanded:
            bindings_list = expanded
        elif isinstance(bindings_raw, dict):
            bindings_list = bindings_from_dict(bindings_raw)
        else:
            bindings_list = ["&none"] * TOTAL_KEYS

        keys = [binding_to_label(b, all_layer_names) for b in bindings_list]

        # Simplify: if key is just a tap string, use the string directly
        simplified = []
        for k in keys:
            if set(k.keys()) == {"t"}:
                simplified.append(k["t"])
            else:
                simplified.append(k)
        result_layers[name] = simplified

    return yaml.dump(
        {"layers": result_layers},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )


# ── main ───────────────────────────────────────────────────────────────────────


def _draw_svg(drawer_yaml: str, output_path: Path, draw_config: dict | None = None) -> None:
    """Call keymap-drawer to render drawer_yaml to an SVG file."""
    import tempfile

    cmd = [
        "uv", "tool", "run", "--from", "keymap-drawer", "keymap",
    ]

    cfg_tmp = None
    if draw_config:
        import json, tempfile as _tf
        cfg_yaml = "draw_config:\n" + "".join(
            f"  {k}: {json.dumps(v)}\n" for k, v in draw_config.items()
        )
        cfg_tmp = _tf.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        cfg_tmp.write(cfg_yaml)
        cfg_tmp.flush()
        cfg_tmp.close()
        cmd += ["-c", cfg_tmp.name]

    cmd += [
        "draw",
        "-j", str(INFO_JSON),
        "-o", str(output_path),
        "-",
    ]

    result = subprocess.run(cmd, input=drawer_yaml, capture_output=True, text=True)

    if cfg_tmp:
        Path(cfg_tmp.name).unlink(missing_ok=True)

    if result.returncode != 0:
        print("keymap-drawer error:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        debug_path = output_path.with_suffix(".debug.yaml")
        debug_path.write_text(drawer_yaml)
        print(f"Debug YAML written to: {debug_path}", file=sys.stderr)
        sys.exit(1)


def _svg_to_png_wallpaper(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    """Render SVG to a PNG at the given pixel dimensions with a dark background."""
    import cairosvg

    # Read SVG dimensions so we can compute scale to fill the target size
    svg_text = svg_path.read_text()
    import re as _re
    vb = _re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    if vb:
        svg_w, svg_h = float(vb.group(1)), float(vb.group(2))
        scale = min(width / svg_w, height / svg_h)
        render_w = int(svg_w * scale)
        render_h = int(svg_h * scale)
    else:
        render_w, render_h = width, height

    # Render SVG → PNG (transparent background)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(tmp_path),
        output_width=render_w,
        output_height=render_h,
    )

    # Composite onto a dark background canvas at exact wallpaper resolution
    from PIL import Image
    bg = Image.new("RGB", (width, height), color=(30, 30, 30))
    fg = Image.open(tmp_path).convert("RGBA")
    x = (width - render_w) // 2
    y = (height - render_h) // 2
    bg.paste(fg, (x, y), fg)
    bg.save(str(png_path), "PNG")
    tmp_path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Generate keymap SVG (and optional wallpaper PNG)")
    parser.add_argument(
        "--output", "-o",
        default=str(DEFAULT_OUTPUT),
        help=f"Output SVG path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--input", "-i",
        default=str(KEYMAP_YAML),
        help="Input keymap.yaml path",
    )
    parser.add_argument(
        "--wallpaper", action="store_true",
        help="Also generate a landscape PNG wallpaper with all layers in one row",
    )
    parser.add_argument(
        "--wallpaper-output",
        default=str(DEFAULT_WALLPAPER_OUTPUT),
        help=f"Wallpaper PNG output path (default: {DEFAULT_WALLPAPER_OUTPUT})",
    )
    parser.add_argument(
        "--width", type=int, default=DEFAULT_WALLPAPER_WIDTH,
        help=f"Wallpaper width in pixels (default: {DEFAULT_WALLPAPER_WIDTH})",
    )
    parser.add_argument(
        "--height", type=int, default=DEFAULT_WALLPAPER_HEIGHT,
        help=f"Wallpaper height in pixels (default: {DEFAULT_WALLPAPER_HEIGHT})",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    wallpaper_path = Path(args.wallpaper_output).expanduser().resolve()

    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        config = yaml.safe_load(f)

    # Dynamically import helpers from sibling generate_keymap.py
    import importlib.util, sys as _sys
    spec = importlib.util.spec_from_file_location(
        "tooling_generate", SCRIPT_DIR / "generate_keymap.py"
    )
    mod = importlib.util.module_from_spec(spec)
    _sys.modules["tooling_generate"] = mod
    spec.loader.exec_module(mod)

    global binding_to_label
    from tooling_generate import bindings_from_dict, expand_shorthand, TOTAL_KEYS

    def _build(cfg):
        raw_layers = cfg.get("layers", [])
        all_layer_names = [l.get("display_name", l["name"]) for l in raw_layers]
        active_layers = [l for l in raw_layers if l.get("status") != "reserved"]
        result_layers = {}
        for layer in active_layers:
            name = layer.get("display_name", layer["name"])
            bindings_raw = layer.get("bindings")
            expanded = expand_shorthand(bindings_raw)
            if expanded:
                bindings_list = expanded
            elif isinstance(bindings_raw, dict):
                bindings_list = bindings_from_dict(bindings_raw)
            else:
                bindings_list = ["&none"] * TOTAL_KEYS
            keys = []
            for b in bindings_list:
                k = binding_to_label(b, all_layer_names)
                if set(k.keys()) == {"t"}:
                    keys.append(k["t"])
                else:
                    keys.append(k)
            result_layers[name] = keys
        return yaml.dump(
            {"layers": result_layers},
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    drawer_yaml = _build(config)

    # Generate standard cheatsheet SVG
    _draw_svg(drawer_yaml, output_path)
    print(f"SVG generated: {output_path}")

    # Generate wallpaper SVG (all layers in one row) then convert to PNG
    if args.wallpaper:
        n_active = sum(1 for l in config.get("layers", []) if l.get("status") != "reserved")
        wallpaper_svg_path = output_path.with_name("keymap-wallpaper.svg")
        _draw_svg(drawer_yaml, wallpaper_svg_path, draw_config={"n_columns": n_active})
        print(f"Wallpaper SVG generated: {wallpaper_svg_path}")
        _svg_to_png_wallpaper(wallpaper_svg_path, wallpaper_path, args.width, args.height)
        print(f"Wallpaper PNG generated: {wallpaper_path}")
        print(f"  Resolution: {args.width}×{args.height}")


if __name__ == "__main__":
    main()
