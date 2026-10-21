# Production files (JLCPCB)

Generated for a JLCPCB fabrication and assembly order of the Tang Nano 9K HAT for KR260, board revision 0.4.
**These files are not a release.** The open items at the end must be closed first.

## Contents

| File | What it is |
|---|---|
| `jlcpcb/tangnano9k-kr260-hat_rev0.4_gerber_drill.zip` | 11 Gerber layers (Protel extensions, no X2, silkscreen clipped by the mask), Excellon PTH and NPTH, drill maps |
| `jlcpcb/tangnano9k-kr260-hat_rev0.4_bom_jlcpcb.csv` | BOM in JLCPCB format: Comment, Designator, Footprint, LCSC Part # (48 lines, 167 placed parts) |
| `jlcpcb/tangnano9k-kr260-hat_rev0.4_cpl_jlcpcb.csv` | Placement file: Designator, Mid X, Mid Y, Layer, Rotation (both sides) |
| `jlcpcb_parts.csv` | Part choice per BOM group (value and footprint): LCSC number, manufacturer, MPN, notes |
| `make_jlcpcb.py` | Regenerates the three order files from the KiCad project and `jlcpcb_parts.csv` |

Regenerate after any change to the board or schematic: `python3 hardware/production/make_jlcpcb.py`. It stops if a
BOM group has no entry in `jlcpcb_parts.csv`. Test points (TP1-TP6) and the JP90 solder jumper are PCB features
and carry no part.

## PCB order settings

| Setting | Value |
|---|---|
| Layers | 4 |
| Size | 65 × 56.5 mm, Raspberry Pi HAT format (fit checked against the KR260 3D model, see below) |
| Thickness | 1.6 mm |
| Stackup | JLC04161H-7628: 35 µm outer copper, 0.2104 mm 7628 prepreg (εr 4.4), 0.5 oz inner copper, 1.065 mm core. The board file carries this stackup |
| Impedance control | Yes. USB D+/D- (USB_DP/USB_DN) on the top layer over the In1 GND plane: 0.30 mm traces, 0.15 mm gap, target 90 Ω differential (about 94 Ω uncoated / 91 Ω with solder mask by KiCad's coupled-microstrip equations; not measured). Order with JLCPCB's impedance control so they can adjust |
| Material | FR-4, TG155 (JLCPCB's material for impedance-controlled multilayer boards) |
| Surface finish | ENIG (0.4 mm pitch QFN-88, 0.5 mm pitch LQFP-64, 0.4 mm pitch QFN-20) |
| Copper | 1 oz outer, 0.5 oz inner |
| Vias | 0.45/0.2 mm minimum (within JLCPCB's standard price range); tented on both sides |
| Minimum track / space | 0.10 / 0.10 mm |
| Solder mask / silkscreen | Green / white |

The 16 thermal vias in the GW1NR exposed pad (U4, 0.3 mm holes, part of the footprint) are open holes. Epoxy filled
and capped vias (JLCPCB's via-in-pad option) avoid solder wicking but cost more; the paste stencil already uses
3 × 3 windows between the vias. Decide before ordering.

The DRC rules in `hardware/tangnano9k-kr260-hat.kicad_dru` encode JLCPCB's multilayer limits (hole-to-copper,
annular rings, hole-to-hole, drill sizes, silkscreen text). Current DRC with schematic parity: 0 errors, 0
unconnected pads, 0 parity issues, 2 warnings (the USB-C library footprint silkscreen crosses the board edge; the
fab clips it).

## Assembly (PCBA)

- Double-sided: 109 parts on the top, 58 on the bottom (decoupling of the GW1NR and FT2232H, 1.2 V LDO, the D3/D4 power OR-ing diodes with C14, J130).
- Through-hole: J130 (2 × 20 female header, bottom side) and J90 (1 × 6 header, top, external JTAG). Both are
  assembled; JLCPCB solders them by hand and prices that in the order.
- Every BOM part is assembled; two of them must be in "My Parts Lib" first (next section).
- The logic ICs must be genuine Texas Instruments parts: the isolation scheme relies on their Ioff (partial
  power-down) behavior.
- Check the orientation of every part in JLCPCB's placement preview before confirming. KiCad and JLCPCB use
  different zero orientations for some packages (SOT-23, SOT-23-6, TSSOP, QFN); apart from J90 and J130, the CPL
  has no rotation offsets applied.
- J90 (pin header) and J130 (socket): KiCad puts their origin on pin 1 with the pins along Y, while the JLCPCB
  footprints are centred with the pins along X. `make_jlcpcb.py` writes them at the centre of their pads, turned
  by -90 degrees (J90 at 270, J130 at 180). Both are unpolarized.
- D3 and D4 (B5819W, SOD-123, bottom side) carry all the board power: in the bottom-side placement preview, check
  that their cathode band sits on pad 1, toward the +5V side (D3: anode from F1, D4: anode from the J21 5 V).
- Fiducials: FID1-FID3 on the top side. The bottom side has none.

Stock and prices come from a catalog snapshot and change daily; JLCPCB's BOM tool shows the current state.

### Full assembly: parts to secure before the PCBA order

The board is ordered fully assembled. Two parts are not in JLCPCB's assembly stock and must be in the private
parts library ("My Parts Lib") before the PCBA order:

1. U2, TMI7003C (C840566, extended part): Parts Manager → Order Parts → search C840566 → quantity → Add to My
   Part Lib → checkout. It is a pre-order: JLCPCB confirms the price within 48 h, and the parts can only be used
   once they reach its warehouse.
2. U4, GW1NR-LV9QN88PC6/I5 (no LCSC number): request it through JLCPCB Global Sourcing in the Parts Manager.
   JLCPCB buys it from global distributors, with a lead time of about 9-15 days.
3. Order one of each per assembled board, plus spares if wanted; leftovers stay in "My Parts Lib".
4. When both are in "My Parts Lib", place the PCB + PCBA order: U2 and U4 match the private library in the BOM
   step, and every other line comes from JLCPCB stock (all in stock for 5 boards in the 2026-10-20 catalog
   snapshot). Do not mark any part "Do not place".

JLCPCB's help article "How to build your own parts library in JLCPCB" (updated 2026-09-09): for the same part,
Global Sourcing or consigned stock cannot be combined with pre-order or JLCPCB stock; different parts have no such
restriction, so U4 from Global Sourcing and U2 from pre-order go in the same order.

## Power inputs (README rev. 0.6)

The board runs from its USB-C or from the KR260 J21 5 V (contacts 2 and 4), each through its own B5819W Schottky
diode (D3, D4) into +5V, so either source alone powers it and neither feeds the other. +5V sits one Schottky drop
below the active source (up to about 0.6 V at 1 A per the JLCPCB catalog). The J21 5 V is limited to 1.0 A by the
KR260 (UG1092).

After assembly, before the first use with the KR260, program the FT2232H EEPROM (U91, 93LC56B) with FTDI FT_PROG:
self-powered, and "suspend on DBUS7 low" (FT_000061 v2.10, section 6.2). PWRSAV# (R10/R11 from VBUS) then keeps
the FT2232H in suspend while no USB host is connected.

## Mechanical fit with the KR260

Checked against the KR260 3D model (XTP744, `KR260-startkit-A02.stp`), not on hardware:

- The HAT fastens to the two KR260 holes on the J21 centreline (2.77 mm, 58 mm apart) with its H1/H2 holes, and
  J130 lands on J21. The rest of the HAT overhangs the KR260 edge (about 47 mm); H3/H4 have no support there.
- Under the 9 mm strip that covers the KR260 there is only J21. Nearest tall KR260 parts: dual RJ45 9.7 mm away,
  SFP cage 14.5 mm, SOM fan heatsink 40.8 mm.
- Stack: J21 plastic (2.4 mm) + 8.5 mm female socket = about 10.9 mm board to board. Use two M2.5 × 11 mm
  standoffs with screws; they are not in the BOM.

## Open items before a release

- Confirm on a real KR260 that J21 pin 1 is on the outer column, at the end toward the Pmod connectors (the 3D
  model does not mark pin 1; the orientation comes from a photo of a Raspberry Pi HAT mounted on J21), and do a
  physical fit check with the 8.5 mm socket and the standoffs.
- K26 PUDC_B state (ISO-14), final pull-down values (ISO-12), PTC and ferrite ratings (PWR-04).
- Link routing priority and length matching (PCB-02, PCB-03), buck converter loop review (PWR-04), signal
  integrity simulation (PCB-14).
- W25Q32JV compatibility with the GW1NR-9 MSPI boot.
- Power budget (PWR-04) against the 1.0 A of the J21 5 V and the current offered by the USB source.
- Human design review of schematic and layout.
