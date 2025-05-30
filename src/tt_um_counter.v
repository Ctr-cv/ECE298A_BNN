module tt_um_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path
    input  wire       ena,      // Enable
    input  wire       clk,      // Clock
    input  wire       rst_n     // Active-low reset
);
    // Internal signals
    reg [7:0] counter_reg;
    wire reset = ~rst_n;       // Convert to active-high reset
    wire load = ui_in[0];      // Load control
    wire oe_n = ui_in[1];      // Output enable (active low)
    wire [7:0] data = ui_in[7:2]; // Data input

    // Counter logic
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            counter_reg <= 8'b0;
        end else if (load) begin
            counter_reg <= data;
        end else if (ena) begin  // Only count when enabled
            counter_reg <= counter_reg + 1;
        end
    end

    // Output with tri-state control
    assign uo_out = (~oe_n) ? counter_reg : 8'bz;

    // Tie off unused outputs
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;  // Set all IOs as inputs
endmodule
