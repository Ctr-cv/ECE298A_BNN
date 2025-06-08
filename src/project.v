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
    reg [7:0] counter_reg;
    wire reset = ~rst_n;       // Active-high reset
    wire load = ui_in[0];      // Load control
    wire enable = ui_in[1];      // Output enable control
    wire count_up = ui_in[2];   // Enable count control
    wire [7:0] data = {ui_in[7:3], 2'b0}; // Loading data (6-bits, multiples of 8, maxes at 248)

    assign uo_out = counter_reg; // Link dedicated output to counter

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            counter_reg <= 8'b0;
        end else if (load) begin
            counter_reg <= data;  // Load on rising edge of 'load'
        end else if (count_up) begin
            counter_reg <= counter_reg + 1;  // Count only if enabled
        end
    end

    assign uo_out = (~enable) ? counter_reg : 8'bZ;  // Tri-state

    // Unused I/Os here
    wire _unused = &{ena, uio_oe, uio_in, uio_out, 1'b0}; 
endmodule
