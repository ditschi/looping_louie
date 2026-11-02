// Looping Louie WLAN-Upgrade – Halter für die Ladeplatine
//
// Variante AA-Fach (zweites Fach statt Brückenplatine):
//   Die Ladeplatine steht HOCHKANT in der AA-Form, die USB-C-Buchse an der Längskante zeigt nach oben
//   aus dem Fach. Schale (Kreissegment hinter der Platine) + 2 Endkappen, gesteckt mit Dübeln aus
//   1,75-mm-Filament – gleiches Prinzip wie der Einsatz der Hauptplatine (huelle.scad).
//   Die Endkappen führen die Nickelbänder der Brücke (BT101/BT102) zu den Fachkontakten.
// Variante Basis:
//   Flacher Halter (Wanne mit Schraublaschen), wird mit der Steckkante an die Innenwand der Basis
//   geklebt oder geschraubt. In die Wand kommt ein Loch für den USB-C-Stecker (Maße: siehe Echo).
//
// Koordinaten (Baugruppe AA): x = Zellachse, Platinenmitte im Ursprung, z = nach oben (Steckrichtung),
// Bestückungsseite zeigt nach +y. Platinenmaße siehe hardware/scripts/gen_charger_pcb.py.
//
// Export: just stl

/* [Auswahl] */
teil = "baugruppe"; // [baugruppe, baugruppe_basis, explosion, druck_schale, druck_kappe_plus, druck_kappe_minus, druck_basis_halter, druck_alle]

/* [Zelle] */
aa_d = 14.5;
aa_l = 50.5;
plus_nippel = true;
nippel_d = 5.5;
nippel_h = 1.0;

/* [Platine] */
pcb_l = 46.0;
pcb_h = 12.5;       // Platinenbreite, im Fach senkrecht
pcb_t = 1.6;
pcb_rueck = -3.2;   // y der Rückseite (Lötseite ohne Bauteile); Vorderseite bei pcb_rueck + pcb_t
usb_x = -15.0;      // Mitte der USB-C-Buchse (gen_charger_pcb.py: USB_X)
jst_x = 10.5;       // Mitte des JST-PH-Steckers
led_x = -7.0;       // Ladeanzeige an der Oberkante

/* [Konstruktion] */
spiel = 0.2;
ueberdeckung = 0.8;     // so weit greift die Platine an jedem Ende in die Kappe
tasche_tiefe = 0.6;     // Vertiefung in der Schale für Lötzinn/Vias auf der Rückseite
rand = 1.2;             // Auflagestege oben/unten
duebel_d = 1.75;
duebel_loch = 1.95;
duebel_z = 2.6;         // Dübel bei z = ±duebel_z
duebel_y = -5.3;
duebel_tiefe = 4.0;
band_b = 4.0;           // Nickelband 4 × 0,15 mm
band_schlitz_t = 0.45;

/* [Basis-Halter] */
boden = 1.2;            // Boden unter der Platine
wand = 1.6;             // Seitenwände
stecker_b = 13.5;       // Loch in der Basiswand für den Stecker-Umspritzling (USB-C max. ca. 12,4 × 6,5)
stecker_h = 7.5;
lasche_loch = 2.2;      // für M2 oder 2,2-mm-Blechschraube

$fn = 96;

// abgeleitet
r = aa_d / 2;
pcb_vorn = pcb_rueck + pcb_t;
kappe_innen = pcb_l / 2 - ueberdeckung;
schale_l = 2 * kappe_innen;
kappe_l = aa_l / 2 - kappe_innen;
eps = 0.01;

assert(pcb_rueck * pcb_rueck + (pcb_h / 2) * (pcb_h / 2) < r * r, "Platinenecken ragen aus der AA-Form");

// ---------- AA-Variante: Schale ----------

module schale_profil() {      // (y, z)
    difference() {
        intersection() {
            circle(r = r);
            translate([-r, -r]) square([r + pcb_rueck, 2 * r]);
        }
        // Tasche hinter der Platine, Auflage nur auf den Stegen oben und unten
        translate([pcb_rueck - tasche_tiefe, -(pcb_h / 2 - rand)]) square([tasche_tiefe + eps, pcb_h - 2 * rand]);
    }
}

// Profil (y, z) entlang x extrudieren
module entlang_x(l) {
    multmatrix([[0, 0, 1, -l / 2], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = l) children();
}

module duebel_loecher(tiefe) {
    for (s = [-1, 1]) translate([0, duebel_y, s * duebel_z])
        rotate([0, 90, 0]) cylinder(d = duebel_loch, h = 2 * tiefe, center = true, $fn = 24);
}

module schale() {
    difference() {
        entlang_x(schale_l) schale_profil();
        for (x = [-1, 1]) translate([x * kappe_innen, 0, 0]) duebel_loecher(duebel_tiefe);
    }
}

// ---------- AA-Variante: Kappen ----------

module kappe(nippel) {          // am +x-Ende; Minus-Kappe = um z gedreht
    koerper = kappe_l - (nippel ? nippel_h : 0);
    difference() {
        union() {
            translate([kappe_innen, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = koerper);
            if (nippel)
                translate([kappe_innen + koerper - eps, 0, 0]) rotate([0, 90, 0])
                    cylinder(d = nippel_d, h = nippel_h + eps);
        }
        // senkrechter Platinenschlitz, blind
        translate([kappe_innen - 1, pcb_rueck - spiel, -(pcb_h / 2 + spiel)])
            cube([1 + ueberdeckung + spiel, pcb_t + 2 * spiel, pcb_h + 2 * spiel]);
        // Nickelband: hinter der Platine (Pad BT10x auf der Rückseite) durch die Kappe nach außen
        translate([kappe_innen - 1, pcb_rueck - band_schlitz_t, -(band_b / 2 + spiel)])
            cube([kappe_l + 2, band_schlitz_t + eps, band_b + 2 * spiel]);
        translate([kappe_innen, 0, 0]) duebel_loecher(min(duebel_tiefe, koerper - 0.6));
    }
}

// ---------- Basis-Variante: flacher Halter ----------
// Koordinaten: Platine liegt flach, Bestückung oben, Steckkante bei y = 0 (bündig mit der Halter-Vorderkante),
// Platine reicht nach -y.

halter_l = pcb_l + 2 * (wand + spiel);
halter_b = pcb_h + spiel + wand;
halter_h = boden + pcb_t + 0.6;     // Wände 0,6 mm über der Platine: halten sie seitlich, ohne Bauteile zu berühren

module basis_halter() {
    difference() {
        union() {
            translate([-halter_l / 2, -halter_b, 0]) cube([halter_l, halter_b, halter_h]);
            // Schraub-/Klebelaschen an den Enden
            for (s = [-1, 1]) hull() {
                translate([s * (halter_l / 2 - 1), -halter_b, 0]) cube([2, halter_b, boden], center = false);
                translate([s * (halter_l / 2 + 3), -halter_b / 2, 0]) cylinder(d = 6, h = boden, $fn = 40);
            }
        }
        // Platinenmulde, nach vorn (Steckkante) offen
        translate([-pcb_l / 2 - spiel, -pcb_h - spiel, boden]) cube([pcb_l + 2 * spiel, pcb_h + spiel + 1, halter_h]);
        // Lötpads/Nickelband unten: flache Tasche
        translate([-(pcb_l / 2 - 3), -(pcb_h - rand), boden - tasche_tiefe])
            cube([pcb_l - 6, pcb_h - 2 * rand, tasche_tiefe + eps]);
        for (s = [-1, 1]) translate([s * (halter_l / 2 + 3), -halter_b / 2, -1])
            cylinder(d = lasche_loch, h = boden + 2, $fn = 24);
    }
}

// Wandloch in der Basis (nur Ansicht): Mitte auf Höhe der Buchsenöffnung
usb_mitte_z = boden + pcb_t + 1.63;
echo(str("Basis: Loch ", stecker_b, " x ", stecker_h, " mm in die Wand, Mitte ", usb_mitte_z,
         " mm über der Auflagefläche des Halters; Lochmitte ", halter_l / 2 + usb_x,
         " mm vom linken Halterende (von innen auf die Wand gesehen)"));

// ---------- Platinen-Dummy (nur Ansicht) ----------

module bauteil_v(x0, x1, z0, z1, h) {   // Bauteil auf der Vorderseite der hochkant stehenden Platine
    translate([x0, pcb_vorn, z0]) cube([x1 - x0, h, z1 - z0]);
}

// Blick auf die Bestückungsseite (von +y) mit der Steckkante oben: rechts ist -x. Deshalb ist
// x im Dummy gegenüber KiCad gespiegelt (x_dummy = -x_KiCad), sonst wäre die Platine seitenverkehrt.
module platine_dummy() {        // hochkant, Koordinaten wie AA-Baugruppe
    color("darkgreen") translate([-pcb_l / 2, pcb_rueck, -pcb_h / 2]) cube([pcb_l, pcb_t, pcb_h]);
    color("silver") bauteil_v(-usb_x - 4.47, -usb_x + 4.47, -1.1, pcb_h / 2, 3.26);   // USB-C
    color("ivory") bauteil_v(-jst_x - 3.95, -jst_x + 3.95, -3.45, pcb_h / 2 - 0.2, 4.7);  // JST-PH
    color("dimgray") {
        bauteil_v(2.6, 8.2, -5.6, -3.0, 2.3);      // D102 SMA
        bauteil_v(2.6, 4.6, -0.2, 2.6, 1.1);       // U101
        bauteil_v(13.5, 16.5, -6.0, -3.0, 1.1);    // U102
    }
    color("red") bauteil_v(-led_x - 0.8, -led_x + 0.8, 4.8, 5.6, 0.6);
    color("gold") for (s = [-1, 1])     // Nickelbänder der Brücke
        translate([s > 0 ? 20.4 : -aa_l / 2, pcb_rueck - 0.15, -band_b / 2]) cube([aa_l / 2 - 20.4, 0.15, band_b]);
}

module aa_einsatz() {
    color("orange", 0.8) schale();
    color("orange", 0.8) kappe(plus_nippel);
    color("orange", 0.8) rotate([0, 0, 180]) kappe(false);
}

module druck_schale()      rotate([0, -90, 0]) translate([kappe_innen, 0, 0]) schale();
module druck_kappe(nippel) rotate([0, -90, 0]) translate([-kappe_innen, 0, 0]) kappe(nippel);

if (teil == "baugruppe") {
    aa_einsatz();
    platine_dummy();
    // USB-C-Stecker von oben (Umriss des Umspritzlings)
    color("black", 0.4) translate([-usb_x - 6.2, pcb_vorn + 1.63 - 3.25, pcb_h / 2 + 1]) cube([12.4, 6.5, 12]);
} else if (teil == "baugruppe_basis") {
    color("orange", 0.8) basis_halter();
    // Platine flach eingelegt: Hochkant-Dummy um x drehen, Steckkante nach y = 0
    translate([0, 0, boden - pcb_rueck]) rotate([0, 0, 180]) translate([0, pcb_h / 2, 0]) rotate([90, 0, 0]) platine_dummy();
    // Basiswand mit Loch (Ansicht)
    color("lightblue", 0.4) difference() {
        translate([-35, 0, -2]) cube([70, 2, 20]);
        translate([usb_x - stecker_b / 2, -1, usb_mitte_z - stecker_h / 2]) cube([stecker_b, 4, stecker_h]);
    }
} else if (teil == "explosion") {
    a = 8;
    color("orange", 0.8) schale();
    translate([0, 6, 0]) platine_dummy();
    color("orange", 0.8) translate([a, 0, 0]) kappe(plus_nippel);
    color("orange", 0.8) translate([-a, 0, 0]) rotate([0, 0, 180]) kappe(false);
    color("red") for (x = [-1, 1], s = [-1, 1])
        translate([x * (kappe_innen + a / 2), duebel_y, s * duebel_z])
            rotate([0, 90, 0]) cylinder(d = duebel_d, h = duebel_tiefe + 2, center = true, $fn = 24);
} else if (teil == "druck_schale") druck_schale();
else if (teil == "druck_kappe_plus") druck_kappe(plus_nippel);
else if (teil == "druck_kappe_minus") druck_kappe(false);
else if (teil == "druck_basis_halter") basis_halter();
else if (teil == "druck_alle") {
    druck_schale();
    translate([18, 0, 0]) druck_kappe(plus_nippel);
    translate([36, 0, 0]) druck_kappe(false);
    translate([0, 40, 0]) basis_halter();
}
