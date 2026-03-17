`timescale 1ns / 1ps

module prediction_mux (
    input wire clk,
    input wire rst,               
    input wire [15:0] in_lr,      // LR prediction (16-bit)
    input wire [15:0] in_mlp,     // MLP prediction (16-bit) - WAS 32, NOW 16!
    input wire high_volatility,   
    input wire trigger_valid,     
    output reg [15:0] prediction, // Final prediction (16-bit) - MATCHES MODELS
    output reg path_used          
);

always @(posedge clk) begin
    if (!rst) begin
        prediction <= 16'd0;
        path_used  <= 1'b0;       
    end else begin
        if (trigger_valid) begin
            if (high_volatility) begin
                prediction <= in_mlp;   // Direct 16-bit assignment
                path_used  <= 1'b1;     // MLP Path
            end else begin
                prediction <= in_lr;    // Direct 16-bit assignment
                path_used  <= 1'b0;     // LR Path
            end
        end
        // If trigger_valid is low, we hold the previous trade signal
    end
end

endmodule