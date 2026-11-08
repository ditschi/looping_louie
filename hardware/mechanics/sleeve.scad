// Looping Louie Wi-Fi retrofit - sleeve for the main board
//
// AA insert:   shell (under the board) + 2 end caps, joined with dowels made of 1.75 mm filament.
// C adapter:   thick sleeve that the finished AA insert slides into (like an AA-to-C adapter).
//
// All parts print without supports:
//   - The shell and the C sleeve stand upright and have the same cross-section over their whole length.
//   - The caps lie on their inner face; the board slot is only a 1.2 mm bridge.
//
// Coordinates (assembly): x = cell axis, board centre at the origin, z = normal of the component side.
// y as in KiCad (hardware/main-board/louie-main.kicad_pcb), +y = USB-C side.
// Board dimensions see hardware/scripts/board_outline.py, component positions from the KiCad board.
//
// Export: just stl   (or: openscad -D 'part="print_aa_shell"' -o aa_shell.stl sleeve.scad)

/* [Selection] */
// assembly = view with the board; print_* = parts in print orientation
part = "assembly"; // [assembly, assembly_c, exploded, collision, print_aa_shell, print_cap_plus, print_cap_minus, print_c_sleeve, print_all]
// Assembly views: real board (3D export, `just model`) instead of the dummy. Preview only (F5 / no --render).
board_stl = false;

/* [View] */
shell_alpha = 0.8;  // transparency of shell and caps in the views

/* [Cell] */
aa_d = 14.5;        // AA diameter (IEC max.)
aa_l = 50.5;        // AA length including the positive terminal
c_d = 25.8;         // outer diameter of the C adapter (C cell max. 26.2)
c_l = 47.5;         // length of the C sleeve; shorter than the AA insert so the caps touch the contacts
plus_nub = true;    // positive terminal nub on the plus cap (in case the compartment has reverse-polarity ribs)
nub_d = 5.5;
nub_h = 1.0;

/* [Board] */
pcb_l = 46.0;
pcb_w = 14.1;           // board width (hardware/scripts/board_outline.py)
pcb_tongue_w = 12.5;    // width of the board ends that engage in the caps (tongue, 0.8 mm long)
pcb_t = 0.8;
pcb_top = 0.5;          // top side above the axis (see docs/hardware-concept.md 4.1)

/* [Construction] */
clearance = 0.2;        // fit clearance
overlap = 0.8;          // how far the board engages in the cap at each end
pocket_w = 10.4;        // pocket under the board for solder pads, solder and wires
pocket_depth = 2.0;
dowel_d = 1.75;         // piece of filament as a dowel
dowel_hole = 1.95;
dowel_y = 2.8;
dowel_z = -4.6;
dowel_depth = 4.0;      // hole depth in the shell
strip_w = 4.0;          // nickel strip for the end contacts (4 x 0.15 mm)
strip_slot_t = 0.45;
cable_x = 14.5;         // centre of the wire pads J1 and the battery pads J5 (bottom side, under the USB-C socket)
cable_l = 9.0;          // length of the cable window (J1: x = 10.7 ... 18.3)
cable_side = 1;         // cable window on +y (side of the USB-C opening; -1 = -y)
c_slot = 3.0;           // lengthwise slot of the C sleeve (wires, clamping)

$fn = 96;

// derived
r = aa_d / 2;
pcb_bot = pcb_top - pcb_t;
cap_inner = pcb_l / 2 - overlap;   // x of the inner face of the caps
shell_l = 2 * cap_inner;
cap_l = aa_l / 2 - cap_inner;      // cap including nub
eps = 0.01;

// ---------- Shell ----------

module shell_profile() {
    difference() {
        intersection() {
            circle(r = r);
            translate([-r, -r]) square([2 * r, r + pcb_bot]);
        }
        translate([-pocket_w / 2, pcb_bot - pocket_depth]) square([pocket_w, pocket_depth + 1]);
    }
}

// extrude a (y, z) profile along x
module along_x(l) {
    multmatrix([[0, 0, 1, -l / 2], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = l) children();
}

module dowel_holes(depth) {
    for (s = [-1, 1]) translate([0, s * dowel_y, dowel_z])
        rotate([0, 90, 0]) cylinder(d = dowel_hole, h = 2 * depth, center = true, $fn = 24);
}

module aa_shell() {
    difference() {
        along_x(shell_l) shell_profile();
        for (x = [-1, 1]) translate([x * cap_inner, 0, 0]) dowel_holes(dowel_depth);
        // cable window in the side at pocket height; only a 2 mm bridge at the top when printing
        translate([cable_x - cable_l / 2, cable_side > 0 ? 0 : -r - 1, pcb_bot - pocket_depth])
            cube([cable_l, r + 1, pocket_depth + eps]);
    }
}

// ---------- Caps ----------

// cap at the +x end; the minus cap is the same shape rotated (symmetric in y)
module cap(nub) {
    body = cap_l - (nub ? nub_h : 0);
    difference() {
        union() {
            translate([cap_inner, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = body);
            if (nub)
                translate([cap_inner + body - eps, 0, 0]) rotate([0, 90, 0])
                    cylinder(d = nub_d, h = nub_h + eps);
        }
        // board slot, blind: locates the board in length, width and height
        translate([cap_inner - 1, -(pcb_tongue_w / 2 + clearance), pcb_bot - clearance])
            cube([1 + overlap + clearance, pcb_tongue_w + 2 * clearance, pcb_t + 2 * clearance]);
        // nickel strip: under the board through the cap to the outside
        translate([cap_inner - 1, -(strip_w / 2 + clearance), pcb_bot - strip_slot_t])
            cube([cap_l + 2, strip_w + 2 * clearance, strip_slot_t + eps]);
        // dowel holes, blind
        translate([cap_inner, 0, 0]) dowel_holes(min(dowel_depth, body - 0.6));
    }
}

// ---------- C sleeve ----------

module c_sleeve_profile() {
    difference() {
        circle(d = c_d);
        circle(d = aa_d + 2 * clearance);
        translate([-c_slot / 2, 0]) square([c_slot, c_d]);
    }
}

module c_sleeve() {
    along_x(c_l) c_sleeve_profile();
}

// ---------- Board dummy (view and collision check only) ----------
// C6 board (docs/main-board-c6.md). More accurate: board_stl = true or part = "collision" with the 3D export
// of the board (just model -> build/main-board/3d/louie-main.stl).
board_stl_path = "../../build/main-board/3d/louie-main.stl";
collision_stl = false;

module component(x0, x1, y0, y1, h) {       // on the top side
    translate([x0, y0, pcb_top]) cube([x1 - x0, y1 - y0, h]);
}

module component_bottom(x0, x1, y0, y1, h) {   // on the bottom side, hangs down into the pocket
    translate([x0, y0, pcb_bot - h]) cube([x1 - x0, y1 - y0, h]);
}

module board_dummy() {
    color("darkgreen") translate([-pcb_l / 2, -pcb_w / 2, pcb_bot]) cube([pcb_l, pcb_w, pcb_t]);
    color("silver") component(-19.9, -3.3, -6.6, 6.6, 2.55);        // ESP32-C6-MINI-1
    color("dimgray") {
        component(-0.3, 1.7, -5.6, -3.6, 0.8);                      // DRV8213 (WSON-8)
        component(3.85, 7.05, -3.5, -1.9, 1.8);                     // C1 (1206)
        component(3.85, 7.05, -1.1, 0.5, 1.8);                      // C2 (1206)
        component(4.09, 7.10, 1.55, 3.06, 1.25);                    // C9 (0805, 10 uF)
        component(5.15, 8.65, -6.55, -3.95, 1.1);                   // D2 (SMAF)
        component(0.9, 3.8, 4.0, 5.6, 1.45);                        // AP2112K
        component(6.15, 9.05, 4.2, 5.5, 1.1);                       // AO3401A
        component(14.35, 17.25, -5.65, -4.05, 1.45);                // USBLC6-2SC6
        component(19.75, 21.75, -6.3, -4.3, 1.0);                   // LIS2DH12 (optional)
    }
    color("lightgray") component(10.83, 19.77, -1.3, 6.1, 3.26);    // USB-C HRO TYPE-C-31-M-12
    // optional parts on the bottom (DNP by default), inside the 2.0 mm pocket
    color("dimgray") {
        component_bottom(0.40, 4.00, 0.25, 2.75, 1.45);             // U6 TPS22918 (SOT-23-6)
        component_bottom(5.50, 6.90, -2.92, -0.08, 1.0);            // F1 (0805 PTC fuse)
        component_bottom(13.25, 16.15, -2.78, -1.33, 1.35);         // C17 (0805, 10 uF)
    }
    // contact strips under the board
    color("gold") for (s = [-1, 1])
        translate([s > 0 ? 19.9 : -aa_l / 2, -strip_w / 2, pcb_bot - 0.15]) cube([aa_l / 2 - 19.9, strip_w, 0.15]);
}

// real board from the KiCad 3D export: STL board bottom at z = 0, centre at (100, -75), y mirrored
module board_real() {
    translate([0, 0, pcb_bot]) mirror([0, 1, 0]) translate([-100, 75, 0]) import(board_stl_path);
}

module board() {
    if (board_stl) color("forestgreen") board_real();
    else board_dummy();
}

// ---------- Output ----------

module aa_insert() {
    color("orange", shell_alpha) aa_shell();
    color("orange", shell_alpha) cap(plus_nub);
    color("orange", shell_alpha) rotate([0, 0, 180]) cap(false);
}

module print_shell()     rotate([0, -90, 0]) translate([cap_inner, 0, 0]) aa_shell();
module print_cap(nub)    rotate([0, -90, 0]) translate([-cap_inner, 0, 0]) cap(nub);
module print_c_sleeve()  rotate([0, -90, 0]) translate([c_l / 2, 0, 0]) c_sleeve();

if (part == "assembly") {
    aa_insert();
    board();
} else if (part == "assembly_c") {
    // AA insert rotated by 90 deg, the cable window faces the slot of the sleeve
    rotate([90 * cable_side, 0, 0]) { aa_insert(); board(); }
    color("steelblue", 0.5) c_sleeve();
} else if (part == "exploded") {
    // parts pulled apart, dowels (pieces of filament) in red
    a = 8;
    color("orange", shell_alpha) aa_shell();
    translate([0, 0, 6]) board();
    color("orange", shell_alpha) translate([a, 0, 0]) cap(plus_nub);
    color("orange", shell_alpha) translate([-a, 0, 0]) rotate([0, 0, 180]) cap(false);
    color("red") for (x = [-1, 1], s = [-1, 1])
        translate([x * (cap_inner + a / 2), s * dowel_y, dowel_z])
            rotate([0, 90, 0]) cylinder(d = dowel_d, h = dowel_depth + 2, center = true, $fn = 24);
} else if (part == "collision") {
    // What sticks out of the AA envelope (empty result = no collision). With collision_stl = true the 3D export
    // of the board is checked instead of the dummy (needs OpenSCAD >= 2023 with Manifold; CGAL in 2021.01
    // fails on the KiCad STL). Numerical check: docs/main-board-c6.md, result of the redesign.
    difference() {
        if (collision_stl) board_real();
        else board_dummy();
        rotate([0, 90, 0]) cylinder(r = r, h = aa_l + 2, center = true);
    }
} else if (part == "print_aa_shell") print_shell();
else if (part == "print_cap_plus") print_cap(plus_nub);
else if (part == "print_cap_minus") print_cap(false);
else if (part == "print_c_sleeve") print_c_sleeve();
else if (part == "print_all") {
    print_shell();
    translate([18, 0, 0]) print_cap(plus_nub);
    translate([36, 0, 0]) print_cap(false);
    translate([0, 30, 0]) print_c_sleeve();
}
