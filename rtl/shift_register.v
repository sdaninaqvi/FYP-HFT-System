`timescale 1ns / 1ps

// FIXED price_buffer: outputs [15:0] to match HLS ap_fixed<16,6> port widths
// 
// BUG #2 FIX: HLS modules (compute_trigger, compute_f3, compute_f13) all have
// 16-bit price_window inputs. The old 32-bit outputs caused Vivado to silently
// truncate to the lower 16 bits, corrupting the data.
//
// Now stores 32-bit internally (for UART compatibility) but outputs lower 16 bits.
// Test hex files must contain ap_fixed<16,6> values in the lower 16 bits.

module price_buffer (
    input wire clk,
    input wire rst,
    input wire [31:0] new_price,
    input wire price_valid,
    input wire buffer_ready,
    
    // *** CHANGED: 16-bit outputs to match HLS port widths ***
    output wire [15:0] price_0,
    output wire [15:0] price_1,
    output wire [15:0] price_2,
    output wire [15:0] price_3,
    output wire [15:0] price_4,
    output wire [15:0] price_5,
    output wire [15:0] price_6,
    output wire [15:0] price_7,
    output wire [15:0] price_8,
    output wire [15:0] price_9,
    output wire [15:0] price_10,
    output wire [15:0] price_11,
    output wire [15:0] price_12,
    output wire [15:0] price_13,
    output wire [15:0] price_14,
    output wire [15:0] price_15,
    output wire [15:0] price_16,
    output wire [15:0] price_17,
    output wire [15:0] price_18,
    output wire [15:0] price_19,
    output wire [15:0] price_20,
    output wire [15:0] price_21,
    output wire [15:0] price_22,
    output wire [15:0] price_23,
    output wire [15:0] price_24,
    output wire [15:0] price_25,
    output wire [15:0] price_26,
    output wire [15:0] price_27,
    output wire [15:0] price_28,
    output wire [15:0] price_29,
    output wire [15:0] price_30,
    output wire [15:0] price_31,
    output wire [15:0] price_32,
    output wire [15:0] price_33,
    output wire [15:0] price_34,
    output wire [15:0] price_35,
    output wire [15:0] price_36,
    output wire [15:0] price_37,
    output wire [15:0] price_38,
    output wire [15:0] price_39,
    output wire [15:0] price_40,
    output wire [15:0] price_41,
    output wire [15:0] price_42,
    output wire [15:0] price_43,
    output wire [15:0] price_44,
    output wire [15:0] price_45,
    output wire [15:0] price_46,
    output wire [15:0] price_47,
    output wire [15:0] price_48,
    output wire [15:0] price_49,
    output wire [15:0] price_50,
    output wire [15:0] price_51,
    output wire [15:0] price_52,
    output wire [15:0] price_53,
    output wire [15:0] price_54,
    output wire [15:0] price_55,
    output wire [15:0] price_56,
    output wire [15:0] price_57,
    output wire [15:0] price_58,
    output wire [15:0] price_59,
    
    output reg window_valid
);

    //=========================================================================
    // Internal Storage (still 32-bit for UART compatibility)
    //=========================================================================
    reg [31:0] prices [0:59];
    reg prev_buffer_ready;
    
    //=========================================================================
    // Shift Register + Edge Detection Logic
    //=========================================================================
    integer i;
    
    always @(posedge clk) begin
        if (rst) begin
            // Reset all prices
            for (i = 0; i < 60; i = i + 1) begin
                prices[i] <= 32'd0;
            end
            window_valid <= 0;
            prev_buffer_ready <= 0;
        end else begin
            // Capture previous buffer_ready
            prev_buffer_ready <= buffer_ready;
            
            // Generate single-cycle pulse on rising edge
            if (buffer_ready && !prev_buffer_ready) begin
                window_valid <= 1;
            end else begin
                window_valid <= 0;
            end
            
            // Shift operation
            if (price_valid) begin
                for (i = 0; i < 59; i = i + 1) begin
                    prices[i] <= prices[i+1];
                end
                prices[59] <= new_price;
            end
        end
    end
    
    //=========================================================================
    // Output Assignments - lower 16 bits to match HLS ap_fixed<16,6>
    //=========================================================================
    assign price_0  = prices[0][15:0];
    assign price_1  = prices[1][15:0];
    assign price_2  = prices[2][15:0];
    assign price_3  = prices[3][15:0];
    assign price_4  = prices[4][15:0];
    assign price_5  = prices[5][15:0];
    assign price_6  = prices[6][15:0];
    assign price_7  = prices[7][15:0];
    assign price_8  = prices[8][15:0];
    assign price_9  = prices[9][15:0];
    assign price_10 = prices[10][15:0];
    assign price_11 = prices[11][15:0];
    assign price_12 = prices[12][15:0];
    assign price_13 = prices[13][15:0];
    assign price_14 = prices[14][15:0];
    assign price_15 = prices[15][15:0];
    assign price_16 = prices[16][15:0];
    assign price_17 = prices[17][15:0];
    assign price_18 = prices[18][15:0];
    assign price_19 = prices[19][15:0];
    assign price_20 = prices[20][15:0];
    assign price_21 = prices[21][15:0];
    assign price_22 = prices[22][15:0];
    assign price_23 = prices[23][15:0];
    assign price_24 = prices[24][15:0];
    assign price_25 = prices[25][15:0];
    assign price_26 = prices[26][15:0];
    assign price_27 = prices[27][15:0];
    assign price_28 = prices[28][15:0];
    assign price_29 = prices[29][15:0];
    assign price_30 = prices[30][15:0];
    assign price_31 = prices[31][15:0];
    assign price_32 = prices[32][15:0];
    assign price_33 = prices[33][15:0];
    assign price_34 = prices[34][15:0];
    assign price_35 = prices[35][15:0];
    assign price_36 = prices[36][15:0];
    assign price_37 = prices[37][15:0];
    assign price_38 = prices[38][15:0];
    assign price_39 = prices[39][15:0];
    assign price_40 = prices[40][15:0];
    assign price_41 = prices[41][15:0];
    assign price_42 = prices[42][15:0];
    assign price_43 = prices[43][15:0];
    assign price_44 = prices[44][15:0];
    assign price_45 = prices[45][15:0];
    assign price_46 = prices[46][15:0];
    assign price_47 = prices[47][15:0];
    assign price_48 = prices[48][15:0];
    assign price_49 = prices[49][15:0];
    assign price_50 = prices[50][15:0];
    assign price_51 = prices[51][15:0];
    assign price_52 = prices[52][15:0];
    assign price_53 = prices[53][15:0];
    assign price_54 = prices[54][15:0];
    assign price_55 = prices[55][15:0];
    assign price_56 = prices[56][15:0];
    assign price_57 = prices[57][15:0];
    assign price_58 = prices[58][15:0];
    assign price_59 = prices[59][15:0];

endmodule