# J21 ↔ K26 ↔ HAT pinout

Revision 0.6 (2026-10-21). Readable version of `docs/pinout-j21.csv`; requirements and criteria in the README, sections 6, 7.3, 8.3 and 17.1.

> **This document is not a release for manufacturing.** The J21 → K26 map was cross-checked against the KR260 carrier schematic (cited as XTP743, F12) and the K26 SOM XDC (F13): the 28 signal contacts match S1 and F11 with 0 differences. This is a document cross-check, not hardware validation. The allocation on the HAT, the bit order and the Gowin pins are **Proposed**, from the preliminary schematic (`hardware/`). Nothing here was measured or validated in hardware.

## 1. 2 × 20 header view (Proposed)

| HAT signal | Silk | RPi signal | Pin | Pin | RPi signal | Silk | HAT signal |
|---|---|---|---:|---:|---|---|---|
| NC (power) | 3V3 | 3V3 | 1 | 2 | 5V | 5V | 5 V input (J21_5V) |
| R I²C (NC) | NC | GPIO2 (I²C SDA) | 3 | 4 | 5V | 5V | 5 V input (J21_5V) |
| R I²C (NC) | NC | GPIO3 (I²C SCL) | 5 | 6 | GND | GND | GND |
| LINK_D0 | D0 | GPIO4 | 7 | 8 | GPIO14 | D1 | LINK_D1 |
| GND | GND | GND | 9 | 10 | GPIO15 | D2 | LINK_D2 |
| LINK_D3 | D3 | GPIO17 | 11 | 12 | GPIO18 | D4 | LINK_D4 |
| LINK_RESET_N | RST | GPIO27 | 13 | 14 | GND | GND | GND |
| LINK_D5 | D5 | GPIO22 | 15 | 16 | GPIO23 | D6 | LINK_D6 |
| NC (power) | 3V3 | 3V3 | 17 | 18 | GPIO24 | NC | reserve (NC) |
| LINK_D7 | D7 | GPIO10 | 19 | 20 | GND | GND | GND |
| LINK_D8 | D8 | GPIO9 | 21 | 22 | GPIO25 | NC | reserve (NC) |
| LINK_D9 | D9 | GPIO11 | 23 | 24 | GPIO8 | D10 | LINK_D10 |
| GND | GND | GND | 25 | 26 | GPIO7 | D11 | LINK_D11 |
| R ID (NC) | NC | GPIO0 (ID_SD) | 27 | 28 | GPIO1 (ID_SC) | NC | R ID (NC) |
| LINK_VALID | VLD | GPIO5 | 29 | 30 | GND | GND | GND |
| **LINK_EN** | EN | GPIO6 | 31 | 32 | GPIO12 | CLK | **LINK_CLK** |
| LINK_READY | RDY | GPIO13 | 33 | 34 | GND | GND | GND |
| LINK_D12 | D12 | GPIO19 | 35 | 36 | GPIO16 | D13 | LINK_D13 |
| reserve (NC) | NC | GPIO26 | 37 | 38 | GPIO20 | D14 | LINK_D14 |
| GND | GND | GND | 39 | 40 | GPIO21 | D15 | LINK_D15 |

`LINK_CLK` (32) sits between GNDs 30 and 34; `LINK_EN` (31), quasi-static, sits opposite it; on the diagonals (29 and 33) are `LINK_VALID` and `LINK_READY`, which have low activity.

Silk: label printed next to each J130 pin on the top side of the HAT (revision 0.5). D0–D15 = `LINK_D0`–`LINK_D15` (`LINK_DATA[15:0]`), CLK = `LINK_CLK`, VLD = `LINK_VALID`, RDY = `LINK_READY`, RST = `LINK_RESET_N`, EN = `LINK_EN`; GND, 3V3 and 5V mark the KR260 rails (5V feeds the HAT through D4 since revision 0.6; 3V3 is not connected); NC marks the contacts left unconnected (3, 5, 18, 22, 27, 28 and 37). Even pins are labelled between the board-edge row and the board edge, odd pins below the inner row, in 0.9 mm text.

## 2. Map by contact

Signals, K26 pins and package pin names: S1 and F11, cross-checked against F12 (sheets 12 and 7) and F13 with 0 differences. Power and GND: S3, matching F12 (sheet 12). Columns "HAT signal" and "Gowin": **Proposed**.

| J21 | RPi signal | KR260 net (F12) | SOM240_2 pin | K26 pin | Package pin name | Bank | Clock | HAT signal | Silk | Gowin (pin, bank) | Path on the HAT |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3V3 | RPI_3V3 | — | — | — | — | — | NC (power) | 3V3 | — | — |
| 2 | 5V | RPI_5V0 | — | — | — | — | — | 5 V input (J21_5V) | 5V | — | `J21_5V` → D4 (B5819W) → +5V; C14 10 µF |
| 3 | GPIO2 (I²C SDA) | RPI_GPIO2_SDA (HDC02) | d54 | AE15 | IO_L1P_AD15P_44 | 44 | — | R I²C (NC) | NC | — | — |
| 4 | 5V | RPI_5V0 | — | — | — | — | — | 5 V input (J21_5V) | 5V | — | `J21_5V` → D4 (B5819W) → +5V; C14 10 µF |
| 5 | GPIO3 (I²C SCL) | RPI_GPIO3_SCL (HDC03) | d56 | AE14 | IO_L1N_AD15N_44 | 44 | — | R I²C (NC) | NC | — | — |
| 6 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 7 | GPIO4 | RPI_GPIO4_GPCLK0 (HDC04) | d57 | AG14 | IO_L2P_AD14P_44 | 44 | — | LINK_D0 | D0 | 68 (IOT42B), bank 1 | U130 1A2→1Y2, R132 22R |
| 8 | GPIO14 | RPI_GPIO14_TXD (HDC14) | b54 | W14 | IO_L9P_AD11P_44 | 44 | — | LINK_D1 | D1 | 69 (IOT42A), bank 1 | U130 1A3→1Y3, R133 22R |
| 9 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 10 | GPIO15 | RPI_GPIO15_RXD (HDC15) | b56 | W13 | IO_L9N_AD11N_44 | 44 | — | LINK_D2 | D2 | 70 (IOT41B), bank 1 | U130 2A0→2Y0, R134 22R |
| 11 | GPIO17 | RPI_GPIO17 (HDC17) | b58 | AB14 | IO_L8N_HDGC_44 | 44 | HDGC N | LINK_D3 | D3 | 71 (IOT41A), bank 1 | U130 2A1→2Y1, R135 22R |
| 12 | GPIO18 | RPI_GPIO18_PCM_CLK (HDC18) | a54 | Y14 | IO_L10P_AD10P_44 | 44 | — | LINK_D4 | D4 | 72 (IOT39B), bank 1 | U130 2A2→2Y2, R136 22R |
| 13 | GPIO27 | RPI_GPIO27 (HDB23) | a52 | AB9 | IO_L12N_AD0N_43 | 43 | — | LINK_RESET_N | RST | 42 (IOB41B), bank 2 | U133C (74LVC3G17) 3→5 |
| 14 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 15 | GPIO22 | RPI_GPIO22 (HDC22) | a59 | Y12 | IO_L12P_AD8P_44 | 44 | — | LINK_D5 | D5 | 75 (IOT38A), bank 1 | U130 2A3→2Y3, R137 22R |
| 16 | GPIO23 | RPI_GPIO23 (HDC23) | a60 | AA12 | IO_L12N_AD8N_44 | 44 | — | LINK_D6 | D6 | 76 (IOT37B), bank 1 | U131 1A0→1Y0, R138 22R |
| 17 | 3V3 | RPI_3V3 | — | — | — | — | — | NC (power) | 3V3 | — | — |
| 18 | GPIO24 | RPI_GPIO24 (HDB20) | a48 | Y9 | IO_L11P_AD1P_43 | 43 | — | reserve (NC) | NC | — | — |
| 19 | GPIO10 | RPI_GPIO10_MOSI (HDC10) | c59 | AE13 | IO_L4P_AD12P_44 | 44 | — | LINK_D7 | D7 | 77 (IOT37A), bank 1 | U131 1A1→1Y1, R139 22R |
| 20 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 21 | GPIO9 | RPI_GPIO9_MISO (HDC09) | c58 | AC13 | IO_L6N_HDGC_44 | 44 | HDGC N | LINK_D8 | D8 | 48 (IOR24B), bank 1 | U131 1A2→1Y2, R140 22R |
| 22 | GPIO25 | RPI_GPIO25 (HDB21) | a50 | AA8 | IO_L11N_AD1N_43 | 43 | — | reserve (NC) | NC | — | — |
| 23 | GPIO11 | RPI_GPIO11_SCLK (HDC11) | c60 | AF13 | IO_L4N_AD12N_44 | 44 | — | LINK_D9 | D9 | 49 (IOR24A), bank 1 | U131 1A3→1Y3, R141 22R |
| 24 | GPIO8 | RPI_GPIO8_CE0 (HDC08_CC) | c56 | AC14 | IO_L6P_HDGC_44 | 44 | HDGC P | LINK_D10 | D10 | 50 (IOR22B), bank 1 | U131 2A0→2Y0, R142 22R |
| 25 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 26 | GPIO7 | RPI_GPIO7_CE1 (HDC07) | c55 | AH13 | IO_L3N_AD13N_44 | 44 | — | LINK_D11 | D11 | 53 (IOR15B/DOUT/WE_N), bank 1 | U131 2A1→2Y1, R143 22R |
| 27 | GPIO0 (ID_SD) | RPI_GPIO0_ID_SD (HDC00_CC) | d52 | AD15 | IO_L5P_HDGC_44 | 44 | HDGC P | R ID (NC) | NC | — | — |
| 28 | GPIO1 (ID_SC) | RPI_GPIO1_ID_SC (HDC01) | d53 | AD14 | IO_L5N_HDGC_44 | 44 | HDGC N | R ID (NC) | NC | — | — |
| 29 | GPIO5 | RPI_GPIO5 (HDC05) | d58 | AH14 | IO_L2N_AD14N_44 | 44 | — | LINK_VALID | VLD | 74 (IOT38B), bank 1 | U130 1A1→1Y1, R131 22R |
| 30 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 31 | GPIO6 | RPI_GPIO6 (HDC06) | c54 | AG13 | IO_L3P_AD13P_44 | 44 | — | **LINK_EN** | EN | 40 (IOB33B), bank 2 | U133A (74LVC3G17) 1→7; also goes into U134 (74LVC1G00) |
| 32 | GPIO12 | RPI_GPIO12_PWM0 (HDC12) | b52 | AA13 | IO_L7P_HDGC_44 | 44 | HDGC P | **LINK_CLK** | CLK | 73 (IOT39A), bank 1 | U130 1A0→1Y0, R130 22R |
| 33 | GPIO13 | RPI_GPIO13_PWM1 (HDC13) | b53 | AB13 | IO_L7N_HDGC_44 | 44 | HDGC N | LINK_READY | RDY | 41 (IOB41A), bank 2 | U133B (74LVC3G17) 6→2 |
| 34 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 35 | GPIO19 | RPI_GPIO19_PCM_FS (HDC19) | a55 | Y13 | IO_L10N_AD10N_44 | 44 | — | LINK_D12 | D12 | 54 (IOR15A/DIN/CLKHOLD_N), bank 1 | U131 2A2→2Y2, R144 22R |
| 36 | GPIO16 | RPI_GPIO16 (HDC16_CC) | b57 | AB15 | IO_L8P_HDGC_44 | 44 | HDGC P | LINK_D13 | D13 | 55 (IOR14B/SSPI_CS_N/D0), bank 1 | U131 2A3→2Y3, R145 22R |
| 37 | GPIO26 | RPI_GPIO26 (HDB22) | a51 | AB10 | IO_L12P_AD0P_43 | 43 | — | reserve (NC) | NC | — | — |
| 38 | GPIO20 | RPI_GPIO20_PCM_DIN (HDC20) | a56 | W12 | IO_L11P_AD9P_44 | 44 | — | LINK_D14 | D14 | 56 (IOR14A/SO/D1), bank 1 | U132 1A0→1Y0, R146 22R |
| 39 | GND | GND | — | — | — | — | — | GND | GND | — | — |
| 40 | GPIO21 | RPI_GPIO21_PCM_DOUT (HDC21) | a58 | W11 | IO_L11N_AD9N_44 | 44 | — | LINK_D15 | D15 | 57 (IOR13A/FASTRD_N/D3), bank 1 | U132 1A1→1Y1, R147 22R |

Internal signal, without a contact on J21: `LINK_TX_EN`, GW1NR pin 47 (IOB43B, bank 2), goes into U134 (74LVC1G00) and has a 4.7k pull-down (R155). Proposed in rev. 0.4 (ISO-15).

## 3. Direction and state with one of the boards powered off (Proposed)

| Signal | J21 contacts | `direction` | `power_off_state` |
|---|---|---|---|
| LINK_CLK | 32 | HAT → KR260; driver enabled only with LINK_OE_N low (OE in hardware: NAND of LINK_EN and LINK_TX_EN, ISO-11/ISO-15); behavior while LINK_RESET_N is low to be defined (LINK-07) | before LINK_EN is high, HAT driver (74LVC244A, Ioff) in high impedance, with a 100k pull-down on the J21 side (R154; value Pending, ISO-12); KR260 off or without a bitstream: LINK_EN stays low (ISO-09) |
| LINK_VALID | 29 | HAT → KR260; driver enabled only with LINK_OE_N low (OE in hardware: NAND of LINK_EN and LINK_TX_EN, ISO-11/ISO-15) | before LINK_EN is high, HAT driver (74LVC244A, Ioff) in high impedance, with a 100k pull-down on the J21 side (R153; value Pending, ISO-12) |
| LINK_D0–LINK_D15 | 7, 8, 10, 11, 12, 15, 16, 19, 21, 23, 24, 26, 35, 36, 38, 40 | HAT → KR260; driver enabled only with LINK_OE_N low (OE in hardware: NAND of LINK_EN and LINK_TX_EN, ISO-11/ISO-15) | before LINK_EN is high, HAT driver (74LVC244A, Ioff) in high impedance, no pull proposed |
| LINK_EN | 31 | KR260 → HAT; enters through a Schmitt receiver with Ioff (74LVC3G17, ISO-13); controls the OE of the output buffers via U134 (ISO-11) | 3.3k pull-down on the J21 side (R150; R ≤ 0.8 V / 190 µA, ISO-12): floating or pulled down = do not transmit; HAT off: receiver with Ioff, no back-powering |
| LINK_READY | 33 | KR260 → HAT; enters through a Schmitt receiver with Ioff (74LVC3G17, ISO-13) | 3.3k pull-down on the J21 side (R151, ISO-12); HAT off: receiver with Ioff |
| LINK_RESET_N | 13 | KR260 → HAT; enters through a Schmitt receiver with Ioff (74LVC3G17, ISO-13) | 3.3k pull-down on the J21 side (R152, ISO-12): low = reset = do not transmit; HAT off: receiver with Ioff; LINK_EN (bank 44) does not indicate the VCCO of bank 43 |
| bank 43 reserve | 18, 22, 37 | unused by the HAT (reserve) | not driven by the HAT (no connection; ISO-09) |
| reserved | 3, 5 | unused by the HAT (reserved) | not driven by the HAT (no connection; ISO-09) |
| reserved | 27, 28 | unused by the HAT (reserved) | not driven by the HAT (no connection; ISO-09) |
| J21_5V | 2, 4 | KR260 → HAT power (RPI_5V0, 1.0 A per rail, F1) | D4 keeps the HAT +5V (from the USB-C) out of the KR260 5 V; no interconnection of supplies (ISO-01, ISO-04) |
| no power connection on the HAT | 1, 17 | not applicable (KR260 power, not used by the HAT) | no connection on the HAT; no interconnection of supplies (ISO-01, ISO-02) |
| GND | 6, 9, 14, 20, 25, 30, 34, 39 | not applicable (GND) | GND always connected to the plane (ISO-03) |

## 4. CSV columns filled from F12 and F13 in this revision

| Column | Value in the CSV | Source |
|---|---|---|
| `kr260_net` | Carrier net and SOM connector signal, e.g. `RPI_GPIO2_SDA (HDC02)`; `RPI_3V3`, `RPI_5V0` or `GND` on the power and GND contacts | F12, sheet 12 |
| `carrier_components` | 4.70k pull-ups to RPI_3V3 on 3 and 5 (R326/R327) and 3.90k on 27 and 28 (R330/R331); `none (direct to SOM240_2)` on the other signal contacts; STMPS2161STR switches U74 (RPI_3V3) and U73 (RPI_5V0) on the power contacts | F12, sheet 12 |
| `som_pin` | SOM240_2 connector pin, e.g. `som240_2_d54`; `—` on the power and GND contacts | F12, sheet 7 |
| `k26_bank_vcco` | Bank and VCCO = PL_3V3 (VCCO_HDC for bank 44, VCCO_HDB for bank 43) | F12, sheet 7; F13 |

The `source` column cites F12 and F13 for every contact (section 6). The new last column, `hat_silkscreen`, gives the J130 silkscreen label of section 1; it comes from the HAT board file (`hardware/`) and follows the Proposed allocation.

## 5. Notes

- GPIO0–23 occupy the 24 I/Os of bank 44, which is entirely dedicated to J21. GPIO24–27 are in bank 43, shared with Pmods 3 and 4.
- HAT → KR260 outputs (`LINK_CLK`, `LINK_VALID`, `LINK_D0–15`) come from three 74LVC244A (U130–U132); the clock shares U130 with VALID and D0–D5, and the skew between packages goes into the TIM-07 budget.
- The 18 output signals use pins of Gowin bank 1 (68–77, 48–50 and 53–57); the three input signals and `LINK_TX_EN` use bank 2 (40, 41, 42 and 47). Pin 51 (pair of the 27 MHz clock on 52) and 63 (PLL input) were left free.
- Alternatives for `LINK_CLK`: 24 and 36 (P-side HDGC), at the cost of reassigning two data signals.
- **5 V from J21 (revision 0.6):** contacts 2 and 4 (RPI_5V0, behind the carrier switch U73, F12) feed `J21_5V`, which reaches +5V through the Schottky D4; the USB-C reaches +5V through D3, so either source alone runs the HAT and neither feeds the other (README PWR-01, ISO-01). Contacts 1 and 17 (RPI_3V3) stay unconnected.
- **Carrier parts (F12):** 4.70k pull-ups to RPI_3V3 on contacts 3 and 5 (R326/R327) and 3.90k on 27 and 28 (R330/R331); the HAT leaves these four contacts unconnected (Proposed). The other signal contacts, including the HAT inputs 13, 31 and 33, go straight to the SOM connector, with no carrier pull-up, series resistor or level shifter.
- **26 × 28 discrepancy (Pending):** the KR260 page states 26 I/Os (F3); S1 connects 28 signals, and F12 connects all 28 signal contacts, including ID_SD/ID_SC (27 and 28), to SOM connector pins. One possible reading, not confirmed, is that the 26 excludes the two ID pins. The allocation only still holds with 26 I/Os if the two contacts left out of the count are among the unconnected ones (3, 5, 18, 22, 27, 28 and 37).
- **Cross-check (revision 0.5):** each signal contact was traced J21 → HDC/HDB net (F12, sheet 12) → som240_2 pin (F12, sheet 7) → package pin and name (F13), with 0 differences from S1 and F11; the transcription check of revision 0.3 against `xczu5evsfvc784pkg.txt` also matched. The optional Vivado check with the xck26 part (README, J21-08) has not been done.

## 6. Sources in the `source` column

- **Signal contacts:** F12 (carrier schematic 038-05101-01 rev A02) sheet 12 (J21 → HDC/HDB net) and sheet 7 (net → som240_2 pin); F13 (Kria_K26_SOM_Rev1.xdc) (som240_2 pin → package pin, name and bank); same as S1 (XDC Hackster 2022) and F11 (xczu5evsfvc784pkg.txt); allocation: rev. 0.4 proposal (preliminary schematic hardware/). Pins 3, 5 and 16 add "consistent with S2 (LogicTronix)"; the HDGC pins add "HDGC: F5, F7".
- **Power and GND:** F12 (carrier schematic 038-05101-01 rev A02) sheet 12; same as S3 (standard Raspberry Pi pinout); allocation: rev. 0.4 proposal (preliminary schematic hardware/).
