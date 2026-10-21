#!/usr/bin/env python3
"""Generate the JLCPCB order files from the KiCad project.

Writes into production/jlcpcb/:
  <board>_<rev>_gerber_drill.zip   Gerbers (11 layers, Protel extensions, no X2), Excellon PTH/NPTH, drill maps
  <board>_<rev>_bom_jlcpcb.csv     Comment, Designator, Footprint, LCSC Part #
  <board>_<rev>_cpl_jlcpcb.csv     Designator, Mid X, Mid Y, Layer, Rotation
Parts come from production/jlcpcb_parts.csv (key "Value|Footprint name"); a BOM group without an entry stops the run.
Pin headers and sockets are written at the centre of their pads and turned to match the JLCPCB library footprints
(PAD_CENTRED); every other part keeps the KiCad position and rotation.

Usage (from anywhere): python3 hardware/production/make_jlcpcb.py
Needs kicad-cli (KiCad 10). With the flatpak build the project must live under $HOME.
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
BOARD = "tangnano9k-kr260-hat"
REV = "rev0.4"
OUT = os.path.join(HERE, "jlcpcb")
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
NO_PART = ("TestPoint", "SolderJumper")
# JLCPCB places a part by the centre of its own library footprint. KiCad pin headers and sockets have their origin
# on pin 1 and their pins along Y; the JLCPCB ones are centred, with the pins along X.
PAD_CENTRED = {"PinHeader_": -90, "PinSocket_": -90}   # footprint name prefix -> rotation correction (degrees)


def kicad(*args):
    r = subprocess.run(["kicad-cli", *args], cwd=HW, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)


def pad_positions(path):
    """Pad centres per reference from an IPC-D-356 export, in mm on the same axes as the position file."""
    text = open(path, encoding="utf-8").read()
    if "UNITS CUST 0" not in text:
        sys.exit("IPC-D-356 export: expected UNITS CUST 0 (0.0001 inch)")
    out = {}
    for line in text.splitlines():
        m = re.search(r"X([+-]\d{6})Y([+-]\d{6})", line)
        if line[:3] in ("317", "327") and m:
            out.setdefault(line[20:26].strip(), []).append((int(m.group(1)) * 0.00254, int(m.group(2)) * 0.00254))
    return out


def main():
    parts = {r["Value|Footprint"]: r for r in csv.DictReader(open(os.path.join(HERE, "jlcpcb_parts.csv"), encoding="utf-8"))}
    work = tempfile.mkdtemp(dir=os.path.expanduser("~"), prefix=".jlcpcb-")   # flatpak kicad-cli writes only under $HOME
    try:
        g = os.path.join(work, "gerber")
        os.makedirs(g)
        kicad("pcb", "export", "gerbers", "-o", g + "/", "--layers", LAYERS, "--no-x2", "--no-netlist",
              "--subtract-soldermask", f"{BOARD}.kicad_pcb")
        kicad("pcb", "export", "drill", "-o", g + "/", "--format", "excellon", "--excellon-units", "mm",
              "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", f"{BOARD}.kicad_pcb")
        kicad("pcb", "export", "pos", "-o", os.path.join(work, "pos.csv"), "--format", "csv", "--units", "mm",
              "--side", "both", "--exclude-dnp", f"{BOARD}.kicad_pcb")
        kicad("pcb", "export", "ipcd356", "-o", os.path.join(work, "pads.d356"), f"{BOARD}.kicad_pcb")
        pads = pad_positions(os.path.join(work, "pads.d356"))
        kicad("sch", "export", "bom", "-o", os.path.join(work, "bom.csv"), "--fields", "Reference,Value,Footprint",
              "--group-by", "Value,Footprint", "--ref-range-delimiter", "", f"{BOARD}.kicad_sch")

        bom, placed = [], set()
        for row in csv.DictReader(open(os.path.join(work, "bom.csv"), encoding="utf-8")):
            fp = row["Footprint"].split(":")[-1]
            if fp.startswith(NO_PART):
                continue
            key = f"{row['Value']}|{fp}"
            if key not in parts:
                sys.exit(f"no entry in jlcpcb_parts.csv for {key}")
            p = parts[key]
            refs = row["Reference"].split(",")
            comment = row["Value"] if fp.startswith(("R_", "C_")) else (p["MPN"] or row["Value"])
            bom.append({"Comment": comment, "Designator": ",".join(refs), "Footprint": fp, "LCSC Part #": p["LCSC"]})
            placed.update(refs)

        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, f"{BOARD}_{REV}_bom_jlcpcb.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #"])
            w.writeheader()
            w.writerows(bom)
        with open(os.path.join(OUT, f"{BOARD}_{REV}_cpl_jlcpcb.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
            w.writeheader()
            n = 0
            for r in csv.DictReader(open(os.path.join(work, "pos.csv"), encoding="utf-8")):
                if r["Ref"] in placed:
                    x, y, rot = float(r["PosX"]), float(r["PosY"]), float(r["Rot"])
                    fix = next((v for k, v in PAD_CENTRED.items() if r["Package"].startswith(k)), None)
                    if fix is not None:
                        xs, ys = zip(*pads[r["Ref"]])
                        x, y, rot = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (rot + fix) % 360
                    w.writerow({"Designator": r["Ref"], "Mid X": f"{x:.4f}mm", "Mid Y": f"{y:.4f}mm",
                                "Layer": "Top" if r["Side"] == "top" else "Bottom",
                                "Rotation": f"{rot:.1f}"})
                    n += 1
        with zipfile.ZipFile(os.path.join(OUT, f"{BOARD}_{REV}_gerber_drill.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for name in sorted(os.listdir(g)):
                if not name.endswith(".gbrjob"):
                    z.write(os.path.join(g, name), name)
        print(f"BOM: {len(bom)} lines, {len(placed)} parts; CPL: {n} rows; files in {OUT}")
        if n != len(placed):
            sys.exit("CPL and BOM disagree")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
