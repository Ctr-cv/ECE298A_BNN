module counter (
    input wire clk,          // Clock input
    input wire reset,       // Active-high reset
    input wire load,        // Active-high load control
    input wire oe_n,        // Active-low output enable (for tri-state)
    input wire [7:0] data,  // 8-bit data input for loading
    output wire [7:0] count // 8-bit counter output
);

    reg [7:0] counter_reg;  // Internal counter register
    
    // Counter logic
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            counter_reg <= 8'b0;         // Reset counter to 0
        end else if (load) begin
            counter_reg <= data;         // Synchronous load
        end else begin
            counter_reg <= counter_reg + 1; // Increment counter
        end
    end
    
    // Tri-state output control
    assign count = (~oe_n) ? counter_reg : 8'bz;
    
endmodule
