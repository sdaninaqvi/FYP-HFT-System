`timescale 1ns / 1ps
module vld_delay (
    input wire clk,
    input wire vld_in,
    output reg vld_out
);
    always @(posedge clk) begin
        vld_out <= vld_in;
    end
endmodule
