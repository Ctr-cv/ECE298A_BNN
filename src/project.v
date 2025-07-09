/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

 /*
 * This is the Design for a 8-8-4 neuron BNN with weight loading into all neurons.
 */

`default_nettype none

module tt_um_BNN (
    input  wire [7:0] ui_in,    // Input: 8-bit ui_in, [7:0]
    output wire [7:0] uo_out,   // Output: 4 neuron output + 2 debug bits, [7:2]
    input  wire [7:0] uio_in,   // Bir-Inputs: 4-bit weight [7:4], 1-bit load_en [3]
    output wire [7:0] uio_out,  // Bir-Outputs: Unused
    output wire [7:0] uio_oe,   // Bir-IO enable, not used
    input  wire       ena,      // Enable
    input  wire       clk,      // Clock
    input  wire       rst_n     // Active-low reset
);
// --------------- Constants set for BNN ------------------------
localparam NUM_NEURONS = 12;
localparam NUM_WEIGHTS = 4;

wire reset = ~rst_n; // use active-high reset

// 8-bits weight per 4 neurons, declared here
reg [2*NUM_WEIGHTS-1:0] weights [0:NUM_NEURONS-1]; // neuron 0 takes [7:0] weights at index 0, and etc.
reg [3:0] thresholds [0:NUM_NEURONS-1];  // threshold for each neuron

reg [4:0] load_state; // Used for weight-loading to indicate # neuron.
wire [3:0] sums [0:NUM_NEURONS-1];  // Used for XNOR-Popcount 4-bit sums

reg [3:0] temp_weight; // used as a buffer for weight loading
reg bit_index; // Used for weight loading. 0: lower 4 bits, 1: upper 4 bits


// initial only works in simulation, may need to change later
initial begin
    // initialize hard-coded weights and thresholds for all neurons.
    // note that you'll need to delete or add weights depending on NUM_NEURONS
    // First layer: 8 neurons
    weights[0] = 8'b11111111; thresholds[0] = 4'b0000;
    weights[1] = 8'b00001111; thresholds[1] = 4'b0000;
    weights[2] = 8'b00111100; thresholds[2] = 4'b0000;
    weights[3] = 8'b11000011; thresholds[3] = 4'b0000;
    weights[4] = 8'b11110000; thresholds[4] = 4'b0000;
    weights[5] = 8'b00001111; thresholds[5] = 4'b0000;
    weights[6] = 8'b00111100; thresholds[6] = 4'b0000;
    weights[7] = 8'b11000011; thresholds[7] = 4'b0000;
    // Second layer: 4 neurons
    weights[8] = 8'b11110000; thresholds[8] = 4'b0100;
    weights[9] = 8'b00001111; thresholds[9] = 4'b0100;
    weights[10] = 8'b00111100; thresholds[10] = 4'b0100;
    weights[11] = 8'b11000011; thresholds[11] = 4'b0100;
    // weights[12] = 8'b11110000; thresholds[12] = 4'b0100;
    // weights[13] = 8'b00110000; thresholds[13] = 4'b0100;
    // weights[14] = 8'b10100000; thresholds[14] = 4'b0100;
    // weights[15] = 8'b11000011; thresholds[15] = 4'b0100;
    // // Third layer: 4 neurons NO THIRD LAYER
    // weights[16] = 8'b11110000; thresholds[16] = 4'b0100;
    // weights[17] = 8'b00110000; thresholds[17] = 4'b0100;
    // weights[18] = 8'b10100000; thresholds[18] = 4'b0100;
    // weights[19] = 8'b11000011; thresholds[19] = 4'b0100;
end

// -------------- Weight Loading for all layers ----------------------------
// NOTE: each neuron takes 2 clock cycles to load, needs to set load_enable high for at least 2 cycles
always @(posedge clk or posedge reset) begin
  if (reset) begin
    load_state <= 0;
    temp_weight <= 8'b00000000;
    bit_index <= 0;
  end else if (ena && uio_in[3]) begin  // Use bidir pin to trigger loading
    if (bit_index == 0) begin
      temp_weight[3:0] <= uio_in[7:4];
      bit_index <= 1;
    end else begin
      weights[load_state] <= {uio_in[7:4], temp_weight[3:0]};
      load_state <= load_state + 1;
      bit_index <= 0;
    end
  end
end

// ------------------------ Layer 1 ------------------------------
// ---------- XNOR-Popcount Calculation ------------
genvar i;
generate
  for (i = 0; i < 8; i = i + 1) begin : neuron1
    // XNOR each input bit with weight, then sum
    assign sums[i] = {3'b000, (ui_in[0] ~^ weights[i][0])} + 
                     {3'b000, (ui_in[1] ~^ weights[i][1])} +
                     {3'b000, (ui_in[2] ~^ weights[i][2])} +
                     {3'b000, (ui_in[3] ~^ weights[i][3])} + 
                     {3'b000, (ui_in[4] ~^ weights[i][4])} + 
                     {3'b000, (ui_in[5] ~^ weights[i][5])} +
                     {3'b000, (ui_in[6] ~^ weights[i][6])} +
                     {3'b000, (ui_in[7] ~^ weights[i][7])};
  end
endgenerate

// ----------------- Threshold Activation -------------------------
wire [7:0] neuron_out1;
generate
  for (i = 0; i < 8; i = i + 1) begin : activation1
    assign neuron_out1[i] = (sums[i] >= thresholds[i]);
  end
endgenerate

// ------------------------ Layer 2 ------------------------------
// ------------------ XNOR-Popcount Calculation ------------------
// genvar j;
// generate
//   for (j = 8; j < 16; j = j + 1) begin : neuron2
//     // XNOR each input bit with weight, then sum
//     // Note, here only last 4 bits of weights are taken from weights[7:4].
//     assign sums[j] = {3'b000, (neuron_out1[0] ~^ weights[j][0])} +
//                      {3'b000, (neuron_out1[1] ~^ weights[j][1])} +
//                      {3'b000, (neuron_out1[2] ~^ weights[j][2])} +
//                      {3'b000, (neuron_out1[3] ~^ weights[j][3])} + 
//                      {3'b000, (neuron_out1[4] ~^ weights[j][4])} +
//                      {3'b000, (neuron_out1[5] ~^ weights[j][5])} +
//                      {3'b000, (neuron_out1[6] ~^ weights[j][6])} +
//                      {3'b000, (neuron_out1[7] ~^ weights[j][7])};
//   end
// endgenerate

// // ----------------- Threshold Activation -------------------------
// wire [7:0] neuron_out2;
// generate
//   for (j = 8; j < 16; j = j + 1) begin : activation2
//     assign neuron_out2[j-8] = (sums[j] >= thresholds[j]);
//   end
// endgenerate

// ------------------------ Layer 2 (actual) ------------------------------
// ------------------ XNOR-Popcount Calculation ------------------
genvar k;
generate
  for (k = 8; k < NUM_NEURONS; k = k + 1) begin : neuron3
    // XNOR each input bit with weight, then sum
    // Note, here only last 4 bits of weights are taken from weights[7:4].
    assign sums[k] = {3'b000, (neuron_out1[0] ~^ weights[k][0])} +
                     {3'b000, (neuron_out1[1] ~^ weights[k][1])} +
                     {3'b000, (neuron_out1[2] ~^ weights[k][2])} +
                     {3'b000, (neuron_out1[3] ~^ weights[k][3])} + 
                     {3'b000, (neuron_out1[4] ~^ weights[k][4])} +
                     {3'b000, (neuron_out1[5] ~^ weights[k][5])} +
                     {3'b000, (neuron_out1[6] ~^ weights[k][6])} +
                     {3'b000, (neuron_out1[7] ~^ weights[k][7])};
  end
endgenerate

// ----------------- Threshold Activation -------------------------
wire [3:0] neuron_out3;
generate
  for (k = 8; k < NUM_NEURONS; k = k + 1) begin : activation3
    assign neuron_out3[k-8] = (sums[k] >= thresholds[k]);
  end
endgenerate

// --------------- Output Assignment ----------------------------
// -------------- Dedicated Outputs ----------------------------
assign uo_out[7:0] = {neuron_out3, neuron_out1[7:4]};  // 4 neuron outputs

// --- Cleaning unused pins ---
assign uio_out = 8'b00000000;      // Unused (set to 0)
assign uio_oe  = 8'b00000000;      // Configure as inputs (0)

endmodule