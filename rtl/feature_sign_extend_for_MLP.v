`timescale 1ns / 1ps

// feature_concatenator_13
//
// Takes 13 x 16-bit features from compute_f13 (ap_fixed<16,6>)
// and bundles them into a single 208-bit bus for myproject_0.
// (13 features * 16 bits = 208 bits total)

module feature_sign_extend_13 (
    input  wire [15:0] feature_0,
    input  wire [15:0] feature_1,
    input  wire [15:0] feature_2,
    input  wire [15:0] feature_3,
    input  wire [15:0] feature_4,
    input  wire [15:0] feature_5,
    input  wire [15:0] feature_6,
    input  wire [15:0] feature_7,
    input  wire [15:0] feature_8,
    input  wire [15:0] feature_9,
    input  wire [15:0] feature_10,
    input  wire [15:0] feature_11,
    input  wire [15:0] feature_12,
    
    output wire [207:0] extended_out
);

    // No sign extension needed! Just direct concatenation.
    assign extended_out[15:0]    = feature_0;
    assign extended_out[31:16]   = feature_1;
    assign extended_out[47:32]   = feature_2;
    assign extended_out[63:48]   = feature_3;
    assign extended_out[79:64]   = feature_4;
    assign extended_out[95:80]   = feature_5;
    assign extended_out[111:96]  = feature_6;
    assign extended_out[127:112] = feature_7;
    assign extended_out[143:128] = feature_8;
    assign extended_out[159:144] = feature_9;
    assign extended_out[175:160] = feature_10;
    assign extended_out[191:176] = feature_11;
    assign extended_out[207:192] = feature_12;

endmodule