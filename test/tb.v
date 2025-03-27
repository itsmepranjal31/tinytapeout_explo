`timescale 1ns/1ps

module tb_traffic();

    // Signals
    reg clk;
    reg rst_n;
    reg sensor;
    wire [2:0] light_highway;
    wire [2:0] light_farm;

    // Instantiate DUT
    traffic_light dut (
        .light_highway(light_highway),
        .light_farm(light_farm),
        .C(sensor),
        .clk(clk),
        .rst_n(rst_n)
    );

    // Clock generation (10ns period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Reset sequence
    initial begin
        rst_n = 0;
        #20 rst_n = 1;
    end

    // Test stimulus
    initial begin
        	 sensor = 0;
        #40  sensor = 1;   // Activate sensor
        #20  sensor = 0;
        #180 sensor = 1;
      	#20  sensor = 0;
        #300 $finish;
    end

    // Waveform dumping
    initial begin
        $dumpfile("traffic.vcd");
        $dumpvars(0, tb_traffic);
    end

endmodule
