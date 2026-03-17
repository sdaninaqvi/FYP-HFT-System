`timescale 1ns / 1ps

module pipeline_reg_208 (
    input wire clk,
    input wire [207:0] data_in,
    output reg [207:0] data_out
);
    
    // Simple 1-cycle pipeline register
    always @(posedge clk) begin
        data_out <= data_in;
    end
    
endmodule