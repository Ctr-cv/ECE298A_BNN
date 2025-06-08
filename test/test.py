# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_tt_um_counter(dut):
    dut._log.info("Start test for tt_um_counter")

    # Set up the clock: 100 kHz → 10 us period
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Apply reset
    dut._log.info("Apply reset")
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1

    # Enable output to safely read uo_out
    dut._log.info("Enable output to check reset value")
    dut.ui_in.value = 0b00000010  # output_en = 1
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value.integer == 0, f"Expected counter 0 after reset, got {dut.uo_out.value}"

    # Load value 40 (5 << 3)
    dut._log.info("Load 16 into the counter")
    dut.ui_in.value = 0b10110000  # load=1, output_en=0, count_up=1, data=0b10101 → 0b00010101 = 16
    await ClockCycles(dut.clk, 1)

    # Enable output to read value
    dut.ui_in.value = 0b01100000  # output_en = 1
    await ClockCycles(dut.clk, 1)

    assert dut.uo_out.value.integer == 16, f"Expected counter to be 16 after load, got {dut.uo_out.value}"

    # Count up 3 times
    dut._log.info("Count up for 3 cycles")
    dut.ui_in.value = 0b01100000  # load=0, output_en=1, count_up=1
    await ClockCycles(dut.clk, 3)

    assert dut.uo_out.value.integer == 19, f"Expected counter 19 after 3 up counts, got {dut.uo_out.value}"

    # Count down for 2 cycles
    dut._log.info("Count down for 2 cycles")
    dut.ui_in.value = 0b01000000  # count_up = 0, output_en = 1
    await ClockCycles(dut.clk, 2)

    assert dut.uo_out.value.integer == 17, f"Expected counter 17 after 2 down counts, got {dut.uo_out.value}"

    dut._log.info("Test completed successfully.")
