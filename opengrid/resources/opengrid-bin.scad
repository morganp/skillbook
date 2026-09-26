$fn = 128;

/* [Bin Parameters] */

bin_width = 100;
bin_depth = 40;
bin_height = 32;

wall_thickness = 2;
floor_thickness = 2;

// You can subdivide the bin into sub-bins along its width and depth.
width_sub_bins = 1;
depth_sub_bins = 1;
sub_bin_wall_thickness = 2;

/* [Snap Parameters] */

// openGrid snap type for connecting to base plates.
snap_type = "Directional"; // [Lite, Full, Directional]

// The number of snaps to position along the connecting face of the bin.
// The snaps will be evenly spaced with one openGrid cell between them, grouped in the center of the connecting face.
// A value of `-1` means that the maximum number of snaps will be used.
preferred_snap_count = 10;

// The fitment affects the tightness of the snap when mounted (ease of removing the peg)
// Use a value between 0.0 and 1.0, with 0.5 meaning a standard fit.
// A value between 0.66-0.75 would be a tight fit, and a value of 1.0 would be very difficult to insert and remove.
snap_fitment = 0.5;

/* [Hidden] */

/*///////////////////////////
    BIN
*////////////////////////////

wall_chamfer_outer = wall_thickness * 1.5;
wall_chamfer_inner = wall_thickness;
lip_chamfer = wall_thickness/2;

module bin() {
	polyhedron(
		points = [
			/* SW Corner */ 
		
			// SW bottom outer corner
				/* 00 */ [wall_chamfer_outer, wall_chamfer_outer, 0], // bottom
				/* 01 */ [wall_chamfer_outer, 0, wall_chamfer_outer], // S
				/* 02 */ [0, wall_chamfer_outer, wall_chamfer_outer], // W
			
			// SW top/lip corner, S seam
				/* 03 */ [wall_chamfer_outer, 0, bin_height - lip_chamfer], // outer
				/* 04 */ [wall_chamfer_outer + wall_thickness/4, wall_thickness/2, bin_height], // top
				/* 05 */ [wall_chamfer_outer + wall_thickness/2, wall_thickness, bin_height - lip_chamfer], // inner
			
			// SW top/lip corner, W seam
				/* 06 */ [0, wall_chamfer_outer, bin_height - lip_chamfer], // outer
				/* 07 */ [wall_thickness/2, wall_chamfer_outer + wall_thickness/4, bin_height], // top
				/* 08 */ [wall_thickness, wall_chamfer_outer + wall_thickness/2, bin_height - lip_chamfer], // inner
			
			// SW bottom inner corner
				/* 09 */ [wall_chamfer_outer + wall_thickness/2, wall_thickness, floor_thickness + wall_chamfer_inner], // S
				/* 10 */ [wall_thickness, wall_chamfer_outer + wall_thickness/2, floor_thickness + wall_chamfer_inner], // W
				/* 11 */ [wall_thickness + wall_chamfer_inner, wall_thickness + wall_chamfer_inner, floor_thickness], // bottom
			
			/* NW Corner */
			
			// NW bottom outer corner
				/* 12 */ [wall_chamfer_outer, bin_depth - wall_chamfer_outer, 0], // bottom
				/* 13 */ [0, bin_depth - wall_chamfer_outer, wall_chamfer_outer], // W
				/* 14 */ [wall_chamfer_outer, bin_depth, wall_chamfer_outer], // N
			
			// NW top/lip corner, W seam
				/* 15 */ [0, bin_depth - wall_chamfer_outer, bin_height - lip_chamfer], // outer
				/* 16 */ [wall_thickness/2, bin_depth - (wall_chamfer_outer + wall_thickness/4), bin_height], // top
				/* 17 */ [wall_thickness, bin_depth - (wall_chamfer_outer + wall_thickness/2), bin_height - lip_chamfer], // inner
			
			// NW top/lip corner, N seam
				/* 18 */ [wall_chamfer_outer, bin_depth, bin_height - lip_chamfer], // outer
				/* 19 */ [wall_chamfer_outer + wall_thickness/4, bin_depth - wall_thickness/2, bin_height], // top
				/* 20 */ [wall_chamfer_outer + wall_thickness/2, bin_depth - wall_thickness, bin_height - lip_chamfer], // inner
			
			// NW bottom inner corner
				/* 21 */ [wall_thickness, bin_depth - (wall_chamfer_outer + wall_thickness/2), floor_thickness + wall_chamfer_inner], // W
				/* 22 */ [wall_thickness + wall_chamfer_inner, bin_depth - wall_thickness, floor_thickness + wall_chamfer_inner], // N
				/* 23 */ [wall_thickness + wall_chamfer_inner, bin_depth - (wall_thickness + wall_chamfer_inner), floor_thickness], // bottom
			
			/* NE Corner */
			
			// NE bottom outer corner
				/* 24 */ [bin_width - wall_chamfer_outer, bin_depth - wall_chamfer_outer, 0], // bottom
				/* 25 */ [bin_width, bin_depth - wall_chamfer_outer, wall_chamfer_outer], // E
				/* 26 */ [bin_width - wall_chamfer_outer, bin_depth, wall_chamfer_outer], // N
			
			// NE top/lip corner, E seam 
				/* 27 */ [bin_width, bin_depth - wall_chamfer_outer, bin_height - lip_chamfer], // outer
				/* 28 */ [bin_width - wall_thickness/2, bin_depth - (wall_chamfer_outer + wall_thickness/4), bin_height], // top
				/* 29 */ [bin_width - wall_thickness, bin_depth - (wall_chamfer_outer + wall_thickness/2), bin_height - lip_chamfer], // inner
			
			// NE top/lip corner, N seam
				/* 30 */ [bin_width - wall_chamfer_outer, bin_depth, bin_height - lip_chamfer], // outer
				/* 31 */ [bin_width - (wall_chamfer_outer + wall_thickness/4), bin_depth - wall_thickness/2, bin_height], // top
				/* 32 */ [bin_width - (wall_chamfer_outer + wall_thickness/2), bin_depth - wall_thickness, bin_height - lip_chamfer], // inner
			
			// NE bottom inner corner
				/* 33 */ [bin_width - wall_thickness, bin_depth - (wall_chamfer_outer + wall_thickness/2), floor_thickness + wall_chamfer_inner], // E
				/* 34 */ [bin_width - (wall_chamfer_outer + wall_thickness/2), bin_depth - wall_thickness, floor_thickness + wall_chamfer_inner], // N
				/* 35 */ [bin_width - (wall_thickness + wall_chamfer_inner), bin_depth - (wall_thickness + wall_chamfer_inner), floor_thickness], // bottom
			
			/* SE Corner */
			
			// SE bottom outer corner
				/* 36 */ [bin_width - wall_chamfer_outer, wall_chamfer_outer, 0], // bottom
				/* 37 */ [bin_width - wall_chamfer_outer, 0, wall_chamfer_outer], // S
				/* 38 */ [bin_width, wall_chamfer_outer, wall_chamfer_outer], // E
			
			// SE top/lip corner, S seam
				/* 39 */ [bin_width - wall_chamfer_outer, 0, bin_height - lip_chamfer], // outer
				/* 40 */ [bin_width - (wall_chamfer_outer + wall_thickness/4), wall_thickness/2, bin_height], // top
				/* 41 */ [bin_width - (wall_chamfer_outer + wall_thickness/2), wall_thickness, bin_height - lip_chamfer], // inner
			
			// SE top/lip corner, E seam
				/* 42 */ [bin_width, wall_chamfer_outer, bin_height - lip_chamfer], // outer
				/* 43 */ [bin_width - wall_thickness/2, wall_chamfer_outer + wall_thickness/4, bin_height], // top
				/* 44 */ [bin_width - wall_thickness, wall_chamfer_outer + wall_thickness/2, bin_height - lip_chamfer], // inner
			
			// SE bottom inner corner
				/* 45 */ [bin_width - (wall_chamfer_outer + wall_thickness/2), wall_thickness, floor_thickness + wall_chamfer_inner], // S
				/* 46 */ [bin_width - wall_thickness, wall_chamfer_outer + wall_thickness/2, floor_thickness + wall_chamfer_inner], // E
				/* 47 */ [bin_width - (wall_thickness + wall_chamfer_inner), wall_thickness + wall_chamfer_inner, floor_thickness], // bottom
		],
		faces = [
			// SW Corner
			[0, 1, 2],	        // outer bottom face 
			[1, 3, 6, 2],       // outer face
			[3, 4, 7, 6],       // outer lip
			[4, 5, 8, 7],       // inner lip
			[5, 9, 10, 8],      // inner face
			[9, 11, 10],        // inner bottom face
			
			// W Wall
            [0, 2, 13, 12],     // outer bottom face
            [2, 6, 15, 13],     // outer face
            [6, 7, 16, 15],     // outer lip
            [7, 8, 17, 16],     // inner lip
            [8, 10, 21, 17],    // inner face
            [10, 11, 23, 21],   // inner bottom face 
			
			// NW Corner
			[12, 13, 14],       // outer bottom face
			[13, 15, 18, 14],   // outer face
			[15, 16, 19, 18],   // outer lip
			[16, 17, 20, 19],   // inner lip
			[17, 21, 22, 20],   // inner face
			[23, 22, 21],       // inner bottom face
			
			// N Face
            [14, 26, 24, 12],   // outer bottom face
			[18, 30, 26, 14],   // outer face
			[18, 19, 31, 30],   // outer lip
			[19, 20, 32, 31],   // inner lip
			[20, 22, 34, 32],   // inner face
			[22, 23, 35, 34],   // inner bottom face
			
			// NE Corner
            [26, 25, 24],       // outer bottom face
			[25, 26, 30, 27],   // outer face
			[30, 31, 28, 27],   // outer lip
			[31, 32, 29, 28],   // inner lip
			[32, 34, 33, 29],   // inner face
			[33, 34, 35],       // inner bottom face
			
			// E Face
            [24, 25, 38, 36],   // outer bottom face
			[25, 27, 42, 38],   // outer face
			[27, 28, 43, 42],   // outer lip
			[28, 29, 44, 43],   // inner lip
			[29, 33, 46, 44],   // inner face
			[33, 35, 47, 46],   // inner bottom face
			
			// SE Corner
            [38, 37, 36],       // outer bottom face
			[38, 42, 39, 37],   // outer face
			[42, 43, 40, 39],   // outer lip
			[43, 44, 41, 40],   // inner lip
			[46, 45, 41, 44],   // inner face
			[45, 46, 47],       // inner bottom face
			
			// S Face
            [0, 36, 37, 1],    // outer bottom face
			[1, 37, 39, 3],     // outer face
			[4, 3, 39, 40],     // outer lip
			[5, 4, 40, 41],     // inner lip
			[9, 5, 41, 45],     // inner face
			[11, 9, 45, 47],    // inner bottom face
            
            // Bottom/outer face
            [0, 12, 24, 36],
            
            // Top/inner face
			[11, 47, 35, 23]
		]
	);
};

module bin_divider(length) {
    inset = wall_thickness/2;
    adjusted_length = length - wall_thickness;
    sub_bin_lip_chamfer = sub_bin_wall_thickness/2;
    height = min(bin_height, bin_height - (lip_chamfer - sub_bin_wall_thickness/2));
    
    polyhedron(
        points = [
            [inset, sub_bin_wall_thickness/2, height], // lip W
            [inset, 0, height - sub_bin_lip_chamfer], // front NW
            [inset, 0, wall_chamfer_inner], // front WSW
            [inset + wall_chamfer_inner, 0, 0], // front SSW
            [length - wall_chamfer_inner, 0, 0], // front SSE
            [length, 0, wall_chamfer_inner], // front ESE
            [length, 0, height - sub_bin_lip_chamfer], // front NE
            [length, sub_bin_wall_thickness/2, height], // lip E
            [length, sub_bin_wall_thickness, height - sub_bin_lip_chamfer], // rear NE
            [length, sub_bin_wall_thickness, wall_chamfer_inner], // rear ESE
            [length - wall_chamfer_inner, sub_bin_wall_thickness, 0], // rear SSE
            [inset + wall_chamfer_inner, sub_bin_wall_thickness, 0], // rear SSW
            [inset, sub_bin_wall_thickness, wall_chamfer_inner], // rear WSW
            [inset, sub_bin_wall_thickness, height - sub_bin_lip_chamfer], // rear NW
        ],
        
        faces = [
            [0, 1, 6, 7], // front lip
            [1, 2, 3, 4, 5, 6], // front face
            [7, 8, 13, 0], // rear lip
            [8, 9, 10, 11, 12, 13], // rear face
            [0, 1, 2, 12, 13], // W edge
            [5, 6, 7, 8, 9], // E edge
            [2, 3, 11, 12], // W bottom chamfer
            [4, 5, 9, 10], // E bottom chamfer
            [3, 4, 10, 11], // bottom edge
        ]
    );
};

/*///////////////////////////
    OPENGRID SNAP
*////////////////////////////

cell_width = 28;
snap_width = 25;
snap_wall = cell_width - snap_width; // thickness of wall between snaps
snap_margin = snap_wall / 2; // thickness of one cell's portion of the wall
long_side_length = 18.2745;
short_side_length = 15.1632;
cutout_offset = (snap_width - long_side_length) / 2;
large_cutout_offset = (snap_width - short_side_length) / 2;
short_tab_length = 10.8;

part_overlap = 0.05; // For ensuring manifold geometry during boolean operations

full_snap_thickness = 6.8;
lite_snap_thickness = 3.4;
snap_diff_thickness = full_snap_thickness - lite_snap_thickness;

module large_corner_cutouts() {
    linear_extrude(height = 5.3)
        polygon(
            points = [
                [0,0],
                [0, large_cutout_offset],
                [large_cutout_offset, 0],
                [0, snap_width-large_cutout_offset],
                [0, snap_width],
                [large_cutout_offset, snap_width],
                [snap_width-large_cutout_offset, snap_width],
                [snap_width, snap_width],
                [snap_width, snap_width-large_cutout_offset],
                [snap_width, large_cutout_offset],
                [snap_width, 0],
                [snap_width-large_cutout_offset, 0]
            ],
            paths = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]
        );
};

module corner_overhang_cutout_template() {
    translate([0, 0, 5.3])
        rotate([90, 0, 45])
            linear_extrude(height = 10)
                polygon(
                    points = [
                        [0, 0],
                        [0, 1.1],
                        [1.1, 0]
                    ]
                );
};

module corner_overhang_cutouts() {
    translate([-.8, 4.162, 0])
        corner_overhang_cutout_template();
    
    rotate([0, 0, 90])
        translate([-1.65, -20,0])
            corner_overhang_cutout_template();
    
    rotate([0, 0, -90])
        translate([-27, 5.353, 0])
            corner_overhang_cutout_template();
    
    rotate([0, 0, 180])
        translate([-27, -19.64, 0])
            corner_overhang_cutout_template();
};

module bottom_slot_cutout_template() {
    hull()
        linear_extrude(height = 6.2) {
            circle(r = 0.4);
            translate([11.8, 0, 0]) {
                circle(r = 0.4);
            };
        };
};

module bottom_slot_cutouts(snap_type) {
    slot_inset = 1.5;

    if (snap_type == "Directional") {
        rotate([13, 0, 0])
            translate([6.75, slot_inset,-7])
                scale([1, 1, 2])
                    bottom_slot_cutout_template();
    } else {
        translate([6.75, slot_inset,-7])
            scale([1, 1, 2])
                bottom_slot_cutout_template();
    }

    // Left side
    translate([slot_inset, 7, -0.01])
        rotate([0, 0, 90])
            bottom_slot_cutout_template();
    
    // Right side
    translate([snap_width - slot_inset, 7, -0.01])
        rotate([0, 0, 90])
            bottom_slot_cutout_template();
    
    // Top, for non-Directional snaps
    if (snap_type != "Directional") {
        translate([6.75, snap_width - slot_inset,-7])
            scale([1, 1, 2])
                bottom_slot_cutout_template();
    }
};

// Generates a cutout of an equilateral triangle
// used to emboss as a directional indicator for Directional snaps
module triangle_directional_cutout_template(side_length, thickness) {

    height = side_length * 0.866; // sin60 = 0.866

    linear_extrude(height = thickness)
        polygon(
            points = [
                [0, 0],
                [side_length, 0],
                [side_length / 2.0, height],
            ],
        );
};

module triangle_directional_cutout() {
    triangle_side_length = 3;
    cutout_thickness = 0.4;

    translate([(snap_width-triangle_side_length)/2, snap_width - 6, -0.1])
        triangle_directional_cutout_template(triangle_side_length, cutout_thickness);
};

module side_slot_cutouts(snap_type) {
    length = 11.4;
    width = 1;
    height = 0.4;
    top_shelf_thickness = 1.2;
    top_distance = full_snap_thickness - top_shelf_thickness;
    
    // Left side
    translate([.75, 7, top_distance])
        rotate([0, 0, 90])
            cube([length, width, height]);
    
    // Right side
    translate([snap_width-width+width, 7, top_distance])
        rotate([0, 0, 90])
            cube([length, width, height]);
    
    // Bottom
    translate([7, 0, top_distance])
        cube([length, width, height]);
    
    // Top, for non-Directional snaps
    if (snap_type != "Directional") {
        translate([7, snap_width, top_distance])
            cube([length, width, height]);
    }
};

module snap_tab(x_scale, y_scale, z_scale) {
    base_x = 14 * x_scale;
    base_y = 4 * y_scale;
    top_x = 9.5 * x_scale;
    top_y = 2.2 * y_scale;
    height = 0.8 * z_scale;

    // Offsets to center the top over the base
    dx = (base_x - top_x) / 2;
    dy = (base_y - top_y) / 2;

    points = [
        // Base (Z = 0)
        [0,      0,      0],  // 0, bottom-left of big face
        [base_x, 0,      0],  // 1, bottom-right of big face
        [base_x, base_y, 0],  // 2, top-right of big face
        [0,      base_y, 0],  // 3, top-left of big face

        // Top (Z = height), centered
        [dx,        dy,        height],  // 4, bottom-left of small face
        [dx+top_x,  dy,        height],  // 5, bottom-right of small face
        [dx+top_x,  dy+top_y,  height],  // 6, top-right of small face
        [dx,        dy+top_y,  height]   // 7, top-left of small face
    ];

    faces = [
        [0, 3, 2, 1],  // bottom
        [0, 1, 5, 4],  // side 1, front
        [0, 4, 7, 3],  // side 2, left
        [1, 2, 6, 5],  // side 3, right
        [2, 3, 7, 6],  // side 4, rear
        [4, 5, 6, 7],  // top
    ];

    polyhedron(points=points, faces=faces);
};

module snap_tab_large(fitment) {
    snap_tab(x_scale = 1.0, y_scale = 1.0, z_scale = fitment);
};

module snap_tab_small(fitment) {
    snap_tab(x_scale = 0.8, y_scale = 0.5, z_scale = fitment);
};

module top_tab(type, fitment) {
    // full or lite tab for top edge
    if (type == "Directional") {
        // full tab for directional snaps
        translate([(snap_width+14)/2, snap_width - part_overlap, 1.4])
            rotate([90, 0, 180])
                snap_tab_large(fitment = 1.0);
    } else {
        // lite tab for non-directional snaps
        translate([(snap_width+short_tab_length)/2+0.4, snap_width - part_overlap, snap_diff_thickness])
            rotate([90, 0, 180])
                snap_tab_small(fitment);
    }
};

module right_tab(fitment) {
    translate([snap_width - part_overlap, (snap_width-short_tab_length)/2, snap_diff_thickness])
        rotate([90, 0, 90])
            snap_tab_small(fitment);
};

module left_tab(fitment) {
    translate([part_overlap, (snap_width+short_tab_length)/2+0.4, snap_diff_thickness])
        rotate([90, 0, -90])
            snap_tab_small(fitment);
};

module bottom_tab(fitment) {
    translate([(snap_width-short_tab_length)/2, part_overlap, snap_diff_thickness])
        rotate([90, 0, 0])
            snap_tab_small(fitment);
};

module lite_snap_cutout() {
    linear_extrude(height = snap_diff_thickness)
        polygon(
            points = [
                [0, 0],
                [0, 30],
                [30, 30],
                [30, 0]
            ]
        );
}

module bottom_half_snapfit_cutter() {
    rotate([90, 0, 90])
        linear_extrude(height = 20)
            polygon(
                points = [
                    [0, 0],
                    [0.8, 0], 
                    [0, 3.4]
                ]
            );
};

module bottom_half_snapfit_cutouts() {
    translate([3, 0, 0])
        bottom_half_snapfit_cutter();

    translate([snap_width-cutout_offset-1.555, 0, 0])
        rotate([0, 0, 45])
            bottom_half_snapfit_cutter();
            
    translate([-3, 7.918, 0])
        rotate([0, 0, -45])
            bottom_half_snapfit_cutter();
};

module primary_box() {
    linear_extrude(height = full_snap_thickness)
        polygon(
            points = [
                [0, cutout_offset],
                [0, cutout_offset+long_side_length],
                [cutout_offset, snap_width],
                [cutout_offset+long_side_length, snap_width],
                [snap_width, cutout_offset+long_side_length],
                [snap_width, cutout_offset],
                [cutout_offset+long_side_length, 0],
                [cutout_offset, 0]
            ]
        );
};

module opengrid_snap(snap_type, fitment) {
    union() {
        difference() {
            primary_box();

            large_corner_cutouts();
            corner_overhang_cutouts();

            bottom_slot_cutouts(snap_type);
            side_slot_cutouts(snap_type);
            
            if (snap_type == "Directional") {
                triangle_directional_cutout();
                bottom_half_snapfit_cutouts();
            }

            if (snap_type == "Lite") {
                lite_snap_cutout();
            }
        };
        top_tab(type = snap_type, fitment = fitment);
        bottom_tab(fitment = fitment);
        left_tab(fitment = fitment);
        right_tab(fitment = fitment);
    };
};

/*///////////////////////////
    ASSEMBLY MODULES
*////////////////////////////

module positioned_snaps() {

    // Figure out how many snaps to place, and their spacing
    snap_surface_width = bin_width - (wall_chamfer_outer * 2);
    cell_count = floor(snap_surface_width / cell_width);
    cell_count_is_even = cell_count % 2 == 0 ? true : false;
    max_snap_count = cell_count_is_even ? floor(cell_count/2) : floor(cell_count/2) + 1; // max number of snaps that we could fit with gaps between
    user_snap_count = preferred_snap_count == -1 ? max_snap_count : preferred_snap_count; // user's preferred snap count (max if -1)
    snap_count = min(max_snap_count, user_snap_count); // resolved actual number of snaps to use
    snap_count_is_even = snap_count % 2 == 0 ? true : false;

    // echo(str("Snap surface width: ", snap_surface_width));
    // echo(str("Cell count: ", cell_count));
    // echo(str("Max snap count: ", max_snap_count));
    // echo(str("User snap count: ", user_snap_count));
    // echo(str("Snap count: ", snap_count));
    // echo(str("Snap count is even: ", snap_count_is_even));

    snap_thickness = snap_type == "Lite" ? lite_snap_thickness : full_snap_thickness;

    snap_group_width = snap_count_is_even ? (cell_width * snap_count * 2) - cell_width : (cell_width * snap_count * 2);
    snap_group_offset = snap_count_is_even ? (snap_surface_width - snap_group_width) / 2 + wall_chamfer_outer : (snap_surface_width - snap_group_width) / 2 + wall_chamfer_outer + cell_width/2;
    
    translate([snap_group_offset, full_snap_thickness - 0.1, bin_height - cell_width])
        for (i = [0 : snap_count - 1]) {
            translate([(cell_width)*2*i + snap_margin, 0, 0])
                rotate([90, 0 , 0])
                    opengrid_snap(snap_type = snap_type, fitment = snap_fitment);
        }
};

module positioned_bin() {
    translate([0, -bin_depth, 0])
        bin();
};

module positioned_dividers() {
    inner_width = bin_width - sub_bin_wall_thickness*(width_sub_bins+1);
    width_gap = inner_width / width_sub_bins;
    inner_depth = bin_depth - sub_bin_wall_thickness*2;
    depth_gap = inner_depth / depth_sub_bins;

    if (width_sub_bins > 1) {
        for (i = [1 : width_sub_bins - 1]) {
            translate([wall_thickness + width_gap*i + sub_bin_wall_thickness*(i-1), 0, 0])
                rotate([0, 0, -90])
                    bin_divider(length = bin_depth - wall_thickness/2);
        }
    }
    
    if (depth_sub_bins > 1) {
        for (i = [1 : depth_sub_bins - 1]) {
            translate([0, -wall_thickness - depth_gap*i - sub_bin_wall_thickness*(i-1), 0])
                bin_divider(length = bin_width - wall_thickness/2);
        }
    }
};

// Final Product
union() {
    render(convexity = 10) positioned_snaps();
    render(convexity = 10) positioned_bin();
    positioned_dividers();
};
