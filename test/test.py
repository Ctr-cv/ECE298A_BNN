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
    await test_weight_loading(dut)

async def test_hardcoded_weights(dut):
    # Test initial hard-coded weights
    cocotb.log.info(f"Testing hardcoded weights")
    
    # A single test 0b11110000 is provided, more could be added later
    # Test pattern that should activate neuron 0 (weights = 11110000)
    stop_patterns = [
        0b00000000,  
        0b00000001,  
        0b00000010, 
        0b00011011
    ]

    right_patterns = [
        0b10000111,
        0b10001110,
    ]

    forward_patterns = [
        0b00011101,
        0b00011100,
        0b00111000,
        0b00011000
    ]

    left_patterns = [
        0b01100000,
        0b11110000
    ]
    
    for i in range(len(stop_patterns)):
        dut.ui_in.value = stop_patterns[i]
        await RisingEdge(dut.clk)  # Cycle 1 post-reset
        await RisingEdge(dut.clk)  # Cycle 2 post-rese
        await RisingEdge(dut.clk)  # Cycle 3 just in case
        # cocotb.log.info(f"index:{format(i, '08b')} layer3 [7:0]:{dut.uo_out.value[4:7]}")
        assert int(dut.uo_out.value[4:7]) == 0b1000, f"Hardcoded weight test failed. Got {bin(dut.uo_out.value[4:7])}, expected 0b1000"
    
    for i in range(len(right_patterns)):
        dut.ui_in.value = right_patterns[i]
        await RisingEdge(dut.clk)  # Cycle 1 post-reset
        await RisingEdge(dut.clk)  # Cycle 2 post-rese
        await RisingEdge(dut.clk)  # Cycle 3 just in case
        # cocotb.log.info(f"index:{format(i, '08b')} layer3 [7:0]:{dut.uo_out.value[4:7]}")
        assert int(dut.uo_out.value[4:7]) == 0b0100, f"Hardcoded weight test failed. Got {bin(dut.uo_out.value[4:7])}, expected 0b0100"
    
    for i in range(len(forward_patterns)):
        dut.ui_in.value = forward_patterns[i]
        await RisingEdge(dut.clk)  # Cycle 1 post-reset
        await RisingEdge(dut.clk)  # Cycle 2 post-rese
        await RisingEdge(dut.clk)  # Cycle 3 just in case
        # cocotb.log.info(f"index:{format(i, '08b')} layer3 [7:0]:{dut.uo_out.value[4:7]}")
        assert int(dut.uo_out.value[4:7]) == 0b0010, f"Hardcoded weight test failed. Got {bin(dut.uo_out.value[4:7])}, expected 0b0010"

    for i in range(len(left_patterns)):
        dut.ui_in.value = left_patterns[i]
        await RisingEdge(dut.clk)  # Cycle 1 post-reset
        await RisingEdge(dut.clk)  # Cycle 2 post-rese
        await RisingEdge(dut.clk)  # Cycle 3 just in case
        # cocotb.log.info(f"index:{format(i, '08b')} layer3 [7:0]:{dut.uo_out.value[4:7]}")
        assert int(dut.uo_out.value[4:7]) == 0b0001, f"Hardcoded weight test failed. Got {bin(dut.uo_out.value[4:7])}, expected 0b0001"


async def test_weight_loading(dut):
    """Test dynamic weight loading through bidirectional pins"""
    cocotb.log.info("Testing weight loading")
    weights_list = [0b11110000, 0b00001111, 0b00111100, 0b11000011, 
               0b11110000, 0b00001111, 0b00111100, 0b11000011,  
               0b11110000, 0b00001111, 0b00111100, 0b11000011]
    dut.uio_in.value = 0b11110000  # Set bit 3 (load_en) high
    
    # Test loading weights, cycling all 12 neurons
    for i in range(12):
        await load_weights(dut, i, weights=weights_list[i])
    
    # Verify by testing inference
    test_input = 0b11110000  # Should perfectly original value, since loaded weights are the same
    expected_output = 0b0000  # Threshold is 5 (0101), sum will be 8
    
    dut.ui_in.value = test_input
    dut.uio_in.value = 0  # Disable weight loading
    await RisingEdge(dut.clk)  # Wait clock 1
    await RisingEdge(dut.clk)  # Wait clock 2
    await RisingEdge(dut.clk)  # Wait clock 3
    # cocotb.log.info(f"layer3 [7:0]:{dut.uo_out.value.binstr}")
    assert int(dut.uo_out.value[4:7]) == expected_output, f"Weight loading test failed. Got {dut.uo_out.value[4:7]}, expected {expected_output}"

async def load_weights(dut, neuron_idx, weights):
    """Helper function to load weights for a specific neuron"""
    # Load lower 4 bits first
    dut.uio_in.value = (weights & 0x0F) << 4 | 0b1000
    await RisingEdge(dut.clk)
    
    # Load upper 4 bits
    dut.uio_in.value = (weights >> 4) << 4 | 0b1000
    await RisingEdge(dut.clk)

    cocotb.log.info(f"Loaded weights {bin(weights)} to neuron {neuron_idx}")