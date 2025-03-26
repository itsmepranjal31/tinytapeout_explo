# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_traffic_light(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 0
    dut.C.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test traffic light behavior")

    # Test initial state (HGRE_FRED)
    await RisingEdge(dut.clk)
    assert dut.light_highway.value == 0b001, "Initial state: Highway should be Green"
    assert dut.light_farm.value == 0b100, "Initial state: Farm should be Red"

    # Wait for 10 cycles and check if still in HGRE_FRED state
    await ClockCycles(dut.clk, 10)
    assert dut.light_highway.value == 0b001, "Should still be in HGRE_FRED state"

    # Activate sensor
    dut.C.value = 1
    await RisingEdge(dut.clk)
    assert dut.light_highway.value == 0b010, "Should transition to HYEL_FRED state"

    # Wait for 3 cycles for HYEL_FRED state
    await ClockCycles(dut.clk, 3)
    assert dut.light_highway.value == 0b100, "Should transition to HRED_FGRE state"
    assert dut.light_farm.value == 0b001, "Farm should be Green"

    # Wait for 10 cycles for HRED_FGRE state
    await ClockCycles(dut.clk, 10)
    assert dut.light_highway.value == 0b100, "Highway should still be Red"
    assert dut.light_farm.value == 0b010, "Should transition to HRED_FYEL state"

    # Wait for 3 cycles to return to initial state
    await ClockCycles(dut.clk, 3)
    assert dut.light_highway.value == 0b001, "Should return to HGRE_FRED state"
    assert dut.light_farm.value == 0b100, "Farm should be Red again"

    dut._log.info("Test completed")
