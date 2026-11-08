// Looping Louie Wi-Fi retrofit - holder for the charger board
//
// AA compartment variant (second compartment instead of the bridge board):
//   The charger board stands ON EDGE in the AA shape, the USB-C socket on the long edge points up and out
//   of the compartment. Shell (circle segment behind the board) + 2 end caps, joined with dowels made of
//   1.75 mm filament - same principle as the main board insert (sleeve.scad).
//   The end caps guide the nickel strips of the bridge (BT101/BT102) to the compartment contacts.
// Base variant:
//   Flat holder (tray with screw tabs), glued or screwed with the plug edge against the inner wall of the
//   base. The wall gets a hole for the USB-C plug (dimensions: see echo).
//
// Coordinates (AA assembly): x = cell axis, board centre at the origin, z = up (plug direction),
// the component side faces +y. Board dimensions see hardware/scripts/gen_charger_pcb.py.
//
// Export: just stl

/* [Selection] */
part = "assembly"; // [assembly, assembly_base, exploded, print_shell, print_cap_plus, print_cap_minus, print_base_holder, print_all]

/* [Cell] */
aa_d = 14.5;
aa_l = 50.5;
plus_nub = true;
nub_d = 5.5;
nub_h = 1.0;

/* [Board] */
pcb_l = 46.0;
pcb_h = 12.5;       // board width, vertical in the compartment
pcb_t = 1.6;
pcb_back = -3.2;    // y of the back side (solder side without components); front side at pcb_back + pcb_t
usb_x = -15.0;      // centre of the USB-C socket (gen_charger_pcb.py: USB_X)
jst_x = 10.5;       // centre of the JST-PH connector
led_x = -7.0;       // charge indicator at the top edge

/* [Construction] */
clearance = 0.2;
overlap = 0.8;          // how far the board engages in the cap at each end
pocket_depth = 0.6;     // recess in the shell for solder/vias on the back side
rim = 1.2;              // support ledges at top and bottom
dowel_d = 1.75;
dowel_hole = 1.95;
dowel_z = 2.6;          // dowels at z = +-dowel_z
dowel_y = -5.3;
dowel_depth = 4.0;
strip_w = 4.0;          // nickel strip 4 x 0.15 mm
strip_slot_t = 0.45;

/* [Base holder] */
floor_t = 1.2;          // floor under the board
wall = 1.6;             // side walls
plug_w = 13.5;          // hole in the base wall for the plug overmould (USB-C max. approx. 12.4 x 6.5)
plug_h = 7.5;
tab_hole = 2.2;         // for M2 or a 2.2 mm self-tapping screw

$fn = 96;

// derived
r = aa_d / 2;
pcb_front = pcb_back + pcb_t;
cap_inner = pcb_l / 2 - overlap;
shell_l = 2 * cap_inner;
cap_l = aa_l / 2 - cap_inner;
eps = 0.01;

assert(pcb_back * pcb_back + (pcb_h / 2) * (pcb_h / 2) < r * r, "board corners stick out of the AA shape");

// ---------- AA variant: shell ----------

module shell_profile() {      // (y, z)
    difference() {
        intersection() {
            circle(r = r);
            translate([-r, -r]) square([r + pcb_back, 2 * r]);
        }
        // pocket behind the board, support only on the ledges at top and bottom
        translate([pcb_back - pocket_depth, -(pcb_h / 2 - rim)]) square([pocket_depth + eps, pcb_h - 2 * rim]);
    }
}

// extrude a (y, z) profile along x
module along_x(l) {
    multmatrix([[0, 0, 1, -l / 2], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        linear_extrude(height = l) children();
}

module dowel_holes(depth) {
    for (s = [-1, 1]) translate([0, dowel_y, s * dowel_z])
        rotate([0, 90, 0]) cylinder(d = dowel_hole, h = 2 * depth, center = true, $fn = 24);
}

module shell() {
    difference() {
        along_x(shell_l) shell_profile();
        for (x = [-1, 1]) translate([x * cap_inner, 0, 0]) dowel_holes(dowel_depth);
    }
}

// ---------- AA variant: caps ----------

module cap(nub) {          // at the +x end; minus cap = rotated about z
    body = cap_l - (nub ? nub_h : 0);
    difference() {
        union() {
            translate([cap_inner, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = body);
            if (nub)
                translate([cap_inner + body - eps, 0, 0]) rotate([0, 90, 0])
                    cylinder(d = nub_d, h = nub_h + eps);
        }
        // vertical board slot, blind
        translate([cap_inner - 1, pcb_back - clearance, -(pcb_h / 2 + clearance)])
            cube([1 + overlap + clearance, pcb_t + 2 * clearance, pcb_h + 2 * clearance]);
        // nickel strip: behind the board (pad BT10x on the back side) through the cap to the outside
        translate([cap_inner - 1, pcb_back - strip_slot_t, -(strip_w / 2 + clearance)])
            cube([cap_l + 2, strip_slot_t + eps, strip_w + 2 * clearance]);
        translate([cap_inner, 0, 0]) dowel_holes(min(dowel_depth, body - 0.6));
    }
}

// ---------- Base variant: flat holder ----------
// Coordinates: board lies flat, components up, plug edge at y = 0 (flush with the front edge of the holder),
// the board extends towards -y.

holder_l = pcb_l + 2 * (wall + clearance);
holder_w = pcb_h + clearance + wall;
holder_h = floor_t + pcb_t + 0.6;     // walls 0.6 mm above the board: hold it sideways without touching components

module base_holder() {
    difference() {
        union() {
            translate([-holder_l / 2, -holder_w, 0]) cube([holder_l, holder_w, holder_h]);
            // screw/glue tabs at the ends
            for (s = [-1, 1]) hull() {
                translate([s * (holder_l / 2 - 1), -holder_w, 0]) cube([2, holder_w, floor_t], center = false);
                translate([s * (holder_l / 2 + 3), -holder_w / 2, 0]) cylinder(d = 6, h = floor_t, $fn = 40);
            }
        }
        // board recess, open towards the front (plug edge)
        translate([-pcb_l / 2 - clearance, -pcb_h - clearance, floor_t]) cube([pcb_l + 2 * clearance, pcb_h + clearance + 1, holder_h]);
        // solder pads/nickel strip underneath: shallow pocket
        translate([-(pcb_l / 2 - 3), -(pcb_h - rim), floor_t - pocket_depth])
            cube([pcb_l - 6, pcb_h - 2 * rim, pocket_depth + eps]);
        for (s = [-1, 1]) translate([s * (holder_l / 2 + 3), -holder_w / 2, -1])
            cylinder(d = tab_hole, h = floor_t + 2, $fn = 24);
    }
}

// hole in the base wall (view only): centre at the height of the socket opening
usb_centre_z = floor_t + pcb_t + 1.63;
echo(str("Base: hole ", plug_w, " x ", plug_h, " mm in the wall, centre ", usb_centre_z,
         " mm above the seating face of the holder; hole centre ", holder_l / 2 + usb_x,
         " mm from the left end of the holder (looking at the wall from inside)"));

// ---------- Board dummy (view only) ----------

module component_front(x0, x1, z0, z1, h) {   // component on the front side of the board standing on edge
    translate([x0, pcb_front, z0]) cube([x1 - x0, h, z1 - z0]);
}

// Looking at the component side (from +y) with the plug edge at the top, -x is on the right. That is why x
// in the dummy is mirrored relative to KiCad (x_dummy = -x_KiCad); otherwise the board would be reversed.
module board_dummy() {        // on edge, coordinates as in the AA assembly
    color("darkgreen") translate([-pcb_l / 2, pcb_back, -pcb_h / 2]) cube([pcb_l, pcb_t, pcb_h]);
    color("silver") component_front(-usb_x - 4.47, -usb_x + 4.47, -1.1, pcb_h / 2, 3.26);   // USB-C
    color("ivory") component_front(-jst_x - 3.95, -jst_x + 3.95, -3.45, pcb_h / 2 - 0.2, 4.7);  // JST-PH
    color("dimgray") {
        component_front(2.6, 8.2, -5.6, -3.0, 2.3);      // D102 SMA
        component_front(2.6, 4.6, -0.2, 2.6, 1.1);       // U101
        component_front(13.5, 16.5, -6.0, -3.0, 1.1);    // U102
    }
    color("red") component_front(-led_x - 0.8, -led_x + 0.8, 4.8, 5.6, 0.6);
    color("gold") for (s = [-1, 1])     // nickel strips of the bridge
        translate([s > 0 ? 20.4 : -aa_l / 2, pcb_back - 0.15, -strip_w / 2]) cube([aa_l / 2 - 20.4, 0.15, strip_w]);
}

module aa_insert() {
    color("orange", 0.8) shell();
    color("orange", 0.8) cap(plus_nub);
    color("orange", 0.8) rotate([0, 0, 180]) cap(false);
}

module print_shell()     rotate([0, -90, 0]) translate([cap_inner, 0, 0]) shell();
module print_cap(nub)    rotate([0, -90, 0]) translate([-cap_inner, 0, 0]) cap(nub);

if (part == "assembly") {
    aa_insert();
    board_dummy();
    // USB-C plug from above (outline of the overmould)
    color("black", 0.4) translate([-usb_x - 6.2, pcb_front + 1.63 - 3.25, pcb_h / 2 + 1]) cube([12.4, 6.5, 12]);
} else if (part == "assembly_base") {
    color("orange", 0.8) base_holder();
    // board laid flat: rotate the on-edge dummy about x, plug edge to y = 0
    translate([0, 0, floor_t - pcb_back]) rotate([0, 0, 180]) translate([0, pcb_h / 2, 0]) rotate([90, 0, 0]) board_dummy();
    // base wall with hole (view)
    color("lightblue", 0.4) difference() {
        translate([-35, 0, -2]) cube([70, 2, 20]);
        translate([usb_x - plug_w / 2, -1, usb_centre_z - plug_h / 2]) cube([plug_w, 4, plug_h]);
    }
} else if (part == "exploded") {
    a = 8;
    color("orange", 0.8) shell();
    translate([0, 6, 0]) board_dummy();
    color("orange", 0.8) translate([a, 0, 0]) cap(plus_nub);
    color("orange", 0.8) translate([-a, 0, 0]) rotate([0, 0, 180]) cap(false);
    color("red") for (x = [-1, 1], s = [-1, 1])
        translate([x * (cap_inner + a / 2), dowel_y, s * dowel_z])
            rotate([0, 90, 0]) cylinder(d = dowel_d, h = dowel_depth + 2, center = true, $fn = 24);
} else if (part == "print_shell") print_shell();
else if (part == "print_cap_plus") print_cap(plus_nub);
else if (part == "print_cap_minus") print_cap(false);
else if (part == "print_base_holder") base_holder();
else if (part == "print_all") {
    print_shell();
    translate([18, 0, 0]) print_cap(plus_nub);
    translate([36, 0, 0]) print_cap(false);
    translate([0, 40, 0]) base_holder();
}
