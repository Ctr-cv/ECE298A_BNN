module counter (
    input wire clk,
    input wire reset,
    input wire load,
    input wire oe_n,
    input wire [7:0] data,
    output wire [7:0] count
);
    reg [7:0] counter_reg;
    
    always @(posedge clk or posedge reset) begin
        if (reset) counter_reg <= 8'b0;
        else if (load) counter_reg <= data;
        else counter_reg <= counter_reg + 1;
    end
    
    assign count = (~oe_n) ? counter_reg : 8'bz;
endmodule

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
    // Signal mapping
    wire reset = ~rst_n;
    wire load = ui_in[0];
    wire oe_n = ui_in[1];
    wire [7:0] data = ui_in[7:2];
    
    // Instantiation
    counter counter_inst (
        .clk(clk),
        .reset(reset),
        .load(load),
        .oe_n(oe_n),
        .data(data),
        .count(uo_out)
    );
    
    // Set unused outputs
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;
endmodule
