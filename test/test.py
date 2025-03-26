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

    # Initialize signals
    dut.ena.value = 1  # REQUIRED: Enable the module
    dut.rst_n.value = 0
    dut.ui_in.value = 0  # C sensor is at ui_in[2]

    # Reset sequence
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Test initial state (HGRE_FRED)
    await RisingEdge(dut.clk)
    assert dut.uo_out[0].value == 0b001, "Highway should be Green (001)"
    assert dut.uo_out[1].value == 0b100, "Farm should be Red (100)"

    # Test sensor activation after 10 cycles
    dut.ui_in.value = 0b00000100  # Set C (ui_in[2]) to 1
    await ClockCycles(dut.clk, 10)
    
    # Verify transition to HYEL_FRED (Highway Yellow)
    assert dut.uo_out[0].value == 0b010, "Highway should be Yellow (010)"
    
    # Wait 3 cycles for HYEL_FRED -> HRED_FGRE transition
    await ClockCycles(dut.clk, 3)
    assert dut.uo_out[0].value == 0b100, "Highway should be Red (100)"
    assert dut.uo_out[1].value == 0b001, "Farm should be Green (001)"

    # Wait 10 cycles for HRED_FGRE -> HRED_FYEL transition
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out[1].value == 0b010, "Farm should be Yellow (010)"

    # Wait 3 cycles for HRED_FYEL -> HGRE_FRED transition
    await ClockCycles(dut.clk, 3)
    assert dut.uo_out[0].value == 0b001, "Highway should return to Green (001)"
    assert dut.uo_out[1].value == 0b100, "Farm should return to Red (100)"

    dut._log.info("Test completed successfully")
