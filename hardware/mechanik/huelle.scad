// Looping Louie WLAN-Upgrade – Hülle für die Hauptplatine
//
// AA-Einsatz:  Schale (unter der Platine) + 2 Endkappen, gesteckt mit Dübeln aus 1,75-mm-Filament.
// C-Adapter:   dicke Hülse, in die der fertige AA-Einsatz geschoben wird (wie ein AA→C-Adapter).
//
// Alle Teile drucken ohne Stützmaterial:
//   - Schale und C-Hülse stehen aufrecht und haben über die ganze Länge denselben Querschnitt.
//   - Kappen liegen mit der Innenseite auf dem Bett; der Platinenschlitz wird nur 1,2 mm weit überbrückt.
//
// Koordinaten (Baugruppe): x = Zellachse, Platinenmitte im Ursprung, z = Normale der Bestückungsseite.
// Platinenmaße siehe hardware/scripts/board_outline.py, Bauteillage aus hardware/main-board/louie-main.kicad_pcb.
//
// Export: just stl   (oder: openscad -D 'teil="aa_schale"' -o schale.stl huelle.scad)

/* [Auswahl] */
// baugruppe = Ansicht mit Platinen-Dummy; druck_* = Teile in Druckausrichtung
teil = "baugruppe"; // [baugruppe, baugruppe_c, explosion, kollision, druck_aa_schale, druck_kappe_plus, druck_kappe_minus, druck_c_huelse, druck_alle]

/* [Zelle] */
aa_d = 14.5;        // Durchmesser AA (IEC max.)
aa_l = 50.5;        // Länge AA inkl. Pluspol
c_d = 25.8;         // Außendurchmesser C-Adapter (C-Zelle max. 26,2)
c_l = 47.5;         // Länge C-Hülse; kürzer als der AA-Einsatz, damit die Kappen an den Kontakten anliegen
plus_nippel = true; // Pluspol-Nippel an der Plus-Kappe (falls das Fach Verpolschutz-Rippen hat)
nippel_d = 5.5;
nippel_h = 1.0;

/* [Platine] */
pcb_l = 46.0;
pcb_w = 13.5;
pcb_t = 0.8;
pcb_top = 0.5;      // Oberseite über der Achse (siehe hardware-konzept.md 4.1)

/* [Konstruktion] */
spiel = 0.2;            // Passungsspiel
ueberdeckung = 0.8;     // so weit greift die Platine an jedem Ende in die Kappe
fach_b = 10.4;          // Tasche unter der Platine für Lötpads, Lötzinn und Kabel
fach_tiefe = 2.0;
duebel_d = 1.75;        // Filamentstück als Dübel
duebel_loch = 1.95;
duebel_y = 2.8;
duebel_z = -4.6;
duebel_tiefe = 4.0;     // Lochtiefe in der Schale
band_b = 4.0;           // Nickelband für die Endkontakte (4 × 0,15 mm)
band_schlitz_t = 0.45;
kabel_x = 14.5;         // Mitte der Kabel-Lötpads J1 und der Akku-Pads J5 (Unterseite, unter der USB-C-Buchse)
kabel_l = 9.0;          // Länge des Kabelfensters (J1: x = 10,7 … 18,3)
kabel_seite = 1;        // Kabelfenster auf +y (Seite der USB-C-Öffnung; -1 = -y)
c_schlitz = 3.0;        // Längsschlitz der C-Hülse (Kabel, Klemmwirkung)

$fn = 96;

// abgeleitet
r = aa_d / 2;
pcb_bot = pcb_top - pcb_t;
kappe_innen = pcb_l / 2 - ueberdeckung;   // x der Kappen-Innenfläche
schale_l = 2 * kappe_innen;
kappe_l = aa_l / 2 - kappe_innen;         // Kappe inkl. Nippel
eps = 0.01;

// ---------- Schale ----------

module schale_profil() {
    difference() {
        intersection() {
            circle(r = r);
            translate([-r, -r]) square([2 * r, r + pcb_bot]);
        }
        translate([-fach_b / 2, pcb_bot - fach_tiefe]) square([fach_b, fach_tiefe + 1]);
    }
}

// Profil (y, z) entlang x extrudieren
module entlang_x(l) {
    multmatrix([[0, 0, 1, -l / 2], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = l) children();
}

module duebel_loecher(tiefe) {
    for (s = [-1, 1]) translate([0, s * duebel_y, duebel_z])
        rotate([0, 90, 0]) cylinder(d = duebel_loch, h = 2 * tiefe, center = true, $fn = 24);
}

module aa_schale() {
    difference() {
        entlang_x(schale_l) schale_profil();
        for (x = [-1, 1]) translate([x * kappe_innen, 0, 0]) duebel_loecher(duebel_tiefe);
        // Kabelfenster seitlich auf Taschenhöhe; oben im Druck nur 2 mm Brücke
        translate([kabel_x - kabel_l / 2, kabel_seite > 0 ? 0 : -r - 1, pcb_bot - fach_tiefe])
            cube([kabel_l, r + 1, fach_tiefe + eps]);
    }
}

// ---------- Kappen ----------

// Kappe am +x-Ende; die Minus-Kappe ist dieselbe Form gedreht (symmetrisch in y)
module kappe(nippel) {
    koerper = kappe_l - (nippel ? nippel_h : 0);
    difference() {
        union() {
            translate([kappe_innen, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = koerper);
            if (nippel)
                translate([kappe_innen + koerper - eps, 0, 0]) rotate([0, 90, 0])
                    cylinder(d = nippel_d, h = nippel_h + eps);
        }
        // Platinenschlitz, blind: legt die Platine in Länge, Breite und Höhe fest
        translate([kappe_innen - 1, -(pcb_w / 2 + spiel), pcb_bot - spiel])
            cube([1 + ueberdeckung + spiel, pcb_w + 2 * spiel, pcb_t + 2 * spiel]);
        // Nickelband: unter der Platine durch die Kappe nach außen
        translate([kappe_innen - 1, -(band_b / 2 + spiel), pcb_bot - band_schlitz_t])
            cube([kappe_l + 2, band_b + 2 * spiel, band_schlitz_t + eps]);
        // Dübellöcher, blind
        translate([kappe_innen, 0, 0]) duebel_loecher(min(duebel_tiefe, koerper - 0.6));
    }
}

// ---------- C-Hülse ----------

module c_huelse_profil() {
    difference() {
        circle(d = c_d);
        circle(d = aa_d + 2 * spiel);
        translate([-c_schlitz / 2, 0]) square([c_schlitz, c_d]);
    }
}

module c_huelse() {
    entlang_x(c_l) c_huelse_profil();
}

// ---------- Platinen-Dummy (nur Ansicht/Kollisionsprüfung) ----------
// Stand C6 (docs/hauptplatine-c6.md). Genauer: teil = "kollision" mit dem 3D-Export der Platine
// (just modell -> build/main-board/3d/louie-main.stl).
platine_stl = "../../build/main-board/3d/louie-main.stl";
kollision_stl = false;

module bauteil(x0, x1, y0, y1, h) {
    translate([x0, y0, pcb_top]) cube([x1 - x0, y1 - y0, h]);
}

module platine_dummy() {
    color("darkgreen") translate([-pcb_l / 2, -pcb_w / 2, pcb_bot]) cube([pcb_l, pcb_w, pcb_t]);
    color("silver") bauteil(-19.9, -3.3, -6.6, 6.6, 2.55);        // ESP32-C6-MINI-1
    color("dimgray") {
        bauteil(-0.3, 1.7, -5.6, -3.6, 0.8);                      // DRV8213 (WSON-8)
        bauteil(3.85, 7.05, -3.5, -1.9, 1.8);                     // C1 (1206)
        bauteil(3.85, 7.05, -1.1, 0.5, 1.8);                      // C2 (1206)
        bauteil(5.15, 8.65, -6.55, -3.95, 1.1);                   // D2 (SMAF)
        bauteil(0.9, 3.8, 4.0, 5.6, 1.45);                        // AP2112K
        bauteil(6.15, 9.05, 4.2, 5.5, 1.1);                       // AO3401A
        bauteil(14.35, 17.25, -5.65, -4.05, 1.45);                // USBLC6-2SC6
        bauteil(19.75, 21.75, -6.3, -4.3, 1.0);                   // LIS2DH12 (optional)
    }
    color("lightgray") bauteil(10.83, 19.77, -1.3, 6.1, 3.26);    // USB-C HRO TYPE-C-31-M-12
    // Kontaktbänder und Kabel unten
    color("gold") for (s = [-1, 1])
        translate([s > 0 ? 19.9 : -aa_l / 2, -band_b / 2, pcb_bot - 0.15]) cube([aa_l / 2 - 19.9, band_b, 0.15]);
}

// ---------- Ausgabe ----------

module aa_einsatz() {
    color("orange", 0.8) aa_schale();
    color("orange", 0.8) kappe(plus_nippel);
    color("orange", 0.8) rotate([0, 0, 180]) kappe(false);
}

module druck_schale()      rotate([0, -90, 0]) translate([kappe_innen, 0, 0]) aa_schale();
module druck_kappe(nippel) rotate([0, -90, 0]) translate([-kappe_innen, 0, 0]) kappe(nippel);
module druck_c_huelse()    rotate([0, -90, 0]) translate([c_l / 2, 0, 0]) c_huelse();

if (teil == "baugruppe") {
    aa_einsatz();
    platine_dummy();
} else if (teil == "baugruppe_c") {
    // AA-Einsatz um 90° gedreht, Kabelfenster zeigt in den Schlitz der Hülse
    rotate([90 * kabel_seite, 0, 0]) { aa_einsatz(); platine_dummy(); }
    color("steelblue", 0.5) c_huelse();
} else if (teil == "explosion") {
    // Teile auseinandergezogen, Dübel (Filamentstücke) rot
    a = 8;
    color("orange", 0.8) aa_schale();
    translate([0, 0, 6]) platine_dummy();
    color("orange", 0.8) translate([a, 0, 0]) kappe(plus_nippel);
    color("orange", 0.8) translate([-a, 0, 0]) rotate([0, 0, 180]) kappe(false);
    color("red") for (x = [-1, 1], s = [-1, 1])
        translate([x * (kappe_innen + a / 2), s * duebel_y, duebel_z])
            rotate([0, 90, 0]) cylinder(d = duebel_d, h = duebel_tiefe + 2, center = true, $fn = 24);
} else if (teil == "kollision") {
    // Was aus der AA-Hüllkurve ragt (leeres Ergebnis = keine Kollision). Mit kollision_stl = true wird statt
    // des Dummys der 3D-Export der Platine geprüft (braucht OpenSCAD >= 2023 mit Manifold; CGAL in 2021.01
    // scheitert an der KiCad-STL). Rechnerische Prüfung: docs/hauptplatine-c6.md, Ergebnis Umbau.
    difference() {
        if (kollision_stl) translate([0, 0, pcb_bot]) mirror([0, 1, 0]) translate([-100, 75, 0]) import(platine_stl);
        else platine_dummy();
        rotate([0, 90, 0]) cylinder(r = r, h = aa_l + 2, center = true);
    }
} else if (teil == "druck_aa_schale") druck_schale();
else if (teil == "druck_kappe_plus") druck_kappe(plus_nippel);
else if (teil == "druck_kappe_minus") druck_kappe(false);
else if (teil == "druck_c_huelse") druck_c_huelse();
else if (teil == "druck_alle") {
    druck_schale();
    translate([18, 0, 0]) druck_kappe(plus_nippel);
    translate([36, 0, 0]) druck_kappe(false);
    translate([0, 30, 0]) druck_c_huelse();
}
