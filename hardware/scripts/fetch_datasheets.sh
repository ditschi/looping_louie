#!/usr/bin/env bash
# Download the datasheets listed in docs/datasheets.md into datasheets/ (gitignored, copyrighted).
# Usage: just datasheets [force=1]   – existing files are kept unless FORCE=1.
set -u
cd "$(dirname "$0")/../.."
mkdir -p datasheets
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
fail=0
while read -r file url; do
    [ -z "$file" ] && continue
    out="datasheets/$file"
    if [ -s "$out" ] && [ "${FORCE:-0}" != "1" ]; then echo "keep  $file"; continue; fi
    if curl -fsSL -A "$UA" --retry 2 -o "$out.part" "$url" && pdfinfo "$out.part" >/dev/null 2>&1; then
        mv "$out.part" "$out"; echo "ok    $file"
    else
        rm -f "$out.part"; echo "FAIL  $file  ($url)"; fail=1
    fi
done <<'LIST'
ESP32-C6-MINI-1_datasheet_en.pdf https://www.espressif.com/sites/default/files/documentation/esp32-c6-mini-1_mini-1u_datasheet_en.pdf
ESP32-C6_datasheet_en.pdf https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf
ESP32-C6_hardware_design_guidelines_en.pdf https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/esp-hardware-design-guidelines-en-master-esp32c6.pdf
TPS22918_datasheet.pdf https://www.ti.com/lit/ds/symlink/tps22918.pdf
BSMD0805-050-6V_datasheet.pdf https://datasheet.lcsc.com/datasheet/pdf/37ba15b8f21d7cb6355030343da3669a.pdf
DRV8213_datasheet_en.pdf https://www.ti.com/lit/ds/symlink/drv8213.pdf
AP2112_datasheet_en.pdf https://www.diodes.com/assets/Datasheets/AP2112.pdf
LIS2DH12_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/80fd3cb5c04ce9b30e9bec7b53c4a455.pdf
AO3401A_datasheet_en.pdf https://www.aosmd.com/res/datasheets/AO3401A.pdf
USBLC6-2SC6_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/0d3a2ab954b34651a0695e7ccf534db0.pdf
HRO_TYPE-C-31-M-12_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf
MDD_SS34F_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/a8b6fbedb99ae95b57cbc8bd1dad1a3d.pdf
MDD_SS34_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/dfa1ff67dea875d0135103ba9ada713a.pdf
KENTO_KT-0603R_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/011ec3e8cb1e825f6961d29bc4db4c7a.pdf
NATIONSTAR_NCD0402G1_datasheet_LCSC_representative.pdf https://datasheet.lcsc.com/datasheet/pdf/3ef27e1d06d585dc1d40cc88a660fdcb.pdf
MCP73831_datasheet_en.pdf https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf
JST_PH_catalog_en.pdf https://www.jst-mfg.com/product/pdf/eng/ePH.pdf
JST_S2B-PH-SM4-TB_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/2474e9261ed7c5f86b55d373e724589d.pdf
SPX3819_datasheet_en.pdf https://www.maxlinear.com/ds/spx3819.pdf
TECHFUSE_SMD0805-050-16V_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/f5237ed89b0fc8241b445f57de0422a2.pdf
BNstar_SMD0805-050C-16V_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/0968bf8022715ab846303180c68ce292.pdf
RO_SMD0805-050-16_datasheet_LCSC.pdf https://datasheet.lcsc.com/datasheet/pdf/828ea1364ab569d31fa1abd643133b81.pdf
LIST
exit $fail
