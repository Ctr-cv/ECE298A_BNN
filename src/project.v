/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

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

    // Bit 0: value load control bit
    // Bit 1: Enable output control bit
    // bit 2: Enable counting control bit
    // bit 3-7: Load value data bits
    
    reg [7:0] counter_reg;
    wire reset = ~rst_n;       // Active-high reset
    wire load = ui_in[0];      // Load control
    wire output_en = ui_in[1];      // Output enable control (actve 
    wire count_up = ui_in[2];   // Count control (1 = count up, 0 = count down)
    wire [7:0] data = {ui_in[7:3], 3'b0}; // Loading data (6-bits, multiples of 8, maxes at 248)

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            counter_reg <= 8'b0;
        end else if (load) begin
            counter_reg <= data;  // Load on rising edge of 'load'
        end else if (count_up) begin
            counter_reg <= counter_reg + 1;  // Count up 
        end else if (!count_up) begin
            counter_reg <= counter_reg - 1;  // else count down
        end
    end

    assign uo_out = (output_en) ? counter_reg : 8'bZ;  // Tri-state, active high output

    // Unused I/Os here
    wire _unused = &{ena, uio_oe, uio_in, uio_out, 1'b0}; 
endmodule
