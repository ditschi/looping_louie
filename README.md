# Looping Louie WLAN-Upgrade

Nachrüst-Elektronik für Looping Louie (alt und neu) und Loopin' Chewie: wird **ohne Löten ins
Batteriefach** gesteckt und macht das Spiel per **Web-UI vom Handy** steuerbar, mit
Spielmodi, eigenen Modi, Spielleiter- und Spielerrollen. Der Original-Hebel bleibt Start/Stopp.

> Status: Neustart (Branch `v2`). Konzept steht, Hardware im Entwurf, Firmware folgt.
> Der alte MicroPython/ESP8266-Stand liegt im Tag `v1-legacy`.

## Aufbau

| Baugruppe | Beschreibung |
|---|---|
| **Hauptplatine** | Im Format einer AA-Zelle: ESP32-C3, H-Brücke DRV8833, Hebel-Erkennung |
| **Brücke** | AA-Dummy aus Kupfer für das zweite Fach (neues Louie, Chewie) |
| **Ladeplatine** | Extern beim Akku: USB-C (Laden + Flashen), Laderegler, LiPo-Anschluss |
| **C-Hülse** | 3D-Druck-Adapter, damit die Hauptplatine ins Baby-Fach des alten Louie passt |

Details: [docs/hardware-konzept.md](docs/hardware-konzept.md)

## Verzeichnisse

```
docs/                 Konzept und Entwicklungsanleitung
hardware/
  bom/teile.csv       Stückliste mit Herstellerteilen, LCSC-Nummern, Alternativen
  lib/                Projektbibliothek (Symbole, Footprints, 3D) – erzeugt mit just parts
  main-board/         KiCad-Projekt Hauptplatine
  scripts/            Hilfsskripte (Umriss, Teile holen, Werkzeugprüfung)
justfile              alle Entwicklungsbefehle (just --list)
setup.sh              installiert alle Werkzeuge
```

## Schnellstart

```bash
./setup.sh     # alle Werkzeuge installieren (einmalig, Ubuntu/Debian)
just check     # Werkzeuge prüfen
just --list    # alle Befehle
```

Einrichtung und Arbeitsweise: [docs/entwicklung.md](docs/entwicklung.md)
