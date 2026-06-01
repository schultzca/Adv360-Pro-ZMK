# Flashing Firmware

Instructions for flashing firmware onto the Kinesis Advantage 360 Pro using the physical reset button.

**Source documentation:** [Kinesis Quick Start Guide (p. 8)](https://kinesis-ergo.com/wp-content/uploads/Advantage360-Professional-QSG-v8-25-22.pdf) · [User Manual §2.7 (p. 9) and §5.9 (p. 14)](https://kinesis-ergo.com/wp-content/uploads/Advantage360-ZMK-KB360-PRO-Users-Manual-v3-10-23.pdf)

## Prerequisites

- Built firmware: `left.uf2` and `right.uf2` (from GitHub Actions artifacts or `firmware/` if built locally)
- A USB-C cable
- A paperclip or sim-eject tool to press the recessed reset button

## Entering Bootloader Mode (Physical Reset)

Each half has a recessed reset button described in User Manual §2.7 (p. 9):

- **Single press** — restarts the half normally
- **Double press** — enters bootloader mode; the half mounts as a USB drive named `ADV360`

## Flashing the Left Half

1. Connect the **left half** to your Mac via USB.
2. **Double-press** the reset button on the left half.
3. It mounts as a USB drive (`ADV360`).
4. Copy `left.uf2` to the drive. It will unmount automatically when done.
5. Power off the left half (unplug USB and flip the power switch off).

## Flashing the Right Half

1. Connect the **right half** to your Mac via USB.
2. **Double-press** the reset button on the right half.
3. It mounts as a USB drive (`ADV360`).
4. Copy `right.uf2` to the drive. It will unmount automatically when done.
5. Unplug the right half.

## Bringing Both Halves Back Online

1. Power on the **left half** first (flip switch on or connect USB). Wait ~5 seconds for it to fully wake up.
2. Power on the **right half**. The halves will pair over BLE automatically.

## Notes

- Some macOS versions may show a spurious "disk not ejected properly" error after the drive unmounts — this is harmless.
- If a half doesn't mount as a USB drive after double-pressing, try pressing the reset button slightly faster or slower. The timing window is ~500ms between presses.
- If you need to flash `settings-reset.uf2` before flashing firmware (e.g., after a sync failure), follow the [settings reset runbook](settings-reset-runbook.md) first, then return here.
