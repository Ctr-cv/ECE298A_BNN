module tt_um_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // Enable - goes high when design is selected
    input  wire       clk,      // Clock
    input  wire       rst_n     // Asynchronous reset, active low
);

    // Map the Tiny Tapeout signals to your module
    wire reset = ~rst_n;  // Convert active-low to active-high
    wire load = ui_in[0]; // Using first UI input for load
    wire oe_n = ui_in[1]; // Using second UI input for output enable
    
    // Instantiate your counter
    programmable_counter counter (
        .clk(clk),
        .reset(reset),
        .load(load),
        .oe_n(oe_n),
        .data(ui_in[7:2]), // Using remaining UI inputs for data
        .count(uo_out)
    );
    
    // Set unused outputs
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;  // Set all IOs as inputs
endmodule
