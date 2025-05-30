module tt_um_counter (
    input  wire [7:0] ui_in,    
    output wire [7:0] uo_out,   
    input  wire [7:0] uio_in,   
    output wire [7:0] uio_out,  
    output wire [7:0] uio_oe,   
    input  wire       ena,      
    input  wire       clk,     
    input  wire       rst_n     
);

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
