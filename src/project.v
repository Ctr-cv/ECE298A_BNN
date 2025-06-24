/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_BNN (
    input  wire [7:0] ui_in,    // Input: 6-bit data, [7:2]
    output wire [7:0] uo_out,   // Output: 4 neuron output + 2 debug bits, [7:2]
    input  wire [7:0] uio_in,   // Bir-Inputs: 6-bits weight [7:2], 1-bit load_en [1]
    output wire [7:0] uio_out,  // Bir-Outputs: Unused
    output wire [7:0] uio_oe,   // Bir-IO enable, not used
    input  wire       ena,      // Enable
    input  wire       clk,      // Clock
    input  wire       rst_n     // Active-low reset
);
// --------------- Constants set for BNN ------------------------
localparam NUM_NEURONS = 4;
localparam NUM_WEIGHTS = 6;

wire reset = ~rst_n; // use active-high reset
wire [5:0] data = {2'b0, ui_in[7:2]}; // 00 + 6-bit input
wire load_en = uio_in[0];             // 1-bit load_en signal

reg [NUM_WEIGHTS-1:0] weight [0:NUM_NEURONS-1]; // 6-bits weight per 4 neurons, declared here
reg [1:0] thresholds [0:NUM_NEURONS-1];  // threshold for each neuron

reg [2:0] load_state; // Used for weight-loading to indicate # neuron.
wire [2:0] sums [0:NUM_NEURONS-1];  // Used for XNOR-Popcount 3-bit sums (max 6)

initial begin
    // initialize hard-coded weights and thresholds for all neurons.
    // note that you'll need to delete or add weights depending on NUM_NEURONS
    weights[0] = 6'b111000; threshold[0] = 2'b10;
    weights[1] = 6'b000111; thresholds[1] = 2'b10;
    weights[2] = 6'b001100; threshold[2] = 2'b10;
    weights[3] = 6'b110011; thresholds[3] = 2'b10;
end

// -------------- Weight Loading Here ----------------------------
always @(posedge clk or posedge reset) begin
  if (reset) begin
    load_state <= 0;
  end else if (load_en) begin  // Use bidir pin to trigger loading
    weights[load_state] <= uio_in[7:2];  // Load 6 bits from bidir pins
    load_state <= load_state + 1;
  end
end

// -------------- BNN Core Logic Here ----------------------------
// --- XNOR-Popcount Calculation ---
genvar i;
generate
  for (i = 0; i < NUM_NEURONS; i = i + 1) begin : neuron
    // XNOR each input bit with weight, then sum
    assign sums[i] = (input_data[0] ~^ weights[i][0]) + 
                     (input_data[1] ~^ weights[i][1]) + 
                     (input_data[2] ~^ weights[i][2]) + 
                     (input_data[3] ~^ weights[i][3]) + 
                     (input_data[4] ~^ weights[i][4]) + 
                     (input_data[5] ~^ weights[i][5]);
  end
endgenerate

// --- Threshold Activation ---
wire [NUM_NEURONS-1:0] neuron_outputs;
generate
  for (i = 0; i < NUM_NEURONS; i = i + 1) begin : activation
    assign neuron_outputs[i] = (sums[i] >= thresholds[i]);
  end
endgenerate

// --------------- Output Assignment ----------------------------
// --- Dedicated Outputs ---
assign uo_out[3:0] = neuron_outputs;  // 4 neuron outputs
// assign uo_out[5:4] = debug_bits;      // Debug signals (XOR/AND)

// --- Bidirectional Pins (Optional) ---
assign uio_out = 8'b0;      // Unused (set to 0)
assign uio_oe  = 8'b0;      // Configure as inputs (0)

endmodule

// module tt_um_counter (
    // input  wire [7:0] ui_in,    // Dedicated inputs
    // output wire [7:0] uo_out,   // Dedicated outputs
    // input  wire [7:0] uio_in,   // IOs: Input path
    // output wire [7:0] uio_out,  // IOs: Output path
    // output wire [7:0] uio_oe,   // IOs: Enable path
    // input  wire       ena,      // Enable
    // input  wire       clk,      // Clock
    // input  wire       rst_n     // Active-low reset
// );

//     // Bit 0: value load control bit
//     // Bit 1: Enable output control bit
//     // bit 2: Enable counting control bit
//     // bit 3-7: Load value data bits
    
//     reg [7:0] counter_reg;
//     wire reset = ~rst_n;       // Active-high reset
//     wire load = ui_in[7];      // Load control
//     wire output_en = ui_in[6];      // Output enable control (active high) 
//     wire count_up = ui_in[5];   // Count control (1 = count up, 0 = hold)
//     wire [7:0] data = {3'b0, ui_in[4:0]}; // Loading data (5-bits, maxes at 31)

//     always @(posedge clk or posedge reset) begin
//         if (reset) begin
//             counter_reg <= 8'b0;
//         end else if (load) begin
//             counter_reg <= data;  // Load on rising edge of 'load'
//         end else if (count_up) begin
//             counter_reg <= counter_reg + 1;  // Count up 
//         end
//     end

//     // dummy values
//     assign uio_out = 8'b0;
//     assign uio_oe = 8'b0;
//     assign uo_out = (output_en) ? counter_reg : 8'bZ;  // Tri-state, active high output

//     // Unused I/Os here
//     wire _unused = &{ena, uio_oe, uio_in, uio_out, 1'b0}; 
// endmodule
