# Tang Nano 9K Custom HAT for AMD Kria KR260

Hardware, firmware, integration and validation requirements for a custom FPGA board based on the Tang Nano 9K, installed directly on the 40-pin J21 header of the KR260.

| Field | Value |
|---|---|
| Document revision | 0.6 — power from the USB-C or from the KR260 J21 5 V (Schottky OR-ing) |
| Date | 2026-10-21 |
| Previous revisions | 0.5 — English translation, KR260 schematic cross-check, PCB prepared for JLCPCB; 0.4 — preliminary schematic and proposed parts; 0.3 — integration with the KR260; 0.2 — consolidation of the HAT scope (all dated 2026-10-21) |
| Host platform | AMD Kria KR260; K26 SOM with XCK26-SFVC784-2LV-C/I (F10) |
| KR260 environment | KAKUEI-OS (customized PetaLinux 2024.2), Vivado/Vitis 2024.2, PL with DPU (DPUCZDX8G) and VCU, applications in Docker containers (R4) |
| Status | Specification with a preliminary schematic and a PCB prepared for JLCPCB fabrication and assembly in KiCad 10 (`hardware/`, Proposed); production files generated for an order, not released; mechanical fit with the KR260 checked against its 3D model (XTP744, F14), with the physical fit check still **Pending**; pinout, outline and PCB still subject to development and validation |
| Planned CAD | KiCad 10 |
| Expansion board FPGA | Gowin GW1NR-LV9QN88PC6/I5, QN88P package |

> **This document is not a release for manufacturing.** The number of usable signals on J21, the clock pins, the voltages, the mechanical fit and the link timing need to be proven in the design. **16 bits at 50 MHz correspond to 100 MB/s raw by calculation, not to a rate already measured or guaranteed.**
>
> **Revision 0.3:** the J21 → K26 map comes from a secondary source and is **preliminary — confirm in XTP743**. The signal allocation on J21 is **Proposed**. Nothing in this revision was measured or validated in hardware.
>
> **Revision 0.4:** the preliminary schematic in `hardware/` was captured in KiCad 10. An ERC with no violations and a netlist checked against the intended connections are document checks, not electrical validation. The new parts are **Proposed** (section 16.1). After the capture, the five sheets were redrawn with wires, power symbols and labels, with no change in connectivity (section 17.1). There is also a PCB study with a provisional outline and automatic routing (section 17.2), which neither defines the mechanics nor is a release for manufacturing.
>
> **Revision 0.5:** the document was translated to English. The J21 → K26 map was cross-checked against the KR260 carrier schematic (cited as XTP743; F12) and the K26 SOM XDC (F13): the 28 signal contacts match with 0 differences, the section 6.4 items are answered except PUDC_B (ISO-14, still **Pending**), and the rails behind the J21 3.3 V and the bank 43/44 VCCO are identified (ISO-10); these are document cross-checks, not hardware validation. The PCB was prepared for JLCPCB fabrication and assembly (section 17.2): English KiCad texts and silkscreen with J21 pin labels, JLCPCB design rules and stackup (Proposed), and the USB pair rerouted on F.Cu without vias (in rev. 0.4: D+ on F.Cu and D− on In2.Cu with 3 vias, 16.0/20.0 mm); other rev. 0.4 values that changed are given next to the new ones in section 17.2. The PUYA P25Q32U Flash, not stocked at JLCPCB and with its datasheet still Pending, was replaced by the Winbond W25Q32JVZPIQ (Proposed; MSPI/boot compatibility with the GW1NR-9 **Pending**), and the Gerber/drill, BOM and CPL files were generated for a JLCPCB order (sections 16 and 17.2). The KR260 carrier 3D model (XTP744, F14) was then read: in the model, J130 and the holes H1/H2 land on J21 and its two header-side holes, so the outline, holes and J21 position move from Pending to Proposed, while the J21 pin 1 position (MEC-02) and a physical fit check stay **Pending** (section 4). The files are not a release: the physical fit check on a KR260, the human design review and the other open items of section 20 remain.
>
> **Revision 0.6:** by design decision (2026-10-21), the HAT runs from either source: its own USB-C or the KR260 J21 5 V (contacts 2 and 4). This replaces “exclusively USB-C” in SYS-05 and PWR-01. Each source reaches +5V through its own B5819W Schottky diode (D3 after the USB-C PTC; D4 after J21, with the 10 µF C14), so neither source can feed the other (ISO-01, section 8.1). The FT2232H becomes self-powered: VBUS reaches its PWRSAV# input through a 4.7k/10k divider (R10/R11), which holds it in suspend while no USB host is present (FT_000061 v2.10, table 3.3 and section 6.2), and its EEPROM must be programmed for self-powered operation with “suspend on DBUS7 low” (section 9). The schematic (ERC with 0 errors and 0 warnings; netlist compared by script with rev. 0.5, only the intended differences) and the PCB (DRC with schematic parity: 0 errors, 0 unconnected pads) were updated and the production files regenerated (sections 16 and 17). These are document checks, not hardware validation; the TMI7003C input range with the lower +5V and the PWR-04 budget against the 1.0 A of J21 are **Pending**.

## 1. Objective, origin and scope

Create a **new PCB with the FPGA soldered directly onto it**, preserving the selected set of Tang Nano 9K functions and adding a communication interface with the KR260 programmable logic through J21. This is not an adapter board for plugging in a ready-made Tang Nano 9K.

The HAT must be able to operate in two ways:

- **Installed on the KR260:** powered by the KR260 through J21 (5 V on contacts 2 and 4) or by its own USB-C (SYS-05), with FPGA ↔ FPGA communication enabled when needed.
- **Standalone:** powered and programmed over USB-C, without depending on the presence of the KR260 for its local functions.

The priority of the link is to achieve **the highest demonstrable sustained speed with electrical and timing margin**, without sacrificing data integrity or low latency. The ARM/Linux processor must not be responsible for sampling each word of the external bus.

### 1.1 Documentary basis and conventions

This consolidation uses the draft **“Placa custom Tang Nano 9K + Pmod: requisitos” (“Custom Tang Nano 9K + Pmod board: requirements”), dated 2026-10-20** (R1), and the later design decisions (R2, R3). The original draft described a different connector and a different link; its information must not be transplanted automatically to J21.

Revision 0.3 incorporates the KR260 integration survey of 2026-10-21 (R5), based on AMD documentation and community sources, and the system context (R4):

- facts from official AMD documentation (**F1–F11**, section 21.3) are entered as fact, with the source cited;
- data from secondary sources (**S1–S4**, section 21.4) appear as **preliminary — confirm in XTP743**, or in the indicated official document when the data does not come from the schematic;
- new allocations and solutions are entered as **Proposed**, and what is not confirmed remains **Pending**. No new item was marked as Decided.

The primary sources listed at the end must be consulted during implementation. Their citation in this README **does not mean that their PDFs, pinouts or constraints were revalidated in this consolidation**. In revision 0.3, the only check made was a transcription check: the pin names of the J21 → K26 map against the pinout file `xczu5evsfvc784pkg.txt` (section 6.3). In revision 0.4, the schematic capture used documents opened in this revision: the Tang Nano 9K 3674 schematic and interactive BOM, Gowin's UG803E, UG119E and DS117E, the FT2232H datasheet and the TI datasheets of the proposed parts (section 21.2). The new choices of revision 0.4 are **Proposed**. In revision 0.5, local copies of AMD files were read and entered as facts F12 to F14 (section 21.3): the KR260 carrier schematic (cited as XTP743), the K26 SOM XDC and the XTP744 carrier 3D model. The J21 → K26 map, the carrier parts on the J21 path, the J21 power rails and the mechanical fit were cross-checked against them (sections 4, 6.3, 6.4, 8.3 and 17.2) as document and model checks, without hardware measurements.

| Marking | Meaning |
|---|---|
| **Decided** | Explicit design choice or requirement expressed in the source draft |
| **Proposed** | Technical solution discussed or recommended detailing; still requires approval/validation |
| **Pending** | There is not enough evidence or no final choice |
| **Validation requirement** | Criterion to be demonstrated; not a statement that the hardware already meets it |

The isolation, protocol, test and release details below make up the **proposed technical baseline**. They make the discussed objectives verifiable, without representing circuits already implemented. In the new requirements of revision 0.3, the status appears in bold at the start of the text.

### 1.2 Out of scope for this revision

Do not include Pmods, board-to-board link cables, HDMI, a new PCIe interface, a USB bridge dedicated to the main data stream or an FPGA change. Electrical/functional compatibility with a conventional Raspberry Pi is not an acceptance criterion: **the target is the KR260**.

## 2. Consolidated decisions

| ID | Item | Baseline | Status |
|---|---|---|---|
| SYS-01 | Host | AMD Kria KR260, not a conventional Raspberry Pi | Decided |
| SYS-02 | Mounting | HAT-type board, plugged into the 40-pin J21 header | Decided; mechanics to be validated |
| SYS-03 | Pmods | No Pmod connector | Decided |
| SYS-04 | FPGA | Same GW1NR-LV9QN88PC6/I5 as the reference | Decided |
| SYS-05 | Power | 5 V from the USB-C or from the KR260 J21 (contacts 2 and 4), either one alone, through Schottky OR-ing (section 8.1); until rev. 0.5, exclusively USB-C | Decided (rev. 0.6) |
| SYS-06 | microSD/TF | Keep the slot and its functionality | Decided |
| SYS-07 | HDMI | Remove the connector and the circuits exclusive to this interface | Decided |
| SYS-08 | Communication with the KR260 | Available in hardware; optional use in firmware | Decided |
| SYS-09 | Priority | Maximum real communication speed compatible with this design | Decided |
| SYS-10 | Flash, PSRAM, clock, LEDs and buttons | Preserve the selected functions of the Tang Nano 9K | Baseline requirement |
| SYS-11 | Programming bridge | FT2232H replacing the BL702 | Proposed in the base draft |
| SYS-12 | RGB/SPI LCD interfaces | Do not include in the current baseline | Proposed, kept from the previous scope |
| SYS-13 | Original Tang GPIO headers | Not reproduced automatically; no commitment to keep all of them exposed | Pending, depending on need |
| SYS-14 | PCB layers | Four | Proposed |
| SYS-15 | Dimensions | Discussed reference of 65 × 56.5 mm | Proposed; checked against the XTP744 3D model in rev. 0.5 (F14), physical fit check pending |
| SYS-16 | Main interface | 16-bit parallel bus with clock and control | Proposed, conditional on the pinout and the timing |
| SYS-17 | Initial frequency | 50 MHz; investigate higher frequencies after validation | Proposed |
| SYS-18 | Direction of the main flow | Tang → KR260 as the starting point | Proposed; final duplex pending |

**Scope replacements:** the two previously requested Pmods, the connection to the KR260 Pmods 3/4 and the 60 × 40 mm size are no longer requirements of this version. No circuit exclusive to these connections should remain through automatic copying.

The expression “based on the Tang Nano 9K” **does not mean preserving all external interfaces of the commercial board**: HDMI is removed, LCDs are outside the proposed baseline, the USB implementation changes and the exposure of the GPIOs changes.

## 3. Proposed functional architecture

```text
                            USB-C
                         5 V + USB 2.0
                            |
             +--------------+------------------+
             |                                 |
   Protection / regulators                   FT2232H
   +5V: USB-C 5 V or J21 5 V            JTAG A / UART B
   (contacts 2 and 4), Schottky OR             |
      3V3 / 1V8 / 1V2                          |
             |                                 |
             |                     JTAG conversion 3V3 <-> 1V8
             |                                 |
             +------------+--------------------+
                          |
                     GW1NR-9
                +---------+----------+
                |         |          |
            SPI Flash   microSD   LEDs / buttons
                |
           Application logic
                |
           FIFO / parallel TX
                |
   Protection and isolation for unpowered states
   (buffer OE controlled by LINK_EN - proposed)
                |
       2x20 female header on the bottom side
                |
         KR260 J21 -> K26 PL
                |
       RX / verification / CDC FIFO
                |
             AXI-Stream
                |
        AXI DMA -> DDR -> software
```

The diagram is functional, not a netlist. Flash, microSD and controls are independent connections of the FPGA. The AXI DMA/DDR chain is an integration proposal and is not mandatory for a consumer that operates entirely in the PL.

In revision 0.3, it is proposed that `LINK_EN`, driven by the KR260 PL, enable the HAT drivers in hardware (ISO-11), and that the RX go into the same bitstream as the DPU and the VCU (KRIA-02).

## 4. Mechanical requirements

| ID | Requirement |
|---|---|
| MEC-01 | Use a 40-way, 2 × 20, 2.54 mm pitch female connector on the bottom side, aligned with the actual J21. |
| MEC-02 | Check the numbering and mirroring between symbol, footprint, bottom view and host connector. Rev. 0.5: the XTP744 model (F14) does not mark pin 1, so the J21 pin 1 position comes from S2 and remains **Pending** until a visual check on a real KR260 (see below). |
| MEC-03 | Confirm the outline, hole coordinates and header position in a mechanical drawing; do not infer these coordinates from the HAT name. Rev. 0.5: **Proposed** after a check against the XTP744 3D model (F14): J130 and the holes H1/H2 land on J21 and its two header-side holes (see below); a physical fit check is still pending. |
| MEC-04 | Validate the height of standoffs and connectors against the actual KR260 assembly, including heatsink, fan and nearby connectors. Rev. 0.5 (**Proposed**, from the model only): 8.5 mm J130 socket and 11 mm M2.5 standoffs, with the HAT bottom about 10.9 mm above the carrier; the nearest tall KR260 parts are listed below (F14). Validation on the actual assembly is still pending. |
| MEC-05 | Keep USB-C, microSD, buttons and test points usable with the HAT installed. Rev. 0.5: in the models, USB-C, microSD, both buttons, the JTAG header and the test points are on the part of the HAT that overhangs the carrier edge, so they stay reachable with the HAT installed (geometric statement, F14). |
| MEC-06 | Do not obstruct cooling or require disassembling the KR260 to insert/remove the card or the programming cable. |
| MEC-07 | Provide mechanical fastening and keepouts for screw heads/standoffs, without relying only on the friction of the header. Rev. 0.5 (**Proposed**): 11 mm M2.5 standoffs at H1 and H2, on the two KR260 holes next to J21 (F14); H3 and H4 fall outside the carrier and have no support (optional feet). |
| MEC-08 | Mark pin 1, mounting orientation, board name, revision and power on the silkscreen. |
| MEC-09 | Define the PCB thickness, number/diameter of holes and tolerances together with the manufacturer and the chosen connectors. |
| MEC-10 | **Proposed.** Use the carrier 3D CAD model (XTP744) as the source for the outline, holes and heights on the KR260 side, recording the revision of the downloaded package. Rev. 0.5: read as F14 (package readme v1.0, 2022; `KR260-startkit-A02.stp`, assembly KR260_STARTKIT_ASM of 2021-10-15, carrier 128_05101_01 rev A02). |
| MEC-11 | **Proposed** (rev. 0.5, F14; Pending in rev. 0.4). The HAT form factor assumes the Raspberry Pi mounting holes. The carrier 3D model has two 2.77 mm holes on the J21 centreline, 58.0 mm apart and 4.87 mm beyond the end pins: the two header-side holes of the Raspberry Pi HAT pattern. The carrier schematic shows two grounded mounting holes, MH11 and MH12, on the J21 sheet (F12, sheet 12); matching them to the model holes is an inference from the geometry, because the STEP has no reference designators. The HAT holes H1 and H2 land on the two model holes (see below), which is the basis for the fastening of MEC-07 and the outline of SYS-15, still subject to a physical fit check. |

**Dimensions not yet approved:** 65 × 56.5 mm (the Raspberry Pi HAT size) was the initial reference, not a measurement taken from an official drawing at this stage. Confirm the applicable mechanical specification and, above all, the fit on the KR260 before freezing the outline. In revision 0.5, the outline was checked against the KR260 3D model (F14, below); the physical fit on a KR260 is still to be confirmed.

**Kit envelope (F3):** with the active thermal solution (fan and heatsink), the KR260 kit measures 119 × 140 × 36 mm, according to the official product page. This is the external size of the kit; it does not give the position of J21 or the clearance above the nearby components, which must come from XTP744. Revision 0.5 takes them from XTP744 (F14, below).

**Fit on the KR260 3D model (F14, revision 0.5; model check, no hardware measured):** placed with its body hanging outward over the right edge of the carrier, the HAT maps as HAT (x, y) → carrier (125.94 + y, 38.31 + x) mm, so J130 pin 1 (8.37, 4.77) lands on the J21 outer column at (130.71, 46.68), and the holes H1 (3.5, 3.5) and H2 (61.5, 3.5) land on the two carrier holes at (129.44, 41.81) and (129.44, 99.81). The HAT covers only a 9.1 mm strip of the carrier, where the only KR260 part is J21 and the only HAT bottom-side part is J130; the other ~47 mm overhang the carrier edge. The nearest tall KR260 parts are the dual RJ45 (top 27.0 mm above the carrier) at 9.7 mm from the HAT outline, the SFP cage (10.2 mm) at 14.5 mm, the SOM fan heatsink (29.2 mm) at 40.8 mm and the dual USB (15.7 mm) at 47.3 mm. With the 8.5 mm J130 socket on the J21 plastic body (top at 2.40 mm), the HAT bottom is about 10.9 mm above the carrier, held by 11 mm M2.5 standoffs at H1 and H2 (**Proposed**); H3 and H4 fall outside the carrier and have no support (optional feet). The J21 pins stand 5.84 mm above their plastic body.

**Fit indication and orientation (S2 — preliminary):** the LogicTronix tutorial shows a Sense HAT mounted on J21. This indicates that a commercial HAT physically fits the header, but it does not validate the fastening, the clearances or the outline of this HAT. The 3D model (F14) does not mark pin 1, so the orientation still comes from this photo: the Sense HAT hangs off the right edge of the KR260, and with the HAT convention (HAT body on the odd-row side), J21 pin 1 is the outer column (x 130.71) at the end toward the Pmod connectors (y 46.69). A HAT facing inward would hit the SOM fan heatsink and the dual RJ45 (F14). The J21 pin 1 position remains **Pending** until a visual check on a real KR260 (MEC-02).

Deliverable for this stage: 3D model of the assembly or overlay drawing with all critical clearances dimensioned, using XTP744 as the carrier model. In revision 0.5, a KiCad 3D view of the HAT on the KR260 model exists; it is kept outside the repository because it shows the licensed model, and the clearances obtained from the model are listed above.

## 5. FPGA resources and compatibility with the Tang Nano 9K

### 5.1 Reference voltages and pins

The values below come from the provided draft and must be cross-checked with the datasheet/pinout of the **exact part number and package**.

| Domain | Design voltage in the base draft | Note |
|---|---|---|
| Core | 1.2 V | Size tolerance, ripple and current according to the manufacturer |
| VCCIO0/1/2 | 3.3 V | Candidates for the interface with J21; on the K26 side, the carrier ties the VCCO of banks 43 and 44 to PL_3V3, shown as 3.3 V/3 A (F12) |
| VCCIO3 | 1.8 V | Supply tied to the PSRAM embedded in the QN88P according to the base draft |

The base draft states a range of **1.71 to 1.89 V for VCCIO3** on the QN88P. This is a critical requirement to be confirmed in the Gowin document: **do not raise VCCIO3 to 3.3 V to accommodate the expansion connector**.

| Preserved resource | Pins stated in the base draft | Requirement |
|---|---|---|
| UART | 17, 18 | Preserve the signals and directions of the reference |
| 27 MHz clock reference | 52 | Preserve frequency and functional circuit |
| P25Q32U SPI Flash (W25Q32JVZPIQ proposed in rev. 0.5, section 16.1) | 59–62 | Preserve interface and programming compatibility |
| microSD/TF card | 36–39 | Preserve the interface mode of the reference Tang |
| Buttons | 3, 4 | Two user buttons, respecting the 1.8 V bank |
| JTAG | 5–8 | Validate TCK/TDI/TDO/TMS pin by pin |
| RECONFIG_N | 9 | Preserve reconfiguration functionality |
| LEDs | 10, 11, 13–16 | Six user LEDs with a compatible circuit |
| MODE1/MODE0 | 87, 88 | Preserve the straps and boot sequence of the reference |

The ranges in this table **do not replace a net map**. Publish the complete correspondence between signal name and pin number before generating the final schematic.

### 5.2 Preservation requirements

**FPGA-01:** keep the FPGA and the integrated PSRAM associated with the specified component; do not assume additional external PSRAM.

**FPGA-02:** keep the original pins of the preserved functions. A change must be documented and approved, with the impact on the firmware identified; do not change the pinout silently to make routing easier.

**FPGA-03:** preserve boot from Flash, volatile programming and JTAG recovery access, as supported by the chosen set.

**FPGA-04:** keep the correct circuit of the 27 MHz clock source. Confirm in the reference schematic whether each component is an oscillator, a crystal or part of an active circuit; do not change the topology based only on the nominal frequency.

**FPGA-05:** keep the microSD with validated decoupling, biasing and pinout. The mention of four signals in the base draft does not authorize assuming a native four-bit SDIO interface.

**FPGA-06:** update the map of free GPIOs after removing HDMI/LCD and reserving clock, programming and memories. Pins of a 1.8 V bank are not directly available 3.3 V GPIOs.

## 6. J21 header: mandatory mapping

UG1092 identifies J21 as the Raspberry Pi expansion header for HATs (F1), and the official KR260 page states 26 I/Os on this header (F3). The pin-by-pin mapping (section 6.3) comes from a secondary source (S1), with the pin names taken from the AMD pinout file (F11); in revision 0.5 it was **cross-checked against the KR260 carrier schematic (F12) and the K26 SOM XDC (F13), with 0 differences for the 28 signal contacts**. This is a document cross-check, not hardware validation, and the pin allocation remains Proposed (section 7.3). The criterion is still the number of suitable signals obtained by reading the KR260 schematic and the K26 SOM mapping, which revision 0.5 did with F12 and F13 (sections 6.3 and 6.4).

Do not copy the Pmod pinout of the original draft to the 40-pin header.

### 6.1 Pinout spreadsheet

`docs/pinout-j21.csv` and its readable version, `docs/pinout.md`, were created in revision 0.3 as a preliminary version and completed from F12 and F13 in revision 0.5. Each physical contact of J21 must have a row with:

| Column | Mandatory content |
|---|---|
| `j21_pin` | Physical number from 1 to 40 |
| `kr260_net` | Exact net name on the carrier |
| `carrier_components` | Resistors, filters, level translations or protections in the path |
| `som_pin` | Corresponding contact of the SOM connector |
| `k26_package_pin` | Physical pin usable in the Vivado constraints |
| `k26_bank_vcco` | Bank, supply and permitted I/O standard |
| `k26_function` | PL/PS, shared function and clock capability |
| `hat_net` | Net name on the HAT |
| `gowin_pin_bank` | GW1NR pin, bank and VCCIO |
| `direction` | Direction in operation and during reset |
| `power_off_state` | Behavior when one of the boards is powered off |
| `source` | Document, revision and sheet that support the mapping |
| `hat_silkscreen` | Silkscreen label of the contact on the top side of the HAT (added in revision 0.5; follows the Proposed allocation) |

`hat_net`, `direction` and `power_off_state` carry the allocation of section 7.3 with the prefix `Proposed:`. Since revision 0.4, `gowin_pin_bank` carries the Gowin pin and the path on the HAT (buffer and resistor), also as Proposed, according to the preliminary schematic. In revision 0.5, `kr260_net`, `carrier_components`, `som_pin`, `k26_bank_vcco` and `source` are filled from the carrier schematic (F12) and the K26 SOM XDC (F13), so no field is `PENDING (XTP743)` any more, and `hat_silkscreen` gives the J21 pin labels of the board (section 17.2). `—` indicates a field that does not apply to a power or GND contact.

### 6.2 Criteria for selecting signals

**J21-01:** confirm which signals reach the PL. Do not declare that all GPIO contacts are equivalent or suitable for synchronous capture.

**J21-02:** reserve a clock path that reaches an appropriate resource on the K26 and an appropriate pin on the Gowin, according to the chosen direction. A regular GPIO must not be treated as an automatic substitute for a dedicated clock input.

**J21-03:** verify the voltage, input limits, drive capability and register/capture resources of each bank. Prefer a grouping that simplifies timing; document the use of multiple banks.

**J21-04:** identify the contacts for 5 V, 3.3 V, GND, identification and reserved signals before assigning nets. Do not reuse power or GND contacts as data.

**J21-05 (revised in rev. 0.3 and 0.5):** according to S1 and to the carrier schematic and K26 SOM XDC (F12, F13), ID pins 27 and 28 (ID_SD/ID_SC, GPIO0/1) go to the K26 PL; on the carrier they have 3.90k pull-ups to RPI_3V3 (R330/R331, F12). The PL only exists after a bitstream is loaded, and in the standard Kria images it is loaded after Linux (F9). Therefore there is no automatic detection of an identification EEPROM at boot. **Proposed:** remove the HAT identification EEPROM from the scope. Pins 27 and 28 remain reserved, unconnected on the HAT. Automatic recognition and formal HAT compliance remain pending scope, not assumed functionality.

**J21-06:** confirm that the Vivado project and the software do not enable other peripherals on the same pins. SPI, I²C and UART over J21 are not promised simultaneously with the complete parallel bus.

**J21-07 (new in rev. 0.3, revised in rev. 0.5):** **Proposed.** The section 6.4 items were answered in revision 0.5 from the carrier schematic (F12) and the K26 SOM XDC (F13), except PUDC_B, which these documents do not give (ISO-14, **Pending**). Freezing the pinout is the proposed next step and still requires approval.

**J21-08 (new in rev. 0.3, revised in rev. 0.5):** **Pending** (optional). For the 28 J21 signals, the K26 SOM XDC (F13) gives the same package pins and pin names as `xczu5evsfvc784pkg.txt` (F11), and the `source` column records it. Confirming them with the xck26 part in Vivado remains an optional extra check of the pinout equivalence between XCK26 and XCZU5EV; record the result in the `source` column if it is done.

### 6.3 J21 → K26 map (cross-checked against F12 and F13)

**Cross-checked against F12 and F13 in revision 0.5, with 0 differences.** Signals and K26 pins: S1, a community XDC that, according to the author, derives from the master XDC included in the XTP743 download and places the 28 signals GPIO0–27, including ID_SD/ID_SC, on PL pins, all in LVCMOS33. Package pin names: F11 (`xczu5evsfvc784pkg.txt`), identical in the K26 SOM XDC (F13; optional Vivado check with the xck26 part, J21-08). Power and GND: S3 (standard Raspberry Pi pinout), matching the carrier schematic (F12, sheet 12). The carrier net and SOM connector pin of each contact are in `docs/pinout-j21.csv`.

| J21 pin | RPi signal | K26 pin | Package pin name | Bank |
|---:|---|---|---|---|
| 1 | 3V3 | — | — | — |
| 2 | 5V | — | — | — |
| 3 | GPIO2 (I²C SDA) | AE15 | IO_L1P_AD15P_44 | 44 |
| 4 | 5V | — | — | — |
| 5 | GPIO3 (I²C SCL) | AE14 | IO_L1N_AD15N_44 | 44 |
| 6 | GND | — | — | — |
| 7 | GPIO4 | AG14 | IO_L2P_AD14P_44 | 44 |
| 8 | GPIO14 | W14 | IO_L9P_AD11P_44 | 44 |
| 9 | GND | — | — | — |
| 10 | GPIO15 | W13 | IO_L9N_AD11N_44 | 44 |
| 11 | GPIO17 | AB14 | IO_L8N_HDGC_44 | 44 |
| 12 | GPIO18 | Y14 | IO_L10P_AD10P_44 | 44 |
| 13 | GPIO27 | AB9 | IO_L12N_AD0N_43 | 43 |
| 14 | GND | — | — | — |
| 15 | GPIO22 | Y12 | IO_L12P_AD8P_44 | 44 |
| 16 | GPIO23 | AA12 | IO_L12N_AD8N_44 | 44 |
| 17 | 3V3 | — | — | — |
| 18 | GPIO24 | Y9 | IO_L11P_AD1P_43 | 43 |
| 19 | GPIO10 | AE13 | IO_L4P_AD12P_44 | 44 |
| 20 | GND | — | — | — |
| 21 | GPIO9 | AC13 | IO_L6N_HDGC_44 | 44 |
| 22 | GPIO25 | AA8 | IO_L11N_AD1N_43 | 43 |
| 23 | GPIO11 | AF13 | IO_L4N_AD12N_44 | 44 |
| 24 | GPIO8 | AC14 | IO_L6P_HDGC_44 | 44 |
| 25 | GND | — | — | — |
| 26 | GPIO7 | AH13 | IO_L3N_AD13N_44 | 44 |
| 27 | GPIO0 (ID_SD) | AD15 | IO_L5P_HDGC_44 | 44 |
| 28 | GPIO1 (ID_SC) | AD14 | IO_L5N_HDGC_44 | 44 |
| 29 | GPIO5 | AH14 | IO_L2N_AD14N_44 | 44 |
| 30 | GND | — | — | — |
| 31 | GPIO6 | AG13 | IO_L3P_AD13P_44 | 44 |
| 32 | GPIO12 | AA13 | IO_L7P_HDGC_44 | 44 |
| 33 | GPIO13 | AB13 | IO_L7N_HDGC_44 | 44 |
| 34 | GND | — | — | — |
| 35 | GPIO19 | Y13 | IO_L10N_AD10N_44 | 44 |
| 36 | GPIO16 | AB15 | IO_L8P_HDGC_44 | 44 |
| 37 | GPIO26 | AB10 | IO_L12P_AD0P_43 | 43 |
| 38 | GPIO20 | W12 | IO_L11P_AD9P_44 | 44 |
| 39 | GND | — | — | — |
| 40 | GPIO21 | W11 | IO_L11N_AD9N_44 | 44 |

Notes:

- GPIO0–23 occupy the 24 I/Os of bank 44, which is entirely dedicated to J21.
- GPIO24–27 are in bank 43, shared with Pmods 3 and 4.
- P-side HDGC pins, suitable for a single-ended clock (F5, F7): 24, 27, 32 and 36. Pin 27 is an ID pin (J21-05).
- S2 uses AE15/AE14 for I²C (GPIO2/3) and AA12 for the interrupt on pin 16 (GPIO23), which is consistent with S1.
- All signals appear in S1 as LVCMOS33; the 3.3 V VCCO was first **inferred** from this and is now documented: VCCO_HDC (bank 44) and VCCO_HDB (bank 43) are tied to PL_3V3 (F12; section 6.4).

**Transcription check (2026-10-21):** the 28 pin/name pairs and the banks in the table match `xczu5evsfvc784pkg.txt`. The file classifies banks 43 and 44 as HD, lists 24 I/Os in bank 44, all present in the table, and eight HDGC pins (four pairs) in that bank. The check does not replace J21-08 or XTP743.

**Cross-check against F12 and F13 (revision 0.5, 2026-10-21):** each of the 28 signal contacts was traced from J21 to its HDC/HDB net (F12, sheet 12), to the som240_2 pin (F12, sheet 7) and to the package pin and pin name (F13), with 0 differences from the table above. The HDC nets are in bank 44 and HDB20–HDB23 in bank 43 (contacts 13, 18, 22 and 37). Contact 32 is HDC12 = som240_2_b52 = AA13, IO_L7P_HDGC_44. The carrier schematic adds the suffix _CC only to HDC00, HDC08 and HDC16, while F13 also places HDC01, HDC09, HDC12, HDC13 and HDC17 on HDGC pins. This is a document cross-check, not hardware validation.

**26 × 28 discrepancy (Pending):** the KR260 page states 26 I/Os on the header (F3), while S1 connects 28 signals, GPIO0–27, to PL pins. The carrier schematic also connects all 28 signal contacts, including ID_SD/ID_SC (27 and 28), to SOM connector pins, with carrier pull-ups on contacts 3, 5, 27 and 28 (F12). One possible reading, not confirmed, is that the 26 of F3 does not count the two ID pins; the discrepancy remains unresolved. The allocation of section 7.3 leaves contacts 3, 5, 27 and 28 and three of the four bank 43 contacts unused by the link; it only still holds with 26 I/Os if the two contacts left out of the count are among these.

### 6.4 Carrier schematic items (cited as XTP743)

For each J21 contact, the following items were to be confirmed in the carrier schematic (cited as XTP743), recording revision and sheet in the `source` column. Results of revision 0.5, from F12 and F13 (document checks, not hardware validation):

- exact net name and SOM connector contact (`kr260_net`, `som_pin`): found for all 40 contacts (F12, sheets 12 and 7) and entered in `docs/pinout-j21.csv`;
- series resistors in the path: none; the signal contacts go straight to the SOM connector, without level shifters (F12);
- ESD protection in the path: none; sheet 12 holds only J21, the two power switches and their resistors, the four pull-ups, capacitors and two mounting holes (F12);
- pull-ups on GPIO2/3 (pins 3 and 5) and on ID_SD/ID_SC (pins 27 and 28): 4.70k to RPI_3V3 on 3 and 5 (R326/R327) and 3.90k to RPI_3V3 on 27 and 28 (R330/R331); the other signal contacts, including the HAT inputs 13, 31 and 33, have no carrier pull-up (F12);
- VCCO of banks 43 and 44 (until revision 0.4, 3.3 V only inferred from the LVCMOS33 of S1): VCCO_HDB (bank 43) and VCCO_HDC (bank 44) are tied to PL_3V3, shown as 3.3 V/3 A and enabled by VCCOEN_PL_M2C (F12, sheets 7 and 5);
- rail that supplies the J21 3.3 V and its relationship with the VCCOs (ISO-10): RPI_3V3 comes from PL_3V3 through the STMPS2161 switch U74 (F12, sheet 12; see ISO-10);
- state of PUDC_B on the K26 (ISO-14; also in DS987): not given in F12 or F13 (F13 only lists the net FPGA_PUDC_B on package pin U7); still **Pending**;
- the 26 × 28 discrepancy of section 6.3: F12 connects all 28 signal contacts; the difference from the 26 I/Os of F3 is still open (section 6.3).

## 7. Pin budget and proposed logical distribution

### 7.1 Link signals

| Logical signal | Quantity | Proposed direction | Function |
|---|---:|---|---|
| `LINK_DATA[15:0]` | 16 | HAT → KR260 | Data word |
| `LINK_CLK` | 1 | HAT → KR260 | Clock forwarded along with the data |
| `LINK_VALID` | 1 | HAT → KR260 | Valid word |
| `LINK_READY` | 1 | KR260 → HAT | Flow control, according to a protocol to be defined |
| `LINK_RESET_N` | 1 | KR260 → HAT | Logical reset of the link, not a direct connection to the 1.8 V RECONFIG_N |
| `LINK_EN` | 1 | KR260 → HAT | New in rev. 0.3 (Proposed). Quasi-static link enable; controls in hardware the OE of the HAT output buffers (ISO-11, LINK-10) |
| Reserve | Up to 7 with the 28 signals of S1 and F12, or up to 5 with the 26 I/Os of F3, conditionally | To be defined | Status, IRQ, command or expansion; contacts 3, 5, 27 and 28 stay reserved because of the carrier pull-ups (section 7.3) |

The interface above uses **21 signals**: the 20 of revision 0.2 plus `LINK_EN`. If 26 usable signals are confirmed (F3), five will remain; with the 28 of S1 and F12, seven will remain, of which four (3, 5, 27 and 28) stay reserved because of the carrier pull-ups (section 7.3). This count does not demonstrate that the physical or electrical allocation is possible.

### 7.2 Budget on the Gowin

The base draft states 48 pins in the 3.3 V banks, of which UART, clock, Flash and microSD occupy 11. With 21 signals in the link, the preliminary count is:

```text
48 pins (base draft) - 11 preserved functions - 21 link signals = 16 remaining
```

If all remaining J21 signal contacts are also connected to the Gowin, 11 would remain with 26 I/Os (five auxiliary) or 9 with the 28 signals of S1 (seven auxiliary).

The preliminary schematic of revision 0.4 adds `LINK_TX_EN`, an internal HAT signal that does not go through J21 (ISO-15). With it, the count becomes `48 - 11 - 22 = 15` free pins; the pins used are in section 17.1. Validate this availability in the actual package, including special functions. **The previous count of 21 free GPIOs was for two 16-signal Pmods and does not apply automatically to the new link.**

No physical pin should be chosen just because it is left over in this count.

### 7.3 Proposed allocation on J21

**Proposed.** Allocation made on the map of section 6.3, cross-checked against F12 and F13 in revision 0.5; no pin in this table is decided.

| Signal | J21 pin(s) | K26 pin(s) (F12, F13) | Bank | Criterion |
|---|---|---|---|---|
| `LINK_CLK` (HAT → KR260) | 32 | AA13, IO_L7P_HDGC_44 | 44 | P-side HDGC, suitable for a single-ended clock (F5, F7), between GNDs 30 and 34 |
| `LINK_EN` (KR260 → HAT) | 31 | AG13, IO_L3P_AD13P_44 | 44 | New, quasi-static signal; it sits opposite the clock, the best position for a static signal |
| `LINK_DATA[15:0]`, `LINK_VALID`, `LINK_READY` | 7, 8, 10, 11, 12, 15, 16, 19, 21, 23, 24, 26, 29, 33, 35, 36, 38 and 40 | See section 6.3 | 44 | 18 pins; the bit order is left to the HAT routing; avoid high-activity bits on 29 and 33, on the clock diagonal |
| `LINK_RESET_N` and reserves | 13, 18, 22 and 37 | AB9, Y9, AA8 and AB10 | 43 | Bank shared with Pmods 3 and 4; the `LINK_RESET_N` pin comes from these four (choice Pending) |
| Reserved, unconnected on the HAT | 3 and 5 | AE15 and AE14 | 44 | Carrier I²C pull-ups (GPIO2/3): 4.70k to RPI_3V3 (R326/R327, F12) |
| Reserved, unconnected on the HAT | 27 and 28 | AD15 and AD14 | 44 | ID pins (ID_SD/ID_SC) with carrier pull-ups of 3.90k to RPI_3V3 (R330/R331, F12); see J21-05 |
| 5 V input (rev. 0.6) | 2 and 4 (5 V, RPI_5V0) | — | — | Feed +5V through D4 (PWR-01); the Schottky OR-ing keeps ISO-01 |
| Power, unconnected on the HAT | 1 and 17 (3.3 V) | — | — | No power connection on the HAT (ISO-02) |
| GND | 6, 9, 14, 20, 25, 30, 34 and 39 | — | — | All connected to the HAT ground plane (ISO-03) |

- **Alternatives for `LINK_CLK`:** pins 24 and 36 are also P-side HDGC and serve as an alternative, at the cost of reassigning two data signals. Pin 27 is also P-side HDGC, but it is an ID pin and is reserved.
- **Clock neighborhood:** pin 32 sits between GNDs 30 and 34; 31, opposite it, gets `LINK_EN`, which is quasi-static; pins 29 and 33, on the diagonal, must not get high-activity bits. Pin 33 (AB13) is the N side of the clock pair and can be a regular I/O, but not another clock (F7).
- **`LINK_EN` in bank 44:** since the HAT only transmits to bank 44, a high level on `LINK_EN` indicates that this bank is powered and that the PL is configured, under the conditions of section 8.3.
- **Bank 43:** gets `LINK_RESET_N` (KR260 → HAT) and the reserves; no HAT → KR260 line is in this bank.
- **Carrier path (F12):** all other signal contacts go straight to the SOM connector, with no series resistor, level shifter or carrier pull-up; this includes the HAT inputs 13, 31 and 33 (ISO-12).
- **Count:** the link goes from 20 to 21 signals (sections 7.1 and 7.2).
- **Rev. 0.4 (Proposed):** the preliminary schematic fixes D0–D15 on contacts 7, 8, 10, 11, 12, 15, 16, 19, 21, 23, 24, 26, 35, 36, 38 and 40, `LINK_VALID` on 29 and `LINK_READY` on 33 (the clock diagonals get the lowest-activity signals) and `LINK_RESET_N` on 13. Contacts 18, 22 and 37 are left unconnected. The bit order may change during routing; see `docs/pinout.md`.

## 8. Power and board-to-board safety

### 8.1 Power inputs: USB-C and J21

**PWR-01 (Decided in rev. 0.6):** the HAT runs from the 5 V of its USB-C or from the KR260 J21 5 V (RPI_5V0 on contacts 2 and 4, F12), with either source alone. Until rev. 0.5 this requirement read “power exclusively through the 5 V USB-C input”. The sources only meet on +5V, each through its own Schottky diode: D3 (B5819W) after the USB-C PTC F1, and D4 (B5819W) after J21, with a 10 µF input capacitor (C14). D4 keeps the USB-C 5 V out of the KR260 J21 5 V and D3 keeps the KR260 5 V out of the USB VBUS (ISO-01, ISO-04). Consequences, **Proposed**:

- +5V sits one Schottky drop below the active source. The JLCPCB catalog gives 600 mV at 1 A for the B5819W (C8598); with a USB source at the low end of its tolerance and the PTC drop, +5V can approach 4.2 V. The TMI7003C minimum input voltage and dropout are **Pending** (datasheet not consulted, PWR-04).
- The J21 5 V is limited to 1.0 A (F1), through the STMPS2161 switch U73 on the carrier (F12). The J21 path has no PTC of its own: the carrier switch is its current limit, and the PWR-04 budget must stay below 1.0 A with margin.
- With both sources present, the one with the higher voltage supplies the board; there is no priority logic.
- The reverse leakage of D3 reaches the USB VBUS when only J21 supplies the board; the 14.7 kΩ PWRSAV# divider (R10 + R11, section 9) loads that node.
- Hot-plug stays not advertised (section 8.3): inserting the HAT into a powered KR260 charges C14 and the +5V capacitors through the U73 current limit.

**PWR-02:** provide for USB-C operation as a consumer/device, with 5.1 kΩ Rd resistors on CC1 and CC2 as proposed in the base draft, ESD protection and correct receptacle connections. The available current must be determined by the source and the applicable USB mode; the presence of the USB-C connector does not authorize assuming an arbitrary current.

**PWR-03:** size a resettable fuse or equivalent protection, TVS, inrush current, voltage drop and undervoltage behavior. Do not require USB Power Delivery above 5 V. Since rev. 0.6, the TVS D1 sits on +5V, after D3 and D4, so it covers both inputs; F1 only protects the USB-C path.

**PWR-04:** create a per-rail budget including the FPGA at the target load, PSRAM, Flash, microSD writes, FT2232H, translators/isolators, LEDs and an explicit margin, and check it against the 1.0 A of the J21 5 V (F1) and the current offered by the USB source (PWR-02). Record typical consumption, estimated worst case and prototype measurements.

### 8.2 Regulators and domains

The reference topology is the TMI7003C with outputs of 3.3 V for general use, 3.3 V for VCCIO0/1/2 and 1.8 V for VCCIO3, plus the ME6211C12 for the 1.2 V core. **These are starting components, not an approved final selection.** Recalculate loads, losses and thermals for the FT2232H and the HAT.

Include all additional domains required by the FT2232H and the other components, without deducing them only from the FPGA rails. Sequencing, ramps, reset and decoupling must follow the manufacturers.

Provide a test point for GND and each rail, a power LED and means to measure consumption during bring-up.

### 8.3 J21 and independent power-up

| ID | Requirement |
|---|---|
| ISO-01 | Do not connect the USB-C 5 V directly to the J21 5 V. Since rev. 0.6 (Proposed), the two meet only through the D3/D4 Schottky OR-ing on +5V (PWR-01), so neither feeds the other. |
| ISO-02 | Do not interconnect the 3.3 V outputs of the HAT and KR260 regulators. |
| ISO-03 | Properly connect all applicable GND contacts to the ground plane; separate supplies do not mean galvanic isolation. |
| ISO-04 | Prevent back-powering through GPIOs, protection diodes, translators, JTAG or auxiliary circuits. |
| ISO-05 | Provide a bus enable with a hardware safe state, including before both FPGAs are configured. |
| ISO-06 | Evaluate buffers/switches with documented partial-power-down/Ioff behavior or an equivalent solution. Include the delay and skew they introduce in the timing. |
| ISO-07 | Do not consider only “high-impedance outputs in the firmware” as sufficient protection for a powered-off board. |
| ISO-08 | Keep reset/OE/pulls safe in all power-on/power-off sequences and on loss of clock. |
| ISO-09 | **Proposed**, based on F2 and F4. The HAT does not drive any J21 line before the KR260 asserts `LINK_EN`. The carrier only supplies the PL VCCO rails after the SOM asserts VCCOEN_PS_M2C and VCCOEN_PL_M2C (F2, UG1092). In an HD bank, the absolute maximum input voltage ranges from −0.55 V to VCCO + 0.55 V (F4, DS925); with VCCO off, any 3.3 V coming from the HAT violates this limit. |
| ISO-10 | **Proposed**; rails identified in revision 0.5 (F12). RPI_3V3 (contacts 1 and 17) is PL_3V3 through an STMPS2161 current-limited switch (U74; EN tied to GND through R332, 10.0k; FLT_B only pulled up), and VCCO_HDC (bank 44) and VCCO_HDB (bank 43) are tied to PL_3V3, which is enabled by VCCOEN_PL_M2C (F12, sheet 5). The J21 3.3 V can therefore only be present when the bank 43/44 VCCO rail is; it can drop alone on a switch fault, but not the reverse. The design still uses `LINK_EN` as the condition for the HAT to transmit (ISO-11); using the J21 3.3 V as an additional gate is a possible option, not implemented. |
| ISO-11 | **Proposed.** `LINK_EN` controls in hardware the OE of the HAT output buffers, with a disabled default state. |
| ISO-12 | **Proposed.** Pull-downs on the J21 side of the HAT on `LINK_EN`, `LINK_RESET_N` and `LINK_READY`, and weak pull-downs on `LINK_VALID` and `LINK_CLK`. Size them against the K26 internal pull-up of up to 190 µA (F4: 75 to 190 µA with VCCO = 3.3 V): R ≤ receiver VIL / 190 µA; for example, a VIL of 0.8 V gives up to about 4.2 kΩ. A floating or pulled-down pin always means “do not transmit”. **Pending:** resistor values, VIL of the chosen receiver and whether the sizing rule also applies to the weak pull-downs on `LINK_VALID` and `LINK_CLK`. |
| ISO-13 | **Proposed.** Every KR260 → HAT line (`LINK_EN`, `LINK_RESET_N`, `LINK_READY`) enters through a receiver with Ioff, with no back-powering when the HAT is off. |
| ISO-14 | **Pending.** State of PUDC_B on the K26, which defines the pull-ups during configuration, to be confirmed in DS987. It is not given in the carrier schematic (F12) or the K26 SOM XDC (F13), which only lists the net FPGA_PUDC_B on package pin U7. Until it is confirmed, the sizing of ISO-12 considers the internal pull-up active. |
| ISO-15 | **Proposed** (rev. 0.4). Joint enabling of the drivers: `LINK_OE_N` = NAND(received `LINK_EN`, `LINK_TX_EN` from the Gowin), through an SN74LVC1G00 with Ioff. During configuration, the Gowin GPIOs are in high impedance with a weak pull-up of 30 to 150 µA (DS117E); that is why `LINK_TX_EN` has a 4.7k pull-down (0.8 V / 150 µA ≈ 5.3 kΩ). `LINK_OE_N` has a 10k pull-up, which keeps the SN74LVC244A in high impedance at power-up, as recommended by the TI datasheet. The drivers only turn on with the KR260 and the Gowin in agreement. |

UG1092 states that J21 is supplied with 3.3 V and 5.0 V, with a limit of 1.0 A per rail (F1). On the carrier, RPI_3V3 comes from PL_3V3 and RPI_5V0 from 5V0_IN, each through an STMPS2161 switch (U74 and U73, F12, sheet 12). Since rev. 0.6, the 5 V contacts 2 and 4 power the HAT through D4 (PWR-01); the 3.3 V contacts 1 and 17 stay without a power connection on the HAT, and all GNDs go to the plane (section 7.3). Being powered from J21 does not mean that the KR260 PL is ready: the HAT only transmits after `LINK_EN` (ISO-09 to ISO-11). If it is necessary to detect the presence of KR260 power, design this sensing specifically, without creating an interconnection of supplies. This sensing does not replace `LINK_EN` (ISO-10).

**`LINK_EN` conditions:** since `LINK_EN` is in bank 44, the high level can only come from the configured PL with that bank powered. This holds provided that the ISO-12 pull-down overcomes the internal pull-up during configuration (ISO-14) and that the path on the carrier does not force a high level on this net; the carrier schematic shows contact 31 going straight to the SOM connector, with no pull-up (F12). `LINK_EN` does not indicate the state of the bank 43 VCCO by itself; in the carrier schematic, banks 43 and 44 share the PL_3V3 rail (F12, ISO-10). In the proposal no HAT → KR260 line is in that bank, and any future use of the bank 43 reserves in that direction requires revising ISO-09.

Do not advertise hot-plug: insert or remove the HAT with both boards powered off until a hot-plug solution is explicitly designed and validated.

## 9. USB, JTAG, UART and recovery

The proposed baseline replaces the BL702 with the **FT2232H**, preserving the programming and UART functionalities, not the complete electrical identity of the original board.

| ID | Requirement |
|---|---|
| USB-01 | Channel A for JTAG/MPSSE; validate ADBUS0–3 as TCK/TDI/TDO/TMS in the component, in the schematic and in the programmer configuration. |
| USB-02 | Channel B for UART; keep the original signals on FPGA pins 17/18 with verified directions. |
| USB-03 | Provide the 12 MHz reference, reset, decoupling and EEPROM according to the FT2232H datasheet. The 93LC56 is a candidate from the base draft, not a frozen BOM. |
| USB-04 | Design the JTAG 3.3 V ↔ 1.8 V level conversion with correct directions and validated thresholds and timing. |
| USB-05 | Do not use only resistive dividers as a generic substitute for the translator: TDO returns from the 1.8 V bank and needs to satisfy the receiver. |
| USB-06 | Provide an external JTAG connector/points with GND and a 1.8 V reference for recovery. Avoid contention between an external programmer and the FT2232H. |
| USB-07 | Validate USB and programming with the KR260 present, absent, powered on and powered off, without back-powering; since rev. 0.6, also with the HAT powered from J21 only, from the USB-C only and from both (HW-09). |

**Rev. 0.4 (Proposed):** the FT2232H circuit (FT2232HL, LQFP-64) follows figure 6.1 of the FT_000061 v2.10 datasheet:

- 12 MHz ±30 ppm crystal with 27 pF;
- REF with 12 kΩ 1 %, RESET# tied to 3.3 V through 1 kΩ and TEST to GND;
- VPHY and VPLL with ferrite, 4.7 µF and 100 nF; VREGOUT with 3.3 µF; 100 nF on each VCORE and VCCIO;
- 93LC56B EEPROM with 10k pull-ups on EECS, EECLK and DO and 2.2k between DO and EEDATA.

USB-04 uses an SN74AVC4T774 (TSSOP-16): TCK, TDI and TMS from 3.3 V to 1.8 V and TDO from 1.8 V to 3.3 V, with fixed direction per bit, Ioff and VCC isolation (TI SCES693I). Its OE̅ has a 10k pull-down, so that it stays enabled without depending on an extra GPIO in the openFPGALoader profile, and a solder jumper (JP90) that takes it to 3.3 V to isolate the FT2232H when there is an external programmer. TI recommends a pull-up on OE̅ to guarantee high impedance at power-up; this change is **Pending** a decision. The J90 header (1×6 on the 1.8 V side: VREF, TMS, TCK, TDO, TDI and GND) meets USB-06. The UART keeps the 22R of the reference.

**Rev. 0.6 (Proposed):** since the HAT can run from J21 without a USB host (PWR-01), the FT2232H is self-powered. PWRSAV# (BCBUS7, pin 59) gets VBUS through 4.7k (R10) with 10k to GND (R11), as in table 3.3 and section 6.2 of FT_000061 v2.10: with no host, PWRSAV# is low and the FT2232H is held in suspend, without driving the USB lines. FTDI asks for the EEPROM to be configured for self-powered operation with the option “suspend on DBUS7 low” selected in FT_PROG, and for this configuration assumes BCBUS7 is not used by MPSSE; channel B is the UART here (USB-02). These settings belong to the EEPROM programming procedure (section 16) and are checked at bring-up (USB-07, HW-09).

The draft cites VID:PID `0403:6010` and the `ft2232` cable selection. **This alone does not prove compatibility with `-b tangnano9k`**: USB interface, JTAG connections, reset control and board profile must also match.

Compatibility objective to be validated:

```sh
openFPGALoader -b tangnano9k firmware.fs
```

The command above is not an already approved test, nor does it by itself define the persistent programming of the Flash. Document validated commands for volatile loading, Flash programming and recovery. If a custom profile is needed, version it and record the difference relative to the original Tang.

## 10. Parallel link protocol

### 10.1 Bandwidth and objectives

The initial proposal is a **16-bit SDR** link, with one word per valid cycle, a clock forwarded by the transmitter and a hardware receiver in the KR260 PL.

| Configuration | Calculated raw rate | Role in the project |
|---|---:|---|
| 16 bits × 50 MHz | 100 MB/s = 800 Mbit/s | Initial engineering target |
| 16 bits × 100 MHz | 200 MB/s = 1600 Mbit/s | Later investigation, with no guarantee (see TIM-14) |

`MB/s` uses decimal units. The useful rate depends on valid cycles, flow control, framing, integrity checking and the capacity of the consumer. Do not present the raw rate as the rate for the Linux application.

The highest possible frequency of this set is not defined. Finding it requires timing closure and physical testing, not just increasing a clock parameter.

### 10.2 Mandatory specification before the final RTL

Document in `docs/link-protocol.md`:

| ID | Content |
|---|---|
| LINK-01 | Clock source, supported frequencies and launch/capture edges. |
| LINK-02 | Bit order, byte order, word format, framing and meaning of the controls. |
| LINK-03 | Exact acceptance rule for a word; no implicit meaning for VALID/READY. |
| LINK-04 | Maximum reaction latency to flow control and maximum number of words in flight. |
| LINK-05 | FIFO depth and almost-full threshold derived from the worst-case backpressure. |
| LINK-06 | Detection of data loss, duplication and corruption; define sequencing and CRC/parity if adopted. |
| LINK-07 | Reset, training/alignment if needed, idle state, loss of clock and recovery. |
| LINK-08 | Rule for stopping the transmitter before the receiver loses the capacity to receive. |
| LINK-09 | Logging of overflow/underflow and persistent errors; no silent discard. |
| LINK-10 | **Proposed.** Semantics of `LINK_EN` (KR260 → HAT, quasi-static). High level: the KR260 allows the HAT to enable the drivers, with bank 44 powered and the PL configured (section 8.3). Low level or floating pin: do not transmit, with the OE of the HAT buffers disabled in hardware (ISO-11). Define who drives `LINK_EN` in the PL, when it rises and how it relates to `LINK_RESET_N` and to the handshake. Since the high level does not identify the loaded bitstream, no other PL design may drive pin 31 high (J21-06). |
| LINK-11 | **Proposed.** A PL reload is a normal operating event: the fall of `LINK_EN` interrupts the TX, the affected words are discarded and counted, without silent discard (LINK-09), and the link requires a new handshake before transmitting again. |

**READY physically crosses the link in the return direction.** Do not treat it automatically as a same-cycle AXI handshake. Choose and specify a timed return mechanism, credits or early backpressure; the FIFO must absorb the words that will still arrive after the change of state.

In the Kria execution model (section 14.3), the PL can be reloaded with the HAT powered on and transmitting. LINK-11 treats this reload as an expected event, not as a failure.

### 10.3 Direction and duplex

The main **HAT → KR260** flow is only the initial proposal. Confirm whether the return is only control, occasional commands or continuous data.

The presence of `READY` does not make the bus full-duplex. If a shared data bus is required, define half-duplex, turnaround, driver enabling and arbitration. Do not assume two independent 16-bit buses on the same header without a new pin budget.

A requirement for simultaneous full-duplex must go through a width/direction review before freezing the schematic.

### 10.4 Latency

The original draft reported **75–88 ns in GHDL simulation** for `link_tx.vhd`, `link_rx.vhd` and `tb_link.vhd`, in a different 8-bit/Pmod arrangement. This result is historical and **does not validate the 16-bit HAT**, nor does it automatically include FIFO, DMA, DDR or Linux.

Define and measure separately the latency from pins to receiver, from producer to consumer in the PL, and up to the application. There is no approved numerical limit for the latency of this version.

## 11. Clocks, CDC and timing closure

**TIM-01:** prove the complete path `Gowin pin -> HAT PCB -> header -> KR260 carrier -> SOM -> K26 pin`, including intermediate components and clock resources.

**TIM-02:** implement a minimal I/O proof on both FPGAs before freezing the pinout, with the tool and version actually used to produce the bitstreams.

**TIM-03:** generate the 50 MHz clock from the 27 MHz reference only through a supported and verified resource/strategy; confirm the actual frequency, lock, jitter and the link release sequence. Do not assume this frequency through simple integer division.

**TIM-04:** choose the capture phase/edge with margin. Sampling data on the same edge on which they change, without an explicit delay budget, is not an approved solution.

**TIM-05:** in Vivado, define input/generated clocks according to the architecture, I/O standards and minimum/maximum input and output delays. Include the return paths of the controls.

**TIM-06:** in the Gowin/open flow, version the `.cst` physical constraints and the timing constraints actually supported by the chosen tool. A pin-location `.cst` does not prove setup/hold closure.

**TIM-07:** document transmitter Tco, flight/skew, isolator delays, jitter, receiver setup/hold, variations and margin. Consider the path on both boards, not only lengths on the HAT.

**TIM-08:** use an asynchronous FIFO or a verified equivalent mechanism to cross from the link domain to AXI/application. Do not synchronize each bit of the bus independently as if that preserved the word.

**TIM-09:** specify synchronization of the controls and reset deassertion per domain. Handle loss of clock and independent restart.

**TIM-10:** require post-place-and-route reports without violations on the relevant paths. Do not use false paths, multicycle or relaxed clock routing to hide a functional path without a reviewed justification.

**TIM-11 (new):** **Pending** (choice of strategy). Per F5, F6 and F8, and per S4 (preliminary — confirm in UG571), the receive clock on the K26 goes through a BUFGCE without compensation of the insertion delay and without per-bit fine phase adjustment. HDGC has direct access only to the global clock buffers (F5); HD banks have no adjacent CMT, and an MMCM fed by a BUFGCE does not compensate the delay of that path (F6); the HD I/O logic has no dedicated phase-alignment circuit, and the register clock goes through the global network (F8); S4 indicates that HD banks have no IDELAY. The capture strategy needs to be chosen and documented explicitly before the final RX RTL.

**TIM-12 (new):** **Proposed.** The Tang forwards `LINK_CLK` via ODDR with inverted phase, so that the edge falls in the middle of the eye. Vivado verifies the capture with source-synchronous constraints: input clock defined on the `LINK_CLK` pin (TIM-05) and `set_input_delay` relative to the forwarded clock, including the uncompensated insertion delay (TIM-11). Confirm support for the ODDR primitive in the Gowin flow (GW-02).

**TIM-13 (new):** **Proposed alternative.** HDGC → BUFGCE → MMCM with dynamic phase shift, accounting for the additional jitter in the TIM-07 budget. The MMCM does not compensate the delay of the path through the BUFGCE (F6); the phase adjustment procedure goes into LINK-07.

**TIM-14 (new):** record in `docs/timing-budget.md` that the restrictions of TIM-11 are the limiting factor for 100 MHz SDR or DDR. HD I/O has IDDRE1/ODDRE1 (F8), so the architecture does not exclude DDR, but 100 MHz remains exploratory because:

- the clock insertion delay through the global network is not compensated (F6) and goes entirely into the budget;
- without a dedicated phase-alignment circuit (F8) and, according to S4, without IDELAY, there is no bit-by-bit capture adjustment to absorb skew;
- doubling the rate per line, with 100 MHz SDR or with DDR, halves the window of each bit relative to the 50 MHz SDR target, but the uncompensated delays, the skew of the complete path (TIM-01) and the delays of the isolation buffers (ISO-06) do not shrink along with it.

Only timing reports without violations (TIM-10) and prototype testing can take 100 MHz out of the exploratory state.

If the chosen tool does not allow proving the necessary constraints, record the limitation and revise the flow before announcing validated timing.

## 12. PCB and signal integrity

### 12.1 Stack-up and impedance

The four-layer proposal starts from:

| Layer | Initial use |
|---|---|
| L1 | Components and critical signals |
| L2 | Continuous GND |
| L3 | Power distribution |
| L4 | Signals compatible with the available reference |

This stack-up is a proposal; it does not authorize critical signals on L4 over power splits. Prioritize routing the link over continuous GND or revise the stack-up to keep an adequate return path.

| Interface | Initial target |
|---|---|
| Routed segments of the parallel link | 50 Ω single-ended |
| USB 2.0 | 90 Ω differential |

The targets do not prove uniform impedance in the header/carrier. Obtain the manufacturer's stack-up and calculate the geometry from it; do not fix the trace width without the actual construction. In revision 0.5, the board carries the JLCPCB JLC04161H-7628 stack-up (Proposed, to be confirmed when ordering), and the USB pair geometry was calculated from it, not measured (section 17.2).

### 12.2 Implementation rules

| ID | Requirement |
|---|---|
| PCB-01 | Place the FPGA, header and interface elements so as to minimize the link path and maintain the GND return. |
| PCB-02 | Priority routing for the clock, with data/controls compatible with the skew budget. |
| PCB-03 | Define the length tolerance from the total timing. The previous ±10 mm value of the Pmod link is not an automatically approved criterion for the HAT. |
| PCB-04 | Provide footprints for series resistors close to the drivers. 0 Ω and 22–33 Ω are test candidates, not guaranteed final values. |
| PCB-05 | Check the terminations already present on the KR260 before adding new ones. Do not automatically copy the 20 Ω + 33 pF RC used in the Pmod context. |
| PCB-06 | Select ESD protections with capacitance, trigger voltage and powered-off behavior compatible with the interfaces. |
| PCB-07 | Minimize stubs and layer transitions; provide a ground return at the necessary transitions. |
| PCB-08 | Place decoupling on the correct pins/domains, with adequate vias and return loops. |
| PCB-09 | Treat USB as a differential pair and keep the protection close to the receptacle. |
| PCB-10 | Validate the QN88P footprint, exposed pad when applicable, paste and assembly recommendations against the manufacturer's drawing. |
| PCB-11 | Include fiducials, accessible test points, silkscreen and markings of unpopulated components. |
| PCB-12 | Define electrical and mechanical rules in KiCad; record justified exceptions instead of suppressing errors indiscriminately. |
| PCB-13 | **Proposed.** The header has only 8 GNDs (6, 9, 14, 20, 25, 30, 34 and 39, according to S3, preliminary — confirm in XTP743) for up to 28 signals (S1), so the allocation must follow adjacency to GND: clock between GNDs, quasi-static signal opposite the clock and high-activity bits off the clock diagonals (section 7.3). |
| PCB-14 | **Validation requirement.** Before manufacturing, simulate signal integrity with IBIS models: K26 side generated with `write_ibis` in Vivado and GW1NR-9 IBIS obtained from Gowin. Include the models of the chosen isolation buffers and receivers (ISO-06, ISO-11, ISO-13). |
| PCB-15 | **Proposed.** Extract from XTP756 the carrier lengths and stack-up, from J21 to the SOM connector, for TIM-07 and PCB-14. The segment from the SOM connector to the K26 pin is outside PCB-15; the source of these delays is **Pending**. |

Investigate overshoot, undershoot, ringing, crosstalk and simultaneous switching of outputs on the prototype. Choose drive/slew based on the results, not always at the maximum value.

## 13. Gowin firmware

| ID | Requirement |
|---|---|
| GW-01 | Versioned HDL project, initially VHDL, with separation between peripherals, link and application. |
| GW-02 | Preserve GHDL -> Yosys -> nextpnr-himbaechel -> gowin_pack -> openFPGALoader as the objective of the existing flow, validating support for the primitives used. |
| GW-03 | Version the `.cst`, clock configurations, supported timing constraints and tool versions. |
| GW-04 | Implement a registered TX, FIFO, flow control, counters and link restart. |
| GW-05 | Provide firmware for blink, UART, Flash, PSRAM, microSD and bus test patterns. |
| GW-06 | Maintain safe behavior when the KR260 is absent or powered off; electrical safety must also exist in the hardware. |
| GW-07 | Expose version/protocol identification and counters to relate each test to the bitstream used. |

Publish reproducible targets for simulation, build, loading and testing. The target names in the repository are part of the implementation; do not present commands as existing before creating them.

## 14. KR260 logic and software

### 14.1 Programmable logic

Implement a registered parallel RX in the link clock domain, error detection, a domain-crossing FIFO and an AXI-Stream interface. Provide AXI-Lite registers for control, identification and statistics.

Capture must take place in hardware in the PL. Do not use GPIO polling by Linux as the receive solution for the main stream.

AXI DMA to DDR is the proposal for reading by the software. Size the complete chain for the link rate, including AXI clock/width, queues and backpressure. If the application consumes the stream directly in the PL, document that separate path.

Reserve instrumentation resources for debugging and deliver utilization and timing reports of the integration with the actual KR260 design, not just of an isolated example.

### 14.2 Software, when there is DDR/Linux access

Define the control interface, driver or access mechanism, device tree/overlay when needed, DMA buffer management and cache coherency. Version the integration with the Linux/PetaLinux environment used in the project (baseline proposed in KRIA-05).

The software must report received bytes, errors, FIFO/link states and test results. Measure separately the rate at the interface, at the DDR and at the application. Do not make the correctness of the link depend on the scheduling latency of a Linux thread.

The parallel interface of this HAT is custom for the KR260 PL; it is not a standard Raspberry Pi peripheral that Linux will recognize automatically.

### 14.3 Kria execution model

System context (R4): the KR260 PL already runs the DPU (DPUCZDX8G) and the VCU; the operating system is KAKUEI-OS, a customized PetaLinux 2024.2; the tools are Vivado/Vitis 2024.2; and the applications run in Docker containers, such as stream-edge.

According to the Kria dfx-mgr/xmutil documentation (F9), each PL application is located in `/lib/firmware/xilinx/<app>`, with `.bit.bin`, `.dtbo` and `shell.json` (plus `.xclbin` in the Vitis/XRT flow), and in the standard Kria images the PL is loaded after Linux.

| ID | Requirement |
|---|---|
| KRIA-01 | **Proposed.** Load the PL containing the RX through dfx-mgr/xmutil or fpga-manager (F9), with the application package in `/lib/firmware/xilinx/<app>`. The choice of mechanism in KAKUEI-OS is **Pending**. While the application is not loaded, `LINK_EN` must remain low (ISO-12, section 8.3), and the HAT does not transmit (ISO-09). |
| KRIA-02 | **Proposed.** The RX goes into the same bitstream as the DPU and the VCU, with a documented budget of resources, clocks, HP/HPC ports and DDR bandwidth, and with reports of the integrated design (section 14.1). |
| KRIA-03 | **Proposed.** PL reloads are treated as a normal event (LINK-11). |
| KRIA-04 | **Proposed.** If the consumer runs in a container, provide for access to the DMA device inside Docker. |
| KRIA-05 | **Proposed.** Fix the KAKUEI-OS/PetaLinux 2024.2 and Vivado 2024.2 baseline for the link bitstreams, constraints and software (TIM-02, section 14.2). |

## 15. Tests and acceptance criteria

### 15.1 Before manufacturing the first prototype

| ID | Verification | Required evidence |
|---|---|---|
| PRE-01 | Complete pinout of the 40 contacts, including power and reserved ones | Table with sources and independent review |
| PRE-02 | Clock path and I/Os of both FPGAs | Constraints and minimal implementation proof |
| PRE-03 | Timing of the 50 MHz target | Reviewed reports and setup/hold budget |
| PRE-04 | Voltage domains and powered-off states | Review of datasheets and isolation circuit |
| PRE-05 | USB/regulator/thermal budget | Spreadsheet or calculation document |
| PRE-06 | Fit on the KR260 | Model/drawing with clearances and accessibility |
| PRE-07 | ERC/DRC and footprint/pinout | Reports without unresolved errors; approved exceptions |
| PRE-08 | Availability and assembly | Reviewed BOM, alternatives and validation by the assembler |
| PRE-09 | Signal integrity in the link path (PCB-14) | IBIS simulation report with identified models and revisions |

**Do not issue a statement of validated 100 MHz just because 50 MHz closes timing.**

### 15.2 Electrical and functional bring-up

First perform inspection and continuity/short tests with everything powered off. Power up the HAT separately from the KR260 using a procedure with limited current and safe states; provide in the hardware the means needed to control the stages. Measure the rails before enabling the link, without assuming that it is possible to switch off each load individually if this was not designed in.

| ID | Test | Criterion |
|---|---|---|
| HW-01 | Voltages, ripple and sequence | Within the applicable limits at idle and under load |
| HW-02 | HAT on, KR260 off | No back-powering or improper voltages |
| HW-03 | KR260 on, HAT off | Same protection criterion. Since rev. 0.6, an installed HAT is powered from the J21 5 V whenever that rail is on; check this case at the power-up and power-down transitions of the KR260 rails |
| HW-04 | Both on, reset/reconfiguration on either side | Link in a safe state and defined recovery |
| HW-05 | JTAG and Flash | Volatile and persistent programming and recovery documented |
| HW-06 | LEDs, buttons, UART and clock | All preserved functions verified |
| HW-07 | PSRAM and microSD | Integrity test and planned operations without errors |
| HW-08 | Signal integrity | Clock/data captures and measurements compatible with the component limits |
| HW-09 | Power sources (PWR-01, rev. 0.6) | J21 only, USB-C only and both: +5V within the TMI7003C input range under load, no back-feed into the source that is off (USB VBUS and J21 5 V measured), FT2232H suspended without a USB host and enumerating when one is connected |

### 15.3 Link and performance

Start at a reduced frequency and progress up to 50 MHz. Evaluate higher frequencies only after reviewing timing, signals, power and temperature.

Use counter/sequence, zeros/ones, walking-one/walking-zero and a pseudorandom pattern according to the test plan. Define a checker that also detects losses/duplications; a match of a short counter that has wrapped around must not mask lost words.

Exercise prolonged backpressure, pauses, FIFO near the limit, reset and recovery. Verify the absence of silent discards and the operation of the error counters, including by deliberate fault injection in testing.

**Proposed stability test:** at least 24 hours at 50 MHz in the target configuration, with zero integrity errors and zero unexpected losses/duplications. Record the bytes actually accepted, link occupancy, resets, load and temperatures; “24 hours powered on” without traffic does not satisfy the test.

The report must separate nominal raw rate, sustained payload and latency, with the measurement conditions. The numerical sustained-payload target and the environmental qualification range still need to be defined. Zero errors observed in a test is not equivalent to an absolute guarantee under any condition.

## 16. Manufacturing, assembly and BOM

Use components with a clearly identified manufacturer, part number and package. Confirm stock, life cycle and alternatives at the time of approving the BOM; this README does not declare the current availability of any part.

Substitutions must preserve the applicable function, voltage, timing, footprint and firmware, or go through review. Do not substitute the FPGA/family without formally changing the scope.

Document the assembly orientation, DNP components, adjustable termination resistors, jumpers, initial EEPROM firmware and the batch programming procedure. Since rev. 0.6, the FT2232H EEPROM settings include self-powered operation and “suspend on DBUS7 low” (section 9).

JLCPCB is the Proposed manufacturer and assembler: revision 0.5 prepared the board and its production files for a JLCPCB order (section 17.2), without releasing them. Initial quantity, target cost and operating temperature range remain pending. Prototype release and production release must be separate steps.

**JLCPCB BOM (rev. 0.5, updated in rev. 0.6, Proposed):** `hardware/production/make_jlcpcb.py` generates the Gerber/drill, BOM and CPL files in `hardware/production/jlcpcb/` from the KiCad project and `hardware/production/jlcpcb_parts.csv` (value and footprint → LCSC number, manufacturer, MPN, note). The BOM has 48 lines for 167 placed parts (the test points and the JP90 solder jumper are PCB features without a part), and 16 lines are JLCPCB basic parts; rev. 0.6 added the B5819W line (D3, D4) and C14, R10 and R11 to existing lines (rev. 0.5: 47 lines, 162 parts). The part data comes from a snapshot of the JLCPCB catalog (cdfer jlcpcb-parts-database, in-stock subset) read on 2026-10-21; stock changes, and this README still does not declare the availability of any part. The GW1NR-LV9QN88PC6/I5 and the TMI7003C are not in that snapshot and need JLCPCB Global Sourcing or consignment. The logic ICs are pinned to Texas Instruments parts, because ISO-06 and ISO-13 rely on their Ioff. Order settings, assembly notes and the open items of the order are in `hardware/production/README.md`.

### 16.1 Proposed parts (rev. 0.4, updated in rev. 0.5 and 0.6)

**Proposed.** Choices made during the capture of the preliminary schematic; in revision 0.5, the Flash was replaced and JLCPCB part numbers were taken from the catalog snapshot (section 16). No part in this table has had its stock, life cycle or price verified.

| Function | Proposed part | Reference | Basis for the choice |
|---|---|---|---|
| FPGA | GW1NR-LV9QN88PC6/I5; custom footprint `GW1NR_QN88P_10x10mm_P0.4mm_EP6.8mm`, with 0.20 × 0.85 mm pads, centers at 9.90 mm and a 6.8 mm EP, according to the recommended layout of figure 4-2 of UG119E. Replaces the KiCad `ArtInChip_QFN-88-1EP` (0.30 mm pads, which left 0.10 mm between pads) | U4 | SYS-04 (Decided); EP checked in UG119E, figure 4-1, and the layout of figure 4-2 applied; the 16 thermal vias of 0.3 mm in the EP and the paste in 3 × 3 windows are Proposed (PCB-10) |
| Triple buck | TMI7003C; 3 × 2.2 µH in 2016 (Murata DFE201610E-2R2M); 680k/150k (3.3 V) and 300k/150k (1.8 V) dividers with 18 pF; 10, 10 and 22 µF output and 22 µF per input | U2, L1–L3 | Values from the 3674; symbol pinout read from the 3674 (TMI datasheet not consulted); inductor current to be sized (PWR-04) |
| 1.2 V LDO | ME6211C12M5 with 10 µF and 2.2 µF | U3 | 3674 |
| Ferrites | UPZ1005D121-1R3TF | FB1–FB4, FB30, FB90, FB91 | 3674; the use on VPHY/VPLL of the FT2232H is our own choice, because FTDI does not specify the value |
| USB input protection | 0.5 A 1206 PTC, nSMD050-33V in the JLCPCB BOM (to be sized, PWR-04), SMAJ5.0A TVS and USBLC6-2SC6 on D+/D− | F1, D1, U1 | PWR-03 and PCB-06; the USBLC6-2SC6 has low capacitance for USB 2.0 HS. SMAJ5.0A polarity to be checked on the footprint |
| Power OR-ing (rev. 0.6) | 2 × B5819W Schottky in SOD-123 (CJ B5819W SL, JLCPCB C8598, basic part; 40 V, 1 A and 600 mV at 1 A in the catalog) and a 10 µF 0603 capacitor on the J21 input | D3, D4, C14 | PWR-01; the drop lowers +5V, TMI7003C input range Pending (PWR-04) |
| USB bridge | FT2232HL (LQFP-64), 12 MHz ±30 ppm crystal in 3225, 93LC56B in SOIC-8 and, from rev. 0.6, the 4.7k/10k PWRSAV# divider | U90, Y90, U91, R10, R11 | SYS-11 and USB-03; FT_000061 v2.10, figures 6.1, 6.3 and 6.5 and table 3.3 |
| JTAG translator | SN74AVC4T774PWR (TI, JLCPCB C129363) | U92 | USB-04, USB-05 and USB-07 (section 9) |
| Link drivers | 3 × SN74LVC244APWR (TI, JLCPCB C7668) in TSSOP-20 | U130–U132 | ISO-06 and ISO-11; Ioff in the TI datasheet |
| Link receivers | SN74LVC3G17DCUR (TI, JLCPCB C68245) in VSSOP-8 | U133 | ISO-13; Schmitt with Ioff |
| Enable | SN74LVC1G00DBVR (TI, JLCPCB C7826) in SOT-23-5 | U134 | ISO-15 |
| Link series resistors | 18 × 22R in 0402 | R130–R147 | PCB-04 (22–33 Ω range) |
| ISO-12 pull-downs | 3.3k on EN, READY and RESET_N; 100k on VALID and CLK | R150–R154 | 3.3k meets R ≤ 4.2 kΩ; 100k Pending (ISO-12) |
| 27 MHz oscillator | 4-pin 3225 CMOS oscillator with EN (Abracon ASE footprint) and 22R in series | Y1, R35 | 3674 (U16 is an oscillator, not a crystal: FPGA-04); part number Pending |
| Flash | Winbond W25Q32JVZPIQ (JLCPCB C571260) in WSON-8 6 × 5 mm, 3.3 V on VCCO0_1_2_3V3, 4.7k pull-ups on WP̅ and HOLD̅/RESET̅ | U5 | Replaces the PUYA P25Q32U of the 3674 in rev. 0.5 (not stocked at JLCPCB; its datasheet was still Pending); the symbol already had the pinout of KiCad's Memory_Flash:W25Q32JVZP, so the footprint and connections are unchanged. MSPI/boot compatibility with the GW1NR-9 **Pending** |
| microSD | Molex 104031-0811 | J2 | Footprint available in KiCad; the 3674 uses Sipeed's own connector |
| J21 header | CONNFLY `DS1023-2*20SF11`, 2.54 mm 2 × 20 female header, 8.5 mm high, THT on the bottom side | J130 | MEC-01; 8.5 mm height **Proposed**: with the XTP744 model (F14), the HAT bottom is about 10.9 mm above the carrier, with 11 mm M2.5 standoffs (section 4); physical fit check pending (MEC-04) |
| External JTAG | 2.54 mm 1 × 6 header PZ254V-11-06P (THT, optional in assembly) and solder jumper | J90, JP90 | USB-06 |
| Buttons | SMD SPST (PTS810 footprint) | SW1, SW2 | The 3674 uses a 3 × 4 mm button; footprint to be confirmed |
| LEDs | 6 orange 0603 LEDs without a resistor, between VCCO3_1V8 and the pins, as on the 3674; orange power LED with 1k | D32–D37, D2, R9 | 3674 and section 8.2 |
| Test points | 1.0 mm pads on +5V, +3V3, VCCO0_1_2_3V3, VCCO3_1V8, +1V2 and GND | TP1–TP6 | Section 8.2 |

## 17. Deliverables

| Group | Deliverable |
|---|---|
| Schematic | Complete hierarchical KiCad 10 project, with power supplies, FPGA, USB/JTAG/UART, memories and J21 |
| Libraries | Required symbols, footprints and models with project-local library tables |
| PCB | Layout, stack-up, rules, target impedances, assembly and 3D model |
| Review | ERC/DRC, pinout, electrical, mechanical, power and timing review |
| Manufacturing | Gerbers, drilling, BOM with MPN, pick-and-place, assembly drawing and DNP list |
| Gowin | RTL, constraints, testbenches, bring-up firmware and reproducible flow |
| KR260 | RTL/IP, XDC constraints, Vivado integration, registers and test/DMA software when applicable |
| Documentation | J21/SOM/K26/Gowin map, protocol, timing/power budgets and installation guide |
| Validation | Logs, identified bitstreams, captures, throughput/latency results and long-duration test |

Maintain traceability between PCB revision, BOM, firmware, constraints and results. No Gerber should be treated as approved just because it has been exported.

### 17.1 Preliminary schematic (rev. 0.4, updated in rev. 0.5)

**Proposed, not released.** Captured in KiCad 10.0.7, in `hardware/`:

| File | Content |
|---|---|
| `tangnano9k-kr260-hat.kicad_sch` | Root with the five sheets |
| `schematics/power.kicad_sch` | USB-C, protection, J21 5 V input and Schottky OR-ing (rev. 0.6), TMI7003C, ME6211, power LED and test points |
| `schematics/fpga.kicad_sch` | GW1NR-9, decoupling, MODE and RECONFIG_N, buttons, LEDs and 27 MHz oscillator |
| `schematics/usb_jtag_uart.kicad_sch` | FT2232H, EEPROM, JTAG translator, external JTAG header and UART |
| `schematics/flash_microsd.kicad_sch` | W25Q32JVZPIQ Flash (U5) and microSD |
| `schematics/j21_interface.kicad_sch` | J21, drivers, receivers, enable and pull-downs |
| `symbols/tangnano9k-kr260-hat.kicad_sym` | GW1NR-9 QN88P (UG803E), TMI7003C (pinout from the 3674), SN74AVC4T774PW (TI), 74LVC244A and P25Q32U_WSON8 (pinout of KiCad's W25Q32JVZP, used for U5) |

Gowin pins in the schematic (Proposed; the preserved functions stay on the same pins as in section 5.1):

| Function | GW1NR pins | Bank |
|---|---|---|
| JTAG TMS, TCK, TDI and TDO | 5, 6, 7 and 8 | 3 (1.8 V) |
| RECONFIG_N, MODE1 and MODE0 | 9, 87 and 88 | 3 |
| Buttons S1 and S2 | 3 and 4 | 3 |
| LEDs 1–6 | 10, 11, 13, 14, 15 and 16 | 3 |
| UART TX and RX | 17 and 18 | 2 (3.3 V) |
| microSD SCLK, MOSI, CS and MISO | 36, 37, 38 and 39 | 2 |
| Received `LINK_EN`, `LINK_READY` and `LINK_RESET_N`; `LINK_TX_EN` | 40, 41 and 42; 47 | 2 |
| 27 MHz clock | 52 | 1 (3.3 V) |
| Flash MCLK, MCS_N, MOSI and MISO | 59, 60, 61 and 62 | 1 |
| `LINK_CLK` and `LINK_VALID` | 73 and 74 | 1 |
| `LINK_D0`–`LINK_D15` | 68–72, 75–77, 48–50 and 53–57 | 1 |
| No connection | 19, 20, 25–35, 51, 63 and 79–86 | — |

Pin 51 (pair of the 27 MHz clock on 52) and 63 (PLL input) were left free on purpose.

Checks made in revision 0.4, all of them document checks and not electrical ones:

- KiCad ERC with no violations in the whole hierarchy;
- netlist exported and checked by script against 109 intended connections (link, JTAG, UART, USB, Flash, TF and power), with no discrepancies; the 76 single-node nets correspond to the pins marked as no connection;
- the 21 J21 → Gowin paths of the netlist match `docs/pinout-j21.csv`;
- after the redraw of the sheets: the same 169 parts, with identical value, footprint and fields, and the same 209 nets, each with the same nodes as in the initial capture, checked by script; the 109 intended connections checked again through the nodes; ERC with no violations.

The redraw organizes each sheet into functional blocks: wires within each block, power symbols on the rails and global labels only on the signals that change sheet. The custom symbols of the TMI7003C and the P25Q32U got a taller body so that the pin names do not overlap; pin numbers and functions did not change.

**Revision 0.5:** all KiCad texts are in English (schematic notes, title blocks, a custom field renamed to "Note", values, symbol and footprint descriptions, silkscreen), and the schematic PDF is `hardware/tangnano9k-kr260-hat_schematic_rev0.4.pdf`. U5 is now the W25Q32JVZPIQ (section 16.1), still drawn with the project symbol `P25Q32U_WSON8`. KiCad ERC: 0 errors and 0 warnings; the netlist is unchanged (209 nets, 169 parts). These are document checks, not electrical validation.

**Revision 0.6:** the power sheet gets D3, D4 and C14 and the nets `VBUS_F` and `J21_5V`, and `VBUS` becomes a global net, because it also reaches the FT2232H sheet; the usb_jtag_uart sheet gets the PWRSAV# divider R10/R11 (`FT_PWRSAV_N`); on the J21 sheet, contacts 2 and 4 go to `J21_5V`. The three sheets were regenerated with the same script as the redraw. KiCad ERC: 0 errors and 0 warnings. Netlist: 209 nets and 174 parts. Compared by script with rev. 0.5, the only differences are the intended ones (F1 pin 2, J130 pins 2 and 4 and U90 pin 59 change nets, `/power/VBUS` becomes `VBUS`, +5V gains D3/D4 and GND gains C14/R11), and the 123 symbols already present keep their library, UUID and fields. These are document checks, not electrical validation.

Known limitations:

- local nets drawn as a direct wire now have an automatic KiCad name (for example, the outputs of the 244s previously named `B_D0`–`B_D15`); the connectivity is the same;
- Gowin pins 53–57 also carry configuration functions (SSPI/CPU). In the reference they served the RGB LCD, but their use as I/O in the open flow (GW-02) is **Pending**;
- the TMI7003C pinout was read from the 3674 schematic, not from the TMI datasheet;
- apart from the QN88P (section 16.1), no footprint was checked against the manufacturer's drawing; the PCB is prepared for a JLCPCB order but not released (section 17.2), and the stock data of the BOM comes only from a catalog snapshot (section 16).

### 17.2 PCB (rev. 0.5, prepared for JLCPCB; mechanical fit Pending)

**Proposed; prepared for JLCPCB fabrication and assembly, not a release for manufacturing.** Mechanical fit with the KR260: checked against the XTP744 3D model (F14, section 4); physical fit check **Pending**. Files: `hardware/tangnano9k-kr260-hat.kicad_pcb`, JLCPCB design rules in `hardware/tangnano9k-kr260-hat.kicad_dru`, views in `hardware/renders/` (`pcb_top.png`, `pcb_bottom.png`, `pcb_iso.png` and `pcb_iso_bottom.png`), assembled model in `hardware/3d/tangnano9k-kr260-hat_rev0.4.step`, and production files generated for a JLCPCB order in `hardware/production/`, with order settings, assembly notes and open items in `hardware/production/README.md`. The board revision on the silkscreen and in the file names is still 0.4.

| Item | Status (rev. 0.5) |
|---|---|
| Outline and fastening | 65 × 56.5 mm, 3 mm corners and four M2.5 (2.7 mm) holes 3.5 mm from the edges, in the Raspberry Pi HAT form factor. Against the XTP744 3D model (F14), J130 and the holes H1 and H2 land on J21 and its two header-side holes (section 4), so the outline, holes and J21 position are **Proposed** (MEC-03, MEC-10 and MEC-11; Pending in rev. 0.4); H3 and H4 fall outside the carrier, without support (optional feet). The two model holes are matched to MH11 and MH12 of F12 by geometry only (inference). Heights: 8.5 mm socket and 11 mm M2.5 standoffs, with the HAT bottom about 10.9 mm above the carrier (Proposed, MEC-04). The physical fit check on a KR260 is still **Pending** |
| J21 | 2 × 20 female socket J130 on the bottom side (MEC-01), with pin 1 in the inner row, on the left, and the even pins in the edge row. Numbering and mirroring checked against the footprint. With the HAT hanging outward, J130 pin 1 lands on the J21 outer column at the end toward the Pmod connectors (F14, section 4); the model does not mark pin 1, so this orientation rests on S2 and the J21 pin 1 position stays **Pending** until a visual check on a real KR260 (MEC-02). Top-side silkscreen pin labels (rev. 0.5), matching the link signal names of both FPGAs: D0–D15 (`LINK_DATA[15:0]`), CLK, VLD (`LINK_VALID`), RDY (`LINK_READY`), RST (`LINK_RESET_N`) and EN, plus GND, 3V3 and 5V for the KR260 rails (5V, contacts 2 and 4, feeds the HAT through D4 since rev. 0.6; 3V3 not connected) and NC on 3, 5, 18, 22, 27, 28 and 37. Even pins are labelled between the edge row and the board edge, odd pins below the inner row, in 0.9 mm text; the label of each contact is in `docs/pinout.md` |
| Layers | Four (SYS-14, Proposed): F.Cu with parts and signals; In1.Cu GND plane; In2.Cu signals; B.Cu with J21, the decoupling of the GW1NR and the FT2232H, the 1.2 V LDO and signals. GND also on the outer layers, with 166 stitching vias |
| Stackup | JLCPCB JLC04161H-7628, 1.6 mm: 35 µm outer copper, 0.2104 mm 7628 prepreg (εr 4.4), 15.2 µm inner copper, 1.065 mm core (εr 4.6); ENIG finish. Set in the board file; Proposed, to be confirmed when ordering, with impedance control (`hardware/production/README.md`) |
| Rules | 0.15 mm track and 0.13 mm clearance (default); 0.4 mm on +5V, VBUS, switching nodes and raw buck outputs; 0.25 mm on the IC supplies; USB pair as in the next row (0.2 mm in rev. 0.4); 0.45/0.2 mm vias. Revision 0.5 adds the JLCPCB design rules in `hardware/tangnano9k-kr260-hat.kicad_dru` (hole clearances, annular rings, hole-to-hole spacing, drill sizes and silkscreen text, with a 0.9 mm minimum for board text). Rev. 0.6: 0.8 mm on `J21_5V`, 0.6 mm on `VBUS_F` and the new +5V joins, 0.2 mm on the VBUS sense line to R10. The values are still to be confirmed with JLCPCB when ordering (MEC-09, PCB-12) |
| USB pair (PCB-09) | Rerouted in rev. 0.5 on F.Cu over the In1.Cu GND plane, without vias: 0.30 mm traces with a 0.15 mm gap, about 94 Ω differential uncoated and about 91 Ω with solder mask, calculated with the coupled-microstrip equations of KiCad 10 (Kirschning–Jansen) ported to Python, not measured; necked to 0.24/0.15 mm for 3 mm between the USBLC6-2SC6 pin columns. The USBLC6-2SC6 pins 1–6 and 3–4 are internal pass-throughs, declared as jumper pad groups in the footprint instance. D+ has 15.20 mm and D− 14.53 mm of copper, including the joins of the USB-C A and B rows; the J1 → FT2232H trunk is matched within 0.16 mm, and the A/B join stubs add 2.0 to 2.7 mm depending on the plug orientation (about 18 ps). R90 (REF, 12k) moved by 0.3 mm and USB_CC2 rerouted. In rev. 0.4: D+ on F.Cu and D− on In2.Cu with 3 vias, 16.0 and 20.0 mm, without controlled impedance or matching |
| Placement | Link buffers and series resistors right below J21 (PCB-01, PCB-04); FPGA in the center, with the decoupling under it on the bottom side; FT2232H on the left, with the USB-C on the bottom edge and the USBLC6-2SC6 between the two (PCB-09); microSD on the right edge; power in the bottom strip; JTAG header on the right edge; buttons SW1 and SW2 on the left edge, each with the ESD diode and the debounce capacitor next to it and with the pull-up (R33, R34) near the GW1NR. In the XTP744 model (F14), the buttons, USB-C, microSD, JTAG header and test points are all on the part of the HAT that overhangs the carrier edge, so they stay reachable with the HAT installed (geometric statement, MEC-05; Pending in rev. 0.4). Rev. 0.6: D3, D4 and C14 on the bottom side under F1 and the USB-C; R10 and R11 on the top side next to U90 pin 59 |
| Routing | Automatic: GND fanout by script (a via next to each pad, and GND of the GW1NR and the TMI7003C connected to the EP), Freerouting 1.9.0 for the rest and local reroutes by script for `LINK_TX_EN` and for the buttons after they were moved to the edge; in rev. 0.5, the USB pair and USB_CC2 were rerouted (USB row). Rev. 0.6 (dual power), routed by script with an A* router on F.Cu, In2.Cu and B.Cu: `J21_5V` from J130 contacts 2 and 4 down the left edge on In2.Cu to D4 (about 64 mm, 46.5 mm of it on In2.Cu), `VBUS_F` from F1 to D3, the D3/D4 cathodes to +5V, the VBUS sense line to R10 (about 22 mm) and `FT_PWRSAV_N` to U90 pin 59; each power layer change has two 0.45/0.2 mm vias, kept 0.15 mm or more from the pads. Totals in rev. 0.6: 1823 tracks (2.91 m), 442 vias (283 GND, 166 stitching) and 181 footprints (58 on the bottom side); rev. 0.5: 1792 tracks (2.81 m), 432 vias and 176 footprints; rev. 0.4: 1794 tracks (2.82 m) and 435 vias |
| Silkscreen | In English (rev. 0.5); the Portuguese "preliminary / do not manufacture" text was removed. Board label "TANG NANO 9K HAT / for KR260 rev 0.4"; J90 (external JTAG, 1.8 V) pin labels 1V8, TMS, TCK, TDO, TDI and GND plus "JTAG"; test point labels 5V, 3V3, VIO, 1V8, 1V2 and GND; "USB-C 5V"; J21 pin labels as in the J21 row. Board texts at least 1.0 mm high (0.9 mm for the J21 pin labels), designators at least 0.8 mm, all with a 0.15 mm stroke (JLCPCB minimums) |
| KiCad DRC | With the JLCPCB rules and schematic parity (rev. 0.5, repeated in rev. 0.6): 0 errors, 0 unconnected pads, 0 parity issues and 2 warnings, from the silkscreen of the USB-C library footprint crossing the board edge, which the fab is expected to clip (rev. 0.4: 13 silkscreen warnings). These are document checks, not electrical validation |
| Not done | Priority and lengths of the link clock and data (PCB-02, PCB-03, TIM-07): `GW_LINK_CLK` ended up with 39.8 mm between the GW1NR and the buffer. Buck converter loops (PWR-04), signal integrity simulation (PCB-14), test points with the assembler (PCB-11; fiducials FID1–FID3 are on the top side only), the choice between open and filled thermal vias in the U4 exposed pad, human design review, physical fit check on a KR260 (outline, holes, J21 position and heights checked only against the XTP744 model; J21 pin 1 position, MEC-02), TMI7003C datasheet (including its input range with +5V one Schottky drop below the source, rev. 0.6), MSPI/boot compatibility of the W25Q32JVZPIQ with the GW1NR-9, and the values still Pending (ISO-12 100k, PWR-04 PTC and ferrites). The rev. 0.4 USB pair item is now covered by the USB row |
| 3D models | J1, J2, Y1, U2, U5 and the 0402 diodes use models of similar parts (GCT USB4105, Hirose DM3D-SF, 3225 crystal, UQFN-20, WSON-8 with a 3.4 × 4.3 mm EP and 0402 resistor), because the KiCad library does not have the models of the proposed parts. They serve only as illustration |

## 18. Proposed repository structure

```text
tangnano9k-kr260-hat/
|-- README.md
|-- hardware/
|   |-- tangnano9k-kr260-hat.kicad_pro
|   |-- tangnano9k-kr260-hat.kicad_sch
|   |-- tangnano9k-kr260-hat.kicad_pcb
|   |-- tangnano9k-kr260-hat.kicad_dru
|   |-- tangnano9k-kr260-hat_schematic_rev0.4.pdf
|   |-- schematics/
|   |   |-- power.kicad_sch
|   |   |-- fpga.kicad_sch
|   |   |-- usb_jtag_uart.kicad_sch
|   |   |-- flash_microsd.kicad_sch
|   |   `-- j21_interface.kicad_sch
|   |-- symbols/
|   |-- footprints/
|   |-- models/
|   |-- renders/
|   |-- 3d/
|   |-- production/
|   |   |-- README.md
|   |   |-- make_jlcpcb.py
|   |   |-- jlcpcb_parts.csv
|   |   `-- jlcpcb/
|   |-- sym-lib-table
|   `-- fp-lib-table
|-- firmware/
|   |-- gowin/
|   |   |-- rtl/
|   |   |-- constraints/
|   |   |-- testbench/
|   |   `-- Makefile
|   `-- kr260/
|       |-- rtl/
|       |-- constraints/
|       |-- vivado/
|       |-- testbench/
|       `-- software/
|-- docs/
|   |-- reference/
|   |-- pinout.md
|   |-- pinout-j21.csv
|   |-- link-protocol.md
|   |-- timing-budget.md
|   |-- power-budget.md
|   |-- mechanical.md
|   |-- bringup.md
|   `-- decisions.md
|-- tests/
|   |-- scripts/
|   `-- results/
`-- manufacturing/
    |-- prototype/
    `-- released/
```

This is a desired structure. In revision 0.5 there are `README.md`, `docs/pinout-j21.csv`, `docs/pinout.md` and, in `hardware/`, the KiCad project with the five sheets, `symbols/`, `sym-lib-table` and the schematic PDF (section 17.1), as well as the PCB with `footprints/`, `fp-lib-table`, the JLCPCB design rules (`.kicad_dru`), `renders/`, `3d/` and the production files generated for a JLCPCB order in `production/`, described in `hardware/production/README.md` (section 17.2). These files are not a release; the `manufacturing/` folders of the desired structure do not exist yet, nor do the other files and build targets.

## 19. Development flow and approval points

**G0 — Finalize the architecture.** Confirm direction/duplex, LCDs and headers out of scope, the role of HAT identification (proposal to remove the EEPROM, J21-05), mounting and the remaining quantitative requirements.

**G1 — Demonstrate link feasibility.** Complete the J21 pinout, choose clock/banks and the capture strategy (TIM-11), carry out a minimal proof in the tools, review the board-to-board protection and finalize the timing budget.

**G2 — Finalize schematic and mechanics.** Redraw the preserved blocks of Tang revision 3674, implement USB/isolation, review BOM, power, pinout and 3D model.

**G3 — Release prototype.** Complete the layout and the ERC/DRC, assembly and signal integrity reviews; generate a traceable manufacturing package.

**G4 — Qualify and release a functional revision.** Carry out bring-up, validate preserved resources, test link and stability, record actual limits and correct the revision when necessary.

Scripts and automated checks help with editing and extracting information, but they **do not validate the schematic, pinout, timing or manufacturing**. Keep human review and versioning of the generated artifacts: a clean ERC and a checked netlist do not replace this review, and the same applies to the DRC with JLCPCB rules and to the generated production files.

## 20. Pending items and blocking conditions

| Item | Current status | Needed to close |
|---|---|---|
| J21 -> carrier -> SOM -> K26 pins | Mapped through the carrier nets and SOM connector pins to the K26 package pins (F12 + F13, section 6.3), with 0 differences from S1 + F11; document cross-check, not hardware validation | Optional Vivado check with the xck26 part (J21-08) and approval of the pinout freeze (J21-07) |
| Number of actually usable signals | F12 connects all 28 signal contacts to SOM pins (pull-ups on 3, 5, 27 and 28); F3 states 26 I/Os, possibly without the two ID pins (interpretation, not confirmed) | Explanation of the 26 of F3 (section 6.3) |
| Appropriate clock input/output on both sides | Candidates identified on the K26: P-side HDGC on pins 24, 27, 32 and 36; `LINK_CLK` proposed on 32; Gowin side pending | Capture strategy (TIM-11 to TIM-13), selection on the Gowin and implementation proof |
| Voltage and signal paths on J21 | Banks 43 and 44 on PL_3V3 (VCCO_HDB, VCCO_HDC); signal contacts straight to the SOM connector, with carrier pull-ups only on 3, 5, 27 and 28 (F12) | Documented in F12, not measured: hardware confirmation at bring-up (HW-01 to HW-04) |
| 16 bits at 50 MHz | Target, not a result | Reviewed timing and measurement on a prototype |
| 100 MHz | Exploratory (TIM-14) | New analysis and qualification |
| Traffic direction/duplex | Pending | Usage specification and protocol |
| Payload and latency target | Pending | Quantitative criteria and measurement points |
| Outline, holes and height | Proposed from the XTP744 model (F14, MEC-10): the outline and the holes H1/H2 fit J21 and its two holes; HAT bottom about 10.9 mm above the carrier with the 8.5 mm socket and 11 mm M2.5 standoffs | Physical fit check on a KR260 |
| Raspberry Pi mounting holes on the KR260 | Two 2.77 mm holes on the J21 centreline, 58.0 mm apart (F14), matched to MH11/MH12 of F12 by geometry (inference); the HAT holes H1/H2 land on them (MEC-11, Proposed) | Physical fit check on a KR260 |
| J21 pin 1 position on the KR260 | Not marked in the XTP744 model (F14); from S2, the outer column at the end toward the Pmod connectors | Visual check on a real KR260 (MEC-02) |
| FT2232H, translators and isolators | Proposed, not finalized | Electrical/timing/BOM selection |
| `tangnano9k` profile in the programmer | Compatibility objective | Tests with actual hardware and configuration |
| Power, USB current and thermals | Pending sizing; since rev. 0.6 the J21 5 V (1.0 A, F1) can also supply the HAT | PWR-04 budget against the USB source and the 1.0 A of J21, and measurement |
| Dual power (rev. 0.6) | Schematic and PCB updated (PWR-01, Decided); TMI7003C input range with the lower +5V not checked; FT2232H EEPROM settings for self-powered operation not yet programmed | TMI datasheet (PWR-04), EEPROM procedure (section 9) and HW-09 at bring-up |
| Formal HAT/EEPROM identification | Proposed: remove the EEPROM from the scope (J21-05) | Approval of the proposal and confirmation of the ID pins in XTP743 |
| K26 PUDC_B | Pending (ISO-14); state not given in F12 or F13 | Confirmation in DS987 and final sizing of ISO-12 |
| J21 3.3 V versus VCCO of banks 43/44 | Identified (F12, ISO-10): RPI_3V3 is PL_3V3 through the STMPS2161 switch U74, and both bank VCCOs are on PL_3V3 | Optional: decide whether to use the J21 3.3 V as an additional transmit gate (ISO-10, not implemented) |
| Pull-ups on GPIO2/3 and on the ID pins | 4.70k (R326/R327) on 3 and 5 and 3.90k (R330/R331) on 27 and 28, to RPI_3V3 (F12); contacts unconnected on the HAT (Proposed) | Approval of the allocation (section 7.3) |
| Identity of XTP685 | Not confirmed as the K26 XDC; the K26 SOM XDC Rev 1 read in rev. 0.5 (F13) carries no XTP number | Identification of the document; the XDC comes via Vivado Board Awareness, and the board file via XilinxBoardStore (F3) |
| XCK26 × XCZU5EV pinout equivalence | For the 28 J21 signals, the K26 SOM XDC (F13) gives the same package pins and names as `xczu5evsfvc784pkg.txt` (F11) | Optional confirmation with the xck26 part in Vivado (J21-08) |
| Integration of the RX with DPU and VCU | Proposed (KRIA-02) | Budget of resources, clocks, HP/HPC ports and DDR bandwidth |
| Preliminary schematic (rev. 0.4, updated in rev. 0.5 and 0.6) | Captured and redrawn with wires; English texts and the Flash substitution in rev. 0.5; dual power in rev. 0.6; ERC with 0 errors and 0 warnings; netlist checked (209 nets, 174 parts; rev. 0.5: 169 parts) | Complete human review and acceptance of the parts of section 16.1 |
| TMI7003C pinout and current | Read from the 3674; datasheet not consulted | TMI datasheet and PWR-04 budget |
| PTC, TVS, ferrites and buck inductors | Proposed values without a budget | PWR-04 budget |
| Gowin pins 53–57 as I/O | Used by `LINK_D11`–`LINK_D15` | Confirmation in the open flow (GW-02) and in UG290E |
| Footprints | QN88P according to UG119E (figures 4-1 and 4-2); the others not checked | Manufacturers' drawings (PCB-10) |
| Outline, holes and position of J21 on the PCB | Raspberry Pi HAT form factor; matches the KR260 J21 and its two holes in the XTP744 model (F14; MEC-03, MEC-10 and MEC-11, Proposed) | Physical fit check on a KR260 |
| PCB routing | Automatic (Freerouting) with local reroutes; USB pair rerouted as a differential pair in rev. 0.5 (impedance calculated, not measured); clock priority, lengths and signal integrity not reviewed | PCB-02, PCB-03, PCB-07, PCB-13 and PCB-14; USB impedance with the fab's impedance control (PCB-09) |
| Link bit order | Proposed in the schematic | Review during routing |
| JTAG translator OE̅ | Pull-down (enabled by default), against TI's pull-up recommendation | Decision on the power-up behavior |
| Skew between the three SN74LVC244A | Not estimated | TIM-07 budget |
| Flash W25Q32JVZPIQ (U5) | Proposed in place of the P25Q32U (section 16.1); MSPI/boot compatibility with the GW1NR-9 not checked (**Pending**) | Check in the Gowin documentation and at bring-up (HW-05) |
| Parts outside the JLCPCB stock snapshot | GW1NR-LV9QN88PC6/I5 and TMI7003C (snapshot of 2026-10-21) | JLCPCB Global Sourcing or consignment when ordering |
| Thermal vias in the U4 exposed pad | Open holes; epoxy-filled and capped vias not chosen | Decision before ordering (`hardware/production/README.md`) |
| JLCPCB order | Production files generated (section 17.2), not released | Human design review, physical fit check on a KR260 and the other open items of this table |
| LCDs and original headers | Outside the proposed baseline | Confirmation before freezing the architecture |
| Assembler, batch and operating environment | JLCPCB Proposed (section 16); batch and operating environment not defined | Manufacturing and qualification requirements |

**Block manufacturing** in the presence of pins without traceability, a clock without a valid path, a power conflict, inability to protect a powered-off board, mechanical impossibility or insufficient timing for the assumed target. Revise width/frequency/circuit explicitly; do not replace the target with a promise without evidence.

## 21. References and traceability

### 21.1 Sources actually used for this consolidation

**R1 — Base draft:** “Placa custom Tang Nano 9K + Pmod: requisitos” (“Custom Tang Nano 9K + Pmod board: requirements”), draft dated 2026-10-20. Origin of the information on FPGA, voltages, pins of the preserved functions, power topology, FT2232H and tools. The Pmod/cable parts were replaced by the HAT scope.

**R2 — Later design decisions:** keep microSD, remove HDMI, power via USB-C (in rev. 0.6, the USB-C or the J21 5 V), adopt the HAT form factor, remove Pmods, provide optional communication, prioritize speed and install specifically on the KR260.

**R3 — Early technical proposals:** four layers, cited HAT size, FT2232H, removal of the LCDs, 16-bit link at 50 MHz and AXI/DMA integration. Where proof was lacking, the item remains proposed or pending.

**R4 — System context (2026-10-21):** the KR260 PL already runs DPU (DPUCZDX8G) and VCU; the operating system is KAKUEI-OS (customized PetaLinux 2024.2); the tools are Vivado/Vitis 2024.2; the applications run in Docker containers, such as stream-edge.

**R5 — KR260 integration survey (2026-10-21):** based on AMD documentation and community sources. It is the origin of facts F1–F11 (section 21.3), of secondary sources S1–S4 (section 21.4), of the preliminary J21 → K26 map and of the proposed allocation.

### 21.2 Primary documents to consult and version

| Document | Expected use | Note |
|---|---|---|
| Sipeed Tang Nano 9K, schematic revision 3674 and interactive BOM 3674 | Redraw of the preserved blocks | Used in rev. 0.4 for topology and values (section 16.1); confirm revision and nets |
| 3672 schematic and dimensional drawing of the Tang | History/comparison | Does not define the HAT mechanics |
| Gowin UG803E GW1NR-9, pinout including QN88P | Pins, banks and VCCIO3/PSRAM restrictions | v1.6.5 used in rev. 0.4 for the symbol (88 pins + EPAD); pin 63 and the name of pin 4 checked by hand |
| GW1NR-9 datasheet and design guides | Power, clock, I/O, timing and IBIS model (PCB-14) | Select the exact document |
| AMD KR260 UG1092 | Interfaces, installation and J21 power | Source of F1 and F2; does not replace the schematic |
| AMD KR260 DS988 | Electrical characteristics | Confirm applicable limits |
| KR260/carrier schematic, cited as XTP743 | J21 and components in the path | Published on the KR260 page, with license acceptance (F3); according to S1, the download includes the master XDC. Read in rev. 0.5 as F12: the carrier card schematic SCK-KR-05101, doc. 038-05101-01 rev A02, 2021-10-15; the XTP number does not appear in that file |
| K26 constraints/pinout, cited as XTP685 | SOM -> FPGA pins and banks | **Identity not confirmed** as the K26 XDC (Pending). According to the KR260 page, the XDC comes via Vivado Board Awareness, and the board file via XilinxBoardStore (F3). The K26 SOM XDC Rev 1 (`Kria_K26_SOM_Rev1.xdc`, F13) was read in rev. 0.5 and cross-checked with the carrier (F12); it carries no XTP number |
| KR260 mechanical documentation and applicable HAT specification | Outline, holes, height and header | The initial 65 × 56.5 mm reference is not an official source; the carrier model is XTP744, read in rev. 0.5 as F14 |
| Datasheets of the FT2232H, translators, EEPROM, Flash and regulators | Circuits and worst case | Do not infer compatibility from the part name |
| Manufacturer's stack-up and rules | Impedances and manufacturability | Obtain before finalizing routing |
| XTP744: KR260 carrier 3D CAD model | Outline, holes and heights (MEC-10, MEC-11) | Published with license acceptance (F3). Read in rev. 0.5 as F14 (readme v1.0, 2022; `KR260-startkit-A02.stp`, carrier 128_05101_01 rev A02). Marked Xilinx confidential/proprietary: not copied into the repository |
| XTP750: carrier schematic source | Nets and components of the J21 path | Published with license acceptance (F3) |
| XTP756: carrier Allegro layout | Lengths and stack-up from J21 to the SOM connector (PCB-15) | Published with license acceptance (F3) |
| XTP757: carrier BOM | Components in the J21 path | Published with license acceptance (F3) |
| KR260 XDC and board files | Constraints and board configuration in Vivado | XDC via Vivado Board Awareness; board file via XilinxBoardStore (F3). The K26 SOM XDC (F13) was read directly in rev. 0.5 |
| DS987: K26 data sheet | SOM part (F10) and PUDC_B (ISO-14) | Confirm PUDC_B, which F12 and F13 do not give |
| DS925: Zynq UltraScale+ DC and AC characteristics | Absolute maximums and DC characteristics of the HD banks (F4) | — |
| UG571: UltraScale SelectIO | HD I/O logic in Zynq UltraScale+ | Confirm F8 and S4 |
| UG572: UltraScale clocking | HDGC, BUFGCE and MMCM (F6) | — |
| UG1075: Zynq UltraScale+ packaging and pinout | HDGC pairs per HD bank (F5) | — |
| UG1091: Kria carrier card design | Carrier design reference for the K26 SOM | https://docs.amd.com/r/en-US/ug1091-carrier-card-design |
| UG1192: conversion methodology | Global clock inputs and board planning (F7) | — |
| UG861: SelectIO, UltraScale+ family | HD I/O logic resources (F8) | For Zynq UltraScale+, confirm in UG571 |
| `xczu5evsfvc784pkg.txt`: XCZU5EV-SFVC784 pinout | Pin names and banks of the J21 → K26 map (F11) | Reference for the XCK26; the K26 SOM XDC (F13) gives the same pins and names for the 28 J21 signals; Vivado check with the xck26 part optional (J21-08) |
| Kria dfx-mgr/xmutil documentation | PL loading and application firmware package (F9, KRIA-01) | The recorded link is from the 2022.1 documentation; confirm in the 2024.2 baseline (KRIA-05) |
| FTDI FT2232H Datasheet, FT_000061 v2.10 | FT2232H circuit (figures 6.1 and 6.5); self-powered PWRSAV# divider and EEPROM settings (table 3.3, section 6.2 and figure 6.3; rev. 0.6) | Copy from a mirror (ecsxtal.com); check against the FTDI original |
| TI SN74AVC4T774 (SCES693I), SN74LVC244A, SN74LVC3G17 and SN74LVC1G00 | Pinout, Ioff and pull-up recommendation on OE | ti.com |
| Gowin DS117E v3.2.5 | Weak pull-up of 30 to 150 µA on the GPIOs during configuration (ISO-15) | docs/gowin |
| Gowin UG119E v1.8.4 | QN88P drawing (6.74 mm EP) and recommended layout | docs/gowin |

Local references cited in the source document:

```text
docs/schematics/Tang_Nano_9K_3674_schematic.pdf
docs/schematics/Tang_Nano_9K_3672_schematic.pdf
docs/board/Tang_Nano_9K_3672_dimension_drawing.pdf
docs/gowin/UG803E_GW1NR-9_pinout_incl_QN88P_v1.6.5.pdf
```

These paths are references to the project environment, **not files included with this README or inspected automatically**. In revision 0.5, three AMD files were read from local copies: the carrier schematic (F12), the K26 SOM XDC (F13) and the XTP744 carrier 3D model (F14). The model is marked confidential and is not copied into the repository, nor is the KiCad 3D view of the HAT on it. The old `pmod.kicad_sch` can serve as a reference for library/protection conventions, not as the pinout of the new J21.

Record the origin and usage permissions of the libraries and documents; do not assume that a public PDF includes an editable KiCad project or a license to redistribute the derived design.

### 21.3 Facts from official AMD documentation (F1–F14)

F1–F11 are facts gathered in R5; they are entered as fact, with the source cited, and their documents were not reopened in this consolidation. F12 to F14 were read in revision 0.5 from local copies of the AMD files; F14 comes from a model marked confidential, so only the facts below are recorded.

| ID | Fact | Source | Link for checking |
|---|---|---|---|
| F1 | J21 is the Raspberry Pi expansion header for HATs. It is supplied with 3.3 V and 5.0 V, with a limit of 1.0 A per rail. | UG1092 | https://docs.amd.com/r/en-US/ug1092-kr260-starter-kit/Powering-the-Starter-Kit-and-Power-Budgets |
| F2 | The carrier only supplies the PL VCCO rails after the SOM asserts VCCOEN_PS_M2C and VCCOEN_PL_M2C. | UG1092 | Same link as F1 |
| F3 | The Raspberry Pi header has 26 I/Os. The kit, with the active thermal solution (fan and heatsink), measures 119 × 140 × 36 mm. Published resources, with license acceptance: XTP743 (schematic), XTP744 (carrier 3D CAD model), XTP750 (schematic source), XTP756 (Allegro layout) and XTP757 (BOM). The XDC comes via Vivado Board Awareness, and the board file via XilinxBoardStore. | Official KR260 page | https://www.amd.com/en/products/system-on-modules/kria/k26/kr260-robotics-starter-kit.html |
| F4 | In HD banks, the absolute maximum input voltage ranges from −0.55 V to VCCO + 0.55 V. With VCCO off, any 3.3 V coming from the HAT violates this limit. The internal pull-up is 75 to 190 µA with VCCO = 3.3 V. | DS925 | https://docs.amd.com/r/en-US/ds925-zynq-ultrascale-plus/Absolute-Maximum-Ratings and https://docs.amd.com/r/en-US/ds925-zynq-ultrascale-plus/DC-Characteristics-Over-Recommended-Operating-Conditions |
| F5 | Each HD bank has four HDGC pairs. HDGC has direct access only to the global clock buffers; GC pins also reach MMCM/PLL. A single-ended clock goes on the P side of the pair. | UG1075 | — |
| F6 | HD banks have no adjacent CMT, so HDGC only drives BUFGCE directly. When an MMCM is fed by a BUFGCE, it does not compensate the delay of that path. | UG572 | https://docs.amd.com/r/en-US/ug572-ultrascale-clocking/MMCM-Clock-Input-Signals |
| F7 | With a single-ended clock on the P side, the N side cannot be another clock, but it can be a regular I/O. | UG1192 | https://docs.amd.com/r/en-US/conversion-methodology/Global-Clock-Inputs-and-Board-Planning |
| F8 | The HD I/O logic supports IDDRE1/ODDRE1 and has no dedicated phase-alignment circuit. The register clock goes through the global network, which reduces performance. | UG861, HD I/O section (UltraScale+ family; for Zynq UltraScale+, confirm in UG571) | https://docs.amd.com/r/en-US/ug861-ultrascale-selectio/HD-I/O-Interface-Logic-Resources |
| F9 | Each PL application is located in `/lib/firmware/xilinx/<app>`, with `.bit.bin`, `.dtbo` and `shell.json` (plus `.xclbin` in the Vitis/XRT flow). In the standard Kria images, the PL is loaded after Linux. | Kria documentation (dfx-mgr/xmutil) | https://xilinx.github.io/kria-apps-docs/creating_applications/2022.1/build/html/docs/kria_vitis_acceleration_flow/petalinux-firmware.html |
| F10 | The K26 uses the XCK26-SFVC784-2LV-C/I. | DS987 | — |
| F11 | The official pinout file `xczu5evsfvc784pkg.txt` was used as the reference for the XCK26. Confirm the pin names with the xck26 part in Vivado. | AMD, pinout file | https://download.amd.com/adaptive-socs-and-fpgas/developer/adaptive-socs-and-fpgas/package-pinout-files/zuppackages/xczu5evsfvc784pkg.txt |
| F12 | The KR260 carrier card schematic SCK-KR-05101 "Robotics Starter Kit Carrier Card" (doc. 038-05101-01 rev A02, 2021-10-15) connects each of the 28 J21 signal contacts through an HDC/HDB net (sheet 12) to a SOM240_2 connector pin (sheet 7), with no series resistor or level shifter. Contacts 3 and 5 have 4.70k pull-ups (R326/R327) and contacts 27 and 28 have 3.90k pull-ups (R330/R331), all to RPI_3V3. RPI_3V3 (contacts 1 and 17) is PL_3V3 through the STMPS2161 switch U74 (EN tied to GND through R332, 10.0k), and RPI_5V0 (contacts 2 and 4) is 5V0_IN through the STMPS2161 switch U73; the GND contacts are 6, 9, 14, 20, 25, 30, 34 and 39. VCCO_HDC (bank 44) and VCCO_HDB (bank 43) are tied to PL_3V3 (sheet 7), a 3.3 V/3 A rail enabled by VCCOEN_PL_M2C (sheet 5). Sheet 12 also shows two grounded mounting holes, MH11 and MH12, without their positions. | Carrier schematic (cited as XTP743), file `038-05101-01_sck-kr_reva02_SKIT_20211015.pdf` | Local copy, not in this repository |
| F13 | The K26 SOM XDC Rev 1 gives, for each SOM240_2 pin, the package pin, bank, VCCO pin and pin name. For the 28 J21 signals, the SOM240_2 pins reached through F12 have the package pins and names of section 6.3, in banks 43 and 44; the bank VCCO pin is som240_2_d59 for bank 44 and som240_2_b59 for bank 43. It lists the net FPGA_PUDC_B on package pin U7, without its state. | K26 SOM XDC, file `Kria_K26_SOM_Rev1.xdc` | Local copy, not in this repository |
| F14 | The KR260 carrier 3D model (assembly KR260_STARTKIT_ASM, 2021-10-15, carrier 128_05101_01 rev A02; millimetres, carrier top surface at z = 0) has a 140 × 119 mm carrier outline. J21 (HDR_2X20) occupies x 126.90–131.98 and y 45.41–96.22, along the right edge and 3 mm from it, with pin columns at x 128.17 and 130.71, rows from y 46.69 to 94.95 (2.54 mm pitch), the plastic body top at z 2.40 and the pin tips at z 8.24. The board solid has two 2.77 mm holes at (129.44, 41.82) and (129.44, 99.82), on the J21 centreline, 58.0 mm apart and 4.87 mm beyond the end pins. Top heights of nearby parts: dual RJ45 z 27.0, SFP cage z 10.2, SOM fan heatsink z 29.2, dual USB z 15.7. The model does not mark pin 1 and has no reference designators. | XTP744 "Kria KR260 Carrier Card 3D CAD Model", `xtp744-kr260-carrier-card-3d-cad-model.zip` (readme v1.0, 2022), file `KR260-startkit-A02.stp`, read with OpenCASCADE (assembly names, bounding boxes, holes from the cylindrical faces of the board solid) | Local copy; marked Xilinx confidential/proprietary and not copied into the repository |

### 21.4 Secondary sources (preliminary)

Data from these sources appear in the document as **preliminary — confirm in XTP743**, or in the official document indicated in the last column, unless an official source now confirms them: in revision 0.5, the S1 pin map and the S3 power and GND pinout were cross-checked against F12 and F13 (section 6.3).

| ID | Content | Source | Link | Confirm in |
|---|---|---|---|---|
| S1 | XDC in which the 28 J21 signals GPIO0–27, including ID_SD/ID_SC, go to K26 PL pins, all in LVCMOS33. According to the author, it derives from the master XDC included in the XTP743 download. | Whitney Knitter, Hackster, 2022 | https://www.hackster.io/whitney-knitter/rpi-pmod-connector-gpio-with-custom-pl-design-in-kria-kr260-53c40e | XTP743 (cross-checked against F12 and F13 in rev. 0.5: 0 differences) |
| S2 | Uses AE15/AE14 for I²C (GPIO2/3) and AA12 for the interrupt on header pin 16 (GPIO23), consistent with S1. Shows a Sense HAT mounted on J21: an indication of physical fit, without validating the fastening. | Sense HAT tutorial on the KR260, LogicTronix | https://www.hackster.io/LogicTronix/jumpstart-the-kr260-with-raspberry-pi-sensehat-petalinux-308dc5 | XTP743 (pins: consistent with F12 and F13 in rev. 0.5); XTP744 (mechanics: F14 gives the fit but does not mark pin 1, so the orientation still rests on this photo; visual check on a real KR260) |
| S3 | Standard Raspberry Pi pinout: GND on pins 6, 9, 14, 20, 25, 30, 34 and 39; 3.3 V on pins 1 and 17; 5 V on pins 2 and 4. | Standard Raspberry Pi pinout | — | XTP743 (matches F12, sheet 12, in rev. 0.5) |
| S4 | HD banks have no IDELAY. | AMD support forum, community member | https://adaptivesupport.amd.com/s/question/0D52E00006hpKWvSAM/timing-constraints-for-rgmii?language=en_US | UG571 |

## 22. Status and definition of done

The current scope is a **customized Tang Nano 9K, without Pmods, mounted on the KR260 J21, powered from J21 or from its own USB-C, with preserved microSD**. The 16-bit parallel link at 50 MHz is the starting proposal, subject to demonstrated feasibility.

The project will be ready for use when the fit and electrical safety are proven, the preserved functions pass the tests, the link operates according to the protocol under load and backpressure, and the hardware/firmware package results in reproducible builds and measurements.

**Current status: requirements consolidated; J21 → K26 map cross-checked against the KR260 carrier schematic and the K26 SOM XDC (F12, F13) as a document check; preliminary schematic captured and PCB prepared for JLCPCB fabrication and assembly, with a provisional outline (Proposed), powered from the USB-C or from the J21 5 V since rev. 0.6; production files generated for an order, not released; mechanical fit checked only against the KR260 3D model (XTP744, F14), physical fit check Pending; no PCB manufactured, and no full compatibility or link speed proven by this document.**
