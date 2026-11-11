# Datasheets: index

Status: 2026-11-11 · The PDFs themselves are copyrighted and are **not** committed: `datasheets/` is in
`.gitignore`. Download them again with `just datasheets` (`just datasheets force=1` overwrites); the URL list lives in
`hardware/scripts/fetch_datasheets.sh`. Extracted and verified facts: [datasheet-facts.md](datasheet-facts.md);
review result: [wiring-review.md](wiring-review.md).

Source rule: manufacturer URL where it could be downloaded automatically, otherwise the datasheet link on the LCSC
part page (the PDF there is the manufacturer's document). All files were downloaded on **2026-11-09**.

## Main board

| Ref | Part | Manufacturer | Document, revision | URL | File |
|---|---|---|---|---|---|
| U1 | ESP32-C6-MINI-1-H8 | Espressif | ESP32-C6-MINI-1 & MINI-1U Datasheet, v1.5 (2026-06-16) | [espressif.com](https://www.espressif.com/sites/default/files/documentation/esp32-c6-mini-1_mini-1u_datasheet_en.pdf) | `ESP32-C6-MINI-1_datasheet_en.pdf` |
| U1 | ESP32-C6 (chip) | Espressif | ESP32-C6 Series Datasheet, v1.5 (2026-03-31) | [espressif.com](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf) | `ESP32-C6_datasheet_en.pdf` |
| U1 | ESP32-C6 | Espressif | ESP32-C6 Hardware Design Guidelines, release "master" (living document, PDF built 2026-11-09, no version number; PDF page = printed page + 3) | [docs.espressif.com](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/esp-hardware-design-guidelines-en-master-esp32c6.pdf) | `ESP32-C6_hardware_design_guidelines_en.pdf` |
| U2 | DRV8213DSGR | Texas Instruments | DRV8213 datasheet SLVSGV9, initial release (Aug 2023) | [ti.com](https://www.ti.com/lit/ds/symlink/drv8213.pdf) | `DRV8213_datasheet_en.pdf` |
| U3 | AP2112K-3.3TRG1 | Diodes Inc. | AP2112 datasheet DS39724 Rev. 2-2 (Jun 2017) | [diodes.com](https://www.diodes.com/assets/Datasheets/AP2112.pdf) | `AP2112_datasheet_en.pdf` |
| U4 | LIS2DH12TR | ST | LIS2DH12 datasheet DocID025056 Rev 6 (May 2017); st.com blocked the automatic download | [LCSC C110926](https://datasheet.lcsc.com/datasheet/pdf/80fd3cb5c04ce9b30e9bec7b53c4a455.pdf) (official: [st.com](https://www.st.com/resource/en/datasheet/lis2dh12.pdf)) | `LIS2DH12_datasheet_LCSC.pdf` |
| U5, U102 | USBLC6-2SC6 | ST | USBLC6-2 datasheet Doc ID 11265 Rev 5 (Oct 2011); newer ST revisions exist, st.com blocked the download | [LCSC C7519](https://datasheet.lcsc.com/datasheet/pdf/0d3a2ab954b34651a0695e7ccf534db0.pdf) (official: [st.com](https://www.st.com/resource/en/datasheet/usblc6-2.pdf)) | `USBLC6-2SC6_datasheet_LCSC.pdf` |
| U6 | TPS22918DBVR | Texas Instruments | TPS22918 datasheet SLVSD76C (rev. Jul 2017) | [ti.com](https://www.ti.com/lit/ds/symlink/tps22918.pdf) | `TPS22918_datasheet.pdf` |
| J4, J101 | TYPE-C-31-M-12 | Korean Hroparts (HRO) | Drawing TYPE-C-31-M-12 Rev A (2020-12-08), 1 sheet; no official manufacturer site | [LCSC C165948](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf) | `HRO_TYPE-C-31-M-12_datasheet_LCSC.pdf` |
| Q1, Q101 | AO3401A | Alpha & Omega | AO3401A datasheet Rev 3.1 (Dec 2023) | [aosmd.com](https://www.aosmd.com/res/datasheets/AO3401A.pdf) | `AO3401A_datasheet_en.pdf` |
| D2 | SS34F | MDD | SS32F–SS3200F (SMAF) Rev 2024A3 | [LCSC C60396](https://datasheet.lcsc.com/datasheet/pdf/a8b6fbedb99ae95b57cbc8bd1dad1a3d.pdf) | `MDD_SS34F_datasheet_LCSC.pdf` |
| D1 | green LED 0402 (generic) | – | **Representative only:** NATIONSTAR NCD0402G1 (LCSC C130723), no revision printed. D1 has no fixed part number | [LCSC](https://datasheet.lcsc.com/datasheet/pdf/3ef27e1d06d585dc1d40cc88a660fdcb.pdf) | `NATIONSTAR_NCD0402G1_datasheet_LCSC_representative.pdf` |
| F1 | BSMD0805-050-6V | BHFUSE | BSMD0805 Series approval sheet, revision 2025 | [LCSC C883108](https://datasheet.lcsc.com/datasheet/pdf/37ba15b8f21d7cb6355030343da3669a.pdf) | `BSMD0805-050-6V_datasheet.pdf` |

### Added 2026-11-09 (power path for VSYS up to 6.6 V, main checkout)

| Ref | Part | Manufacturer | Document, revision | URL | File |
|---|---|---|---|---|---|
| U3, U6 | SPX3819M5-L-3-3 (C9055), SPX3819M5-L-5-0 (C13417) | MaxLinear | SPX3819 500 mA Low-Noise LDO, Rev 2.0.5 (Dec 2019); the LCSC copy is the older Rev 2.0.2 with misaligned EN/limit rows | [maxlinear.com](https://www.maxlinear.com/ds/spx3819.pdf) | `SPX3819_datasheet_en.pdf` |
| F1 (candidate) | SMD0805-050-16V (C2833485) | TECHFUSE | approval sheet (2013) | [LCSC](https://datasheet.lcsc.com/datasheet/pdf/f5237ed89b0fc8241b445f57de0422a2.pdf) | `TECHFUSE_SMD0805-050-16V_datasheet_LCSC.pdf` |
| F1 (candidate) | SMD0805-050C-16V (C2760262) | BNstar | Version 1.0 (2018-12-27) | [LCSC](https://datasheet.lcsc.com/datasheet/pdf/0968bf8022715ab846303180c68ce292.pdf) | `BNstar_SMD0805-050C-16V_datasheet_LCSC.pdf` |
| F1 (candidate) | SMD0805-050-16 (C46640986) | Zhuhai Hongjiacheng (R+O) | SMD0805 series Rev 1.2 | [LCSC](https://datasheet.lcsc.com/datasheet/pdf/828ea1364ab569d31fa1abd643133b81.pdf) | `RO_SMD0805-050-16_datasheet_LCSC.pdf` |

The AP2112K, TPS22918 and BSMD0805-050-6V rows above describe the state at commit `32a3535` and are superseded by
these parts on the main board.

### Added 2026-11-11 (rev B: buck trial, then the LDO TPS7A2633 for U3)

| Ref | Part | Manufacturer | Document, revision | URL | File |
|---|---|---|---|---|---|
| U3 | TPS62162DSGR (C40256); TPS62160DSGR (C324077) as adjustable fallback | Texas Instruments | TPS62160/1/2/3 datasheet SLVSAM2E (Rev. E, May 2017; DSG land pattern 4218900/E 08/2022) | [ti.com](https://www.ti.com/lit/ds/symlink/tps62160.pdf) | `TPS6216x_datasheet_en.pdf` |
| L1 | DFE201612P-2R2M=P2 (C79317) | Murata | DFE201612P reference specification J(E)TE243A-0033-01, 9 pages (electrical values, recommended land pattern, notice on copper under the coil) | [LCSC](https://datasheet.lcsc.com/datasheet/pdf/3da72e1ea2c544751f1a10542ca0aaa4.pdf) (product page: [murata.com](https://www.murata.com/en-us/products/productdetail?partno=DFE201612P-2R2M%3DP2)) | `Murata_DFE201612P-2R2M_datasheet_LCSC.pdf` |
| U3 (current) | TPS7A2633DRVR (C2876256); TPS7A2601DRVR (C2859671) as adjustable second source | Texas Instruments | TPS7A26 datasheet SBVS290B (Rev. B, Oct 2019; DRV0006A land pattern 4222173/C 11/2025) | [ti.com](https://www.ti.com/lit/ds/symlink/tps7a26.pdf) | `TPS7A26_datasheet_en.pdf` |
| – (alternative) | TPS62840DLCR (C2071859) | Texas Instruments | TPS6284x datasheet SLVSEC6D (Rev. D, Mar 2020) | [ti.com](https://www.ti.com/lit/ds/symlink/tps62840.pdf) | `TPS6284x_datasheet_en.pdf` |

The TPS6216x and DFE201612P rows describe the buck trial of rev B (review: [wiring-review.md](wiring-review.md)
section 8); the TPS7A26 is the current U3 (review: section 9). Comparison: [proposal-supply-standby.md](proposal-supply-standby.md).

From rev B on, the SPX3819 row above applies to U6 (LED LDO, DNP) only; in rev A (tag `rev-a-spx3819`) it is also U3.

## Charger board

U102 (USBLC6-2SC6), J101 (TYPE-C-31-M-12) and Q101 (AO3401A) use the same documents as the main board.

| Ref | Part | Manufacturer | Document, revision | URL | File |
|---|---|---|---|---|---|
| U101 | MCP73831T-2ACI/OT | Microchip | MCP73831/2 data sheet DS20001984H (Jun 2020) | [microchip.com](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf) | `MCP73831_datasheet_en.pdf` |
| D102 | SS34 | MDD | SS32–SS3200 (SMA) Rev 2024A5 | [LCSC C8678](https://datasheet.lcsc.com/datasheet/pdf/dfa1ff67dea875d0135103ba9ada713a.pdf) | `MDD_SS34_datasheet_LCSC.pdf` |
| D101 | KT-0603R | Hubei KENTO | Specification for approval 0603 red, A.0 (2018-12-06) | [LCSC C2286](https://datasheet.lcsc.com/datasheet/pdf/011ec3e8cb1e825f6961d29bc4db4c7a.pdf) | `KENTO_KT-0603R_datasheet_LCSC.pdf` |
| J102 | S2B-PH-SM4-TB | JST | PH connector catalog ePH.pdf (current web version, no revision printed) | [jst-mfg.com](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) | `JST_PH_catalog_en.pdf` |
| J102 | S2B-PH-SM4-TB | JST | older PH catalog pages (cross-check only) | [LCSC C295747](https://datasheet.lcsc.com/datasheet/pdf/2474e9261ed7c5f86b55d373e724589d.pdf) | `JST_S2B-PH-SM4-TB_datasheet_LCSC.pdf` |

## Not covered

Passive parts (resistors, capacitors) are generic and have no individual datasheet here; their voltage ratings
were checked against parts.csv only.
