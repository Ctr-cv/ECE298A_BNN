# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.types import LogicArray

@cocotb.test()
async def test_programmable_counter(dut):
    """Test the programmable counter module"""
    
    # Start 100 KHz clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initialize inputs
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 1  # Active low reset (start deasserted)

    dut._log.info("=== Test 1: Reset Behavior ===")
    # Apply reset
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    
    # Check counter is zero after reset
    assert dut.uo_out.value == 0, "Counter not reset to zero"
    dut._log.info("Reset test passed")

    dut._log.info("=== Test 2: Counting Operation ===")
    # Let counter run for 10 cycles
    for i in range(1, 11):
        await RisingEdge(dut.clk)
        assert dut.uo_out.value == i % 256, f"Counter not incrementing correctly at cycle {i}"
    dut._log.info("Counting test passed")

    dut._log.info("=== Test 3: Load Operation ===")
    # Prepare load value (0x55) and activate load
    load_value = 0x55
    dut.ui_in.value = (1 << 0) | (load_value << 2)  # Set load bit (ui_in[0]) and data (ui_in[7:2])
    await RisingEdge(dut.clk)
    
    # Deassert load
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    
    # Verify loaded value
    assert dut.uo_out.value == load_value, f"Counter not loaded with {hex(load_value)}"
    dut._log.info("Load test passed")

    dut._log.info("=== Test 4: Output Enable ===")
    # First check output is enabled (oe_n=1 means output is enabled in our wrapper)
    assert dut.uo_out.value == load_value + 1, "Output not enabled when it should be"
    
    # Disable output (set oe_n=0 through ui_in[1])
    dut.ui_in.value = (1 << 1)
    await RisingEdge(dut.clk)
    
    # Check output is high-Z (represented as 'X' in simulation)
    assert LogicArray(dut.uo_out.value).is_X, "Output not high-Z when disabled"
    
    # Re-enable output
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    dut._log.info("Output enable test passed")

    dut._log.info("=== Test 5: Combined Operations ===")
    # Test combination of operations
    test_value = 0xAA
    dut.ui_in.value = (1 << 0) | (test_value << 2)  # Load new value
    await RisingEdge(dut.clk)
    dut.ui_in.value = 0  # Return to counting mode
    await RisingEdge(dut.clk)
    
    # Verify counting continues from loaded value
    assert dut.uo_out.value == test_value + 1, "Counter not incrementing after load"
    
    # Let it count a few more cycles
    for i in range(2, 5):
        await RisingEdge(dut.clk)
        assert dut.uo_out.value == (test_value + i) % 256, "Counter not incrementing correctly"
    
    dut._log.info("All tests passed successfully!")
