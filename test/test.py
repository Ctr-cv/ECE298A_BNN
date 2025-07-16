# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.result import TestFailure
import random

# ---------------------- This test needs to be updated to the actual project -------------------------
# 1. test using static weight, 3 sets of testing data
# 2. test using partially loaded weight onto neuron 1 & 2, 3 sets
# 3. test using fully loaded weight onto all neurons, 3 sets 
# 4. test on debugging outputs and intermediate process, 1 set
@cocotb.test()
async def test_tt_um_BNN(dut): 
    # Start clock (100MHz)
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Initialize signals
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0
    
    # Reset for 2 cycles
    await Timer(2, units="ns")
    dut.rst_n.value = 1
    await Timer(2, units="ns")
    
    # --------------------------
    # Test 1: Verify Hardcoded Weights
    # --------------------------
    await test_hardcoded_weights(dut)
    
    # --------------------------
    # Test 2: Dynamic Weight Loading
    # --------------------------
    # await test_weight_loading(dut)
    
    # --------------------------
    # Test 3: Full Network Inference
    # --------------------------
    # await test_network_inference(dut)

async def test_hardcoded_weights(dut):
    # Test initial hard-coded weights
    cocotb.log.info(f"Testing hardcoded weights")
    
    # A single test 0b11110000 is provided, more could be added later
    # Test pattern that should activate neuron 0 (weights = 11110000)
    stop_patterns = [
        [0, 0, 0, 0, 0, 0, 0, 1],  # Row 2
        [0, 0, 0, 0, 0, 0, 1, 0],  # Row 3
        [0, 0, 0, 0, 0, 0, 1, 1],  # Row 4
        [0, 0, 0, 0, 0, 1, 0, 0],  # Row 5
        [0, 0, 0, 0, 0, 1, 0, 1],  # Row 6
        [0, 0, 0, 0, 0, 1, 1, 0],  # Row 7
        [0, 0, 0, 0, 0, 1, 1, 1],  # Row 8
        [0, 0, 0, 0, 1, 0, 0, 1],  # Row 10
        [0, 0, 0, 0, 1, 0, 1, 0],  # Row 11
        [0, 0, 0, 0, 1, 0, 1, 1],  # Row 12
        [0, 0, 0, 0, 1, 1, 0, 0],  # Row 13
        [0, 0, 0, 0, 1, 1, 0, 1],  # Row 14
        [0, 0, 0, 0, 1, 1, 1, 0],  # Row 15
        [0, 0, 0, 0, 1, 1, 1, 1],  # Row 16
        [0, 0, 0, 1, 0, 0, 0, 1],  # Row 18
        [0, 0, 0, 1, 0, 0, 1, 0]   # Row 19
    ]

    left_patterns = [
        [0, 0, 0, 0, 0, 0, 0, 0],  # Row 1
        [0, 0, 0, 0, 1, 0, 0, 0],  # Row 9
        [0, 0, 0, 1, 1, 0, 0, 0],  # Row 25
        [1, 0, 0, 0, 0, 0, 0, 0]   # Row 129
    ]
    # test_inputs = [0b00000000, 0b00111111, 0b11111111, 0b01100000] # left, stop, right, uturn
    expected_outputs = [0b1000, 0b0001, 0b0100, 0b0010]  # Expected output for each one
    
    for i in range(len(stop_patterns)):
        dut.ui_in.value = stop_patterns[i]
        await RisingEdge(dut.clk)  # Cycle 1 post-reset
        await RisingEdge(dut.clk)  # Cycle 2 post-reset
        cocotb.log.info(f"layer3 [7:0]:{dut.uo_out.value.binstr}")
        # cocotb.log.info(f"expected value: {bin(expected_outputs[i])}, actual value: {bin(dut.uo_out.value[4:7])}")
        # assert int(dut.uo_out.value[4:7]) == expected_outputs[i], f"Hardcoded weight test failed. Got {bin(dut.uo_out.value[4:7])}, expected {bin(expected_output[i])}"

async def test_weight_loading(dut):
    """Test dynamic weight loading through bidirectional pins"""
    cocotb.log.info("Testing weight loading")
    weights_list = [0b11110000, 0b00001111, 0b00111100, 0b11000011, 
               0b11110000, 0b00001111, 0b00111100, 0b11000011,  
               0b11110000, 0b00001111, 0b00111100, 0b11000011]
    # weights[0] <= 8'b11111111;
    # weights[1] <= 8'b00001111;
    # weights[2] <= 8'b00111100;
    # weights[3] <= 8'b11000011;
    # weights[4] <= 8'b11110000;
    # weights[5] <= 8'b00001111;
    # weights[6] <= 8'b00111100;
    # weights[7] <= 8'b11000011;
    # // Second layer: 4 neurons
    # weights[8] <= 8'b11110000;
    # weights[9] <= 8'b00001111;
    # weights[10] <= 8'b00111100;
    # weights[11] <= 8'b11000011;
    # Enable weight loading mode
    dut.uio_in.value = 0b11110000  # Set bit 3 (load_en) high
    
    # Test loading weights, cycling all 12 neurons
    for i in range(12):
        await load_weights(dut, i, weights=weights_list[i])
    
    # Verify by testing inference
    test_input = 0b11110000  # Should perfectly original value, since loaded weights are the same
    expected_output = 0b1111  # Threshold is 5 (0101), sum will be 8
    
    dut.ui_in.value = test_input
    dut.uio_in.value = 0  # Disable weight loading
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")
    cocotb.log.info(f"weight at node 0: {bin(dut.uo_out.value[4:7:-1])}")
    assert int(dut.uo_out.value[4:7:-1]) == expected_output, f"Weight loading test failed. Got {dut.uo_out.value[4:7:-1]}, expected {expected_output}"

async def load_weights(dut, neuron_idx, weights):
    """Helper function to load weights for a specific neuron"""
    # Load lower 4 bits first
    dut.uio_in.value = (weights & 0x0F) << 4 | 0b1000
    await RisingEdge(dut.clk)
    
    # Load upper 4 bits
    dut.uio_in.value = (weights >> 4) << 4 | 0b1000
    await RisingEdge(dut.clk)

    cocotb.log.info(f"Loaded weights {bin(weights)} to neuron {neuron_idx}")

async def test_network_inference(dut):
    # Simulates the complete process using python here
    cocotb.log.info("Testing network inference")
    
    # Test 10 random patterns
    for _ in range(10):
        # Generate random input
        test_input = random.randint(0, 255)
        
        # Calculate expected output (based on hardcoded weights)
        expected = calculate_expected_output(test_input)
        
        # Apply input
        dut.ui_in.value = test_input
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        
        # Verify output
        assert int(dut.uo_out.value) == expected, f"Inference failed for input {bin(test_input)}. Got {dut.uo_out.value}, expected {expected}"

def calculate_expected_output(input_val):
    """Calculate expected output based on hardcoded weights"""
    # Layer 1 weights (first 8 neurons)
    layer1_weights = [ 0b10100000, 0b01000001, 0b01111010, 0b00011000,
        0b11101101, 0b10110111, 0b01100111, 0b00111010]
    
    # Layer 2 weights (neurons 8-11)
    layer2_weights = [0b11111001, 0b01100010, 0b11110111, 0b00001111]
    
    # Threshold for all neurons is 5 (0101)
    threshold = 5
    
    # Layer 1 computation
    layer1_output = 0
    for i in range(8):
        matches = bin(input_val ^ layer1_weights[i]).count('0')
        if matches >= threshold:
            layer1_output |= (1 << i)
    
    # Layer 2 computation
    final_output = 0
    for i in range(4):
        # Compare with bits [4:7] of weights (per your code)
        weight_part = (layer2_weights[i] >> 4) & 0x0F
        input_part = layer1_output
        matches = bin(input_part ^ weight_part).count('0')
        if matches >= threshold:
            final_output |= (1 << i)
    
    return final_output