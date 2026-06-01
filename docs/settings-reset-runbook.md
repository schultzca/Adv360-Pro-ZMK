# Settings Reset Runbook

**Source documentation:** [ZMK Split Keyboard Connection Issues](https://zmk.dev/docs/troubleshooting/connection-issues#split-keyboard-parts-unable-to-pair) · [Kinesis Support: Firmware Updates](https://kinesis-ergo.com/support/kb360pro/#firmware-updates)

## When to use this

There are two levels of reset — use the lightest one that fixes your problem.

### Option A — BT profile clear (try this first)

Use when the keyboard won't connect or pair to your Mac, but the two halves are talking to each other normally (no red LEDs flashing on the right half).

1. On the keyboard: **Mod + Windows Key** to clear the active Bluetooth profile.
2. On your Mac: **System Settings → Bluetooth** → find Adv360Pro → **Forget This Device**.
3. Re-pair from scratch.

### Option B — Full settings reset with `settings-reset.uf2` (this runbook)

Use when:
- The right-half LEDs are **all flashing red** (halves can't find each other)
- You replaced a controller on one half
- A firmware upgrade changelog explicitly requires it (see [CHANGELOG](../CHANGELOG.md))

> **⚠️ Warning:** This erases **all** stored settings: Bluetooth profiles, output selection, RGB colors, etc. You will need to re-pair the keyboard with your Mac afterward.

## Prerequisites

- `settings-reset.uf2` (located at the repo root)
- Your normal firmware files: `left.uf2` and `right.uf2`

## Procedure

### Step 1 — Flash settings-reset to the left half

1. Connect the left half to USB.
2. Enter bootloader mode: press **Mod+macro1**, or use the physical reset button (see User Manual §2.7).
3. The left half mounts as a USB drive.
4. Copy `settings-reset.uf2` to the drive. It will disconnect automatically.

### Step 2 — Flash settings-reset to the right half

1. Connect the right half to USB.
2. Enter bootloader mode: press **Mod+macro3**, or use the physical reset button.
3. The right half mounts as a USB drive.
4. Copy `settings-reset.uf2` to the drive. It will disconnect automatically.

> **Note:** While `settings-reset.uf2` is loaded, Bluetooth is disabled. The keyboard will not appear in any Bluetooth device lists until you flash normal firmware in the next step.

### Step 3 — Flash normal firmware to both halves

Follow the standard [flashing procedure](../README.md#overview) to flash `left.uf2` and `right.uf2`.

### Step 4 — Re-pair with your Mac

1. On your Mac, open **System Settings → Bluetooth**.
2. Find the Advantage 360 Pro, click the **ⓘ** icon, and choose **Forget This Device**.
3. Re-pair the keyboard as normal.

## Notes

- Some operating systems may show a spurious eject error after flashing; this is harmless and does not indicate a failure.
- If the halves still haven't paired after completing these steps, try resetting both halves simultaneously (press the reset buttons on both at roughly the same time, or power both off then on together).
- For major version upgrades (V2 → V3), additional reset files and instructions are available at [kinesis-ergo.com/support/kb360pro/#firmware-updates](https://kinesis-ergo.com/support/kb360pro/#firmware-updates).
