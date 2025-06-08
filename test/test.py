# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_tt_um_counter(dut):
    dut._log.info("Starting tt_um_counter test")

    # Clock setup: 10 us period (100 kHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset sequence
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.uio_oe.value = 0
    dut.uio_out.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # After reset, counter should be zero
    dut._log.info("Checking counter reset")
    assert dut.uo_out.value.integer == 0, f"Expected counter 0 after reset, got {dut.uo_out.value.integer}"

    # Load a value into the counter: load = 1 (bit 0), output_en=1 (bit1), count_up don't care here
    # Load data: 5 << 2 = 20, so ui_in bits [7:3] = 5 (0b00101)
    # ui_in: bit7..3=0b00101, bit2=0 (count direction), bit1=1 (output enable), bit0=1 (load)
    load_value = 5
    ui_in_val = (load_value << 3) | (1 << 1) | (1 << 0)  # bits 7:3 = load_value, bit1=output_en=1, bit0=load=1
    dut._log.info(f"Loading value {load_value} (effective counter load = {load_value << 2})")
    dut.ui_in.value = ui_in_val
    await ClockCycles(dut.clk, 2)  # Wait 2 cycles to register load

    # Check counter loaded value (shifted left by 2)
    expected_load = load_value << 2
    actual = dut.uo_out.value.integer
    assert actual == expected_load, f"Counter load failed: expected {expected_load}, got {actual}"

    # Count up for 3 cycles: load=0, output_en=1, count_up=1
    dut.ui_in.value = (1 << 2) | (1 << 1)  # bit2=count_up=1, bit1=output_en=1, bit0=0 load
    dut._log.info("Counting up for 3 cycles")
    await ClockCycles(dut.clk, 3)

    expected_count = expected_load + 3
    actual = dut.uo_out.value.integer
    assert actual == expected_count, f"Count up failed: expected {expected_count}, got {actual}"

    # Count down for 2 cycles: load=0, output_en=1, count_up=0
    dut.ui_in.value = (0 << 2) | (1 << 1)  # bit2=count_up=0, bit1=output_en=1, bit0=0 load
    dut._log.info("Counting down for 2 cycles")
    await ClockCycles(dut.clk, 2)

    expected_count -= 2
    actual = dut.uo_out.value.integer
    assert actual == expected_count, f"Count down failed: expected {expected_count}, got {actual}"

    # Disable output enable: output_en=0, counter keeps counting but output is high Z
    dut.ui_in.value = 0  # all bits 0: load=0, output_en=0, count_up=0
    dut._log.info("Output disabled (tri-state), counter should decrement but output is Z")
    await ClockCycles(dut.clk, 1)
    # uo_out should be 'Z' (high impedance)
    assert dut.uo_out.value.is_resolvable is False, "Output enable disabled, uo_out should be high impedance"

    # Enable output again, verify counter decremented
    dut.ui_in.value = (0 << 2) | (1 << 1)  # output_en=1, count_up=0
    await ClockCycles(dut.clk, 1)
    expected_count -= 1
    actual = dut.uo_out.value.integer
    assert actual == expected_count, f"Counter value mismatch after re-enabling output: expected {expected_count}, got {actual}"

    dut._log.info("All tests passed!")
