/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_tlc(   
    input  wire [7:0] ui_in,   // 8-bit input
    output wire [7:0] uo_out,  // 8-bit output
    input  wire [7:0] uio_in,  // 8-bit bidirectional (for advanced usage)
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,  
    input  wire clk,           // Clock signal
    input  wire rst_n          // Active-low reset
);

    // Mapping TinyTapeout inputs to your signals
    wire C    = ui_in[0];  // Sensor input
    wire clk  = ui_in[1];  // Clock
    wire rst_n = ui_in[2]; // Active-low reset
    wire ena  = ui_in[3];  // Enable

    reg [2:0] light_highway;
    reg [2:0] light_farm;

    // State encoding
    parameter HGRE_FRED = 2'b00,  // Highway Green/Farm Red
              HYEL_FRED = 2'b01,  // Highway Yellow/Farm Red
              HRED_FGRE = 2'b10,  // Highway Red/Farm Green
              HRED_FYEL = 2'b11;  // Highway Red/Farm Yellow

    reg [1:0] state, next_state;
  reg [3:0] counter;
    reg delay_10s, delay_3s;

    // State transition logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= HGRE_FRED;
            counter <= 0;
        end else begin
            state <= next_state;
          counter <= (counter >= 4'd13) ? 0 : counter + 1;
        end
    end

   // Timing control
    always @(posedge clk) begin
      delay_10s <= (counter == 4'd13);  
      delay_3s  <= (counter == 4'd3);  
    end

    // FSM combinational logic
    always @(*) begin
        case(state)
            HGRE_FRED: begin
                light_highway = 3'b001;
                light_farm = 3'b100;
                next_state = C ? HYEL_FRED : HGRE_FRED;
            end
            HYEL_FRED: begin
                light_highway = 3'b010;
                light_farm = 3'b100;
                next_state = (delay_3s) ? HRED_FGRE : HYEL_FRED;
            end
            HRED_FGRE: begin
                light_highway = 3'b100;
                light_farm = 3'b001;
                next_state = (delay_10s) ? HRED_FYEL : HRED_FGRE;
            end
            HRED_FYEL: begin
                light_highway = 3'b100;
                light_farm = 3'b010;
                next_state = (delay_3s) ? HGRE_FRED : HRED_FYEL;
            end
        endcase
    end

endmodule
