`timescale 1ns / 1ps

module board_display (
    input wire clk,
    input wire rst,              // active-low (same as prediction_mux, result_sync)
    
    // tapped from existing block design nets - observation only
    input wire window_valid,
    input wire trigger_valid,
    input wire high_volatility,
    input wire path_used,
    input wire [15:0] prediction,
    
    // new top-level outputs
    output reg [6:0] seg,        // seven-segment cathodes CA-CG (active low)
    output reg [3:0] an,         // seven-segment anodes AN3-AN0 (active low)
    output reg dp,               // decimal point (active low)
    output reg [6:0] led_upper   // LD14 down to LD8
);

    // =========================================================================
    // Latency counter - counts cycles between window_valid and trigger_valid
    // =========================================================================
    reg [15:0] cycle_counter;
    reg [15:0] latency_hold;     // frozen result for display
    reg counting;
    
    always @(posedge clk) begin
        if (!rst) begin
            cycle_counter <= 0;
            latency_hold  <= 0;
            counting      <= 0;
        end else begin
            if (window_valid) begin
                cycle_counter <= 0;
                counting      <= 1;
            end else if (counting) begin
                cycle_counter <= cycle_counter + 1;
                if (trigger_valid) begin
                    latency_hold <= cycle_counter + 1;
                    counting     <= 0;
                end
            end
        end
    end

    // =========================================================================
    // Prediction latch - holds prediction value after trigger_valid
    // =========================================================================
    reg [15:0] pred_hold;
    reg        path_hold;
    reg        hv_hold;
    
    always @(posedge clk) begin
        if (!rst) begin
            pred_hold <= 0;
            path_hold <= 0;
            hv_hold   <= 0;
        end else if (trigger_valid) begin
            pred_hold <= prediction;
            path_hold <= path_used;
            hv_hold   <= high_volatility;
        end
    end

    // =========================================================================
    // Rolling history - last 4 model decisions on LD11-LD8
    // =========================================================================
    reg [3:0] history;
    reg       prev_trigger_valid;
    
    always @(posedge clk) begin
        if (!rst) begin
            history             <= 4'b0000;
            prev_trigger_valid  <= 0;
        end else begin
            prev_trigger_valid <= trigger_valid;
            // shift on rising edge of trigger_valid
            if (trigger_valid && !prev_trigger_valid) begin
                history <= {history[2:0], path_used};
            end
        end
    end

    // =========================================================================
    // Inference counter - total windows and passes (self-check)
    // =========================================================================
    reg [7:0] total_count;
    reg [7:0] inference_active_count;  // just counts total inferences
    
    always @(posedge clk) begin
        if (!rst) begin
            total_count <= 0;
        end else begin
            if (trigger_valid && !prev_trigger_valid) begin
                total_count <= total_count + 1;
            end
        end
    end

    // =========================================================================
    // LED upper bank - LD14 down to LD8
    // =========================================================================
    // LD14: pipeline active (inference in progress)
    // LD13: high volatility flag (latched)
    // LD12: trigger_valid latched (result ready)
    // LD11-LD8: rolling history (newest at LD8)
    
    reg pipeline_active;
    reg result_ready;
    
    always @(posedge clk) begin
        if (!rst) begin
            pipeline_active <= 0;
            result_ready    <= 0;
        end else begin
            if (window_valid)
                pipeline_active <= 1;
            if (trigger_valid)
                pipeline_active <= 0;
            
            if (trigger_valid)
                result_ready <= 1;
            if (window_valid)
                result_ready <= 0;
        end
    end
    
    always @(*) begin
        led_upper[6] = pipeline_active;   // LD14
        led_upper[5] = hv_hold;           // LD13
        led_upper[4] = result_ready;      // LD12
        led_upper[3] = history[3];        // LD11 (oldest)
        led_upper[2] = history[2];        // LD10
        led_upper[1] = history[1];        // LD9
        led_upper[0] = history[0];        // LD8  (newest)
    end

    // =========================================================================
    // Seven-segment display - shows latency in decimal (4 digits)
    // =========================================================================
    
    // BCD conversion for latency_hold (max 9999)
    reg [3:0] digit3, digit2, digit1, digit0;
    reg [15:0] bcd_tmp;
    
    always @(*) begin
        bcd_tmp = latency_hold;
        digit3  = bcd_tmp / 1000;
        digit2  = (bcd_tmp / 100) % 10;
        digit1  = (bcd_tmp / 10) % 10;
        digit0  = bcd_tmp % 10;
    end
    
    // Refresh counter - cycle through 4 digits at ~1kHz
    // 100MHz / 2^17 = ~763 Hz per digit, 4 digits = ~190 Hz refresh
    reg [16:0] refresh_counter;
    wire [1:0] active_digit;
    
    always @(posedge clk) begin
        if (!rst)
            refresh_counter <= 0;
        else
            refresh_counter <= refresh_counter + 1;
    end
    
    assign active_digit = refresh_counter[16:15];
    
    // Digit select and segment decode
    reg [3:0] current_digit_val;
    
    always @(*) begin
        case (active_digit)
            2'b00: begin
                an = 4'b1110;   // AN0 active (rightmost)
                current_digit_val = digit0;
                dp = 1'b1;      // no decimal point
            end
            2'b01: begin
                an = 4'b1101;   // AN1
                current_digit_val = digit1;
                dp = 1'b1;
            end
            2'b10: begin
                an = 4'b1011;   // AN2
                current_digit_val = digit2;
                dp = 1'b1;
            end
            2'b11: begin
                an = 4'b0111;   // AN3 (leftmost)
                current_digit_val = digit3;
                // decimal point on leftmost digit indicates path:
                // DP ON (low) = MLP, DP OFF (high) = LR
                dp = ~path_hold;
            end
            default: begin
                an = 4'b1111;
                current_digit_val = 4'd0;
                dp = 1'b1;
            end
        endcase
    end
    
    // Seven-segment encoder (active low: 0 = segment ON)
    //   segment mapping:  CA=seg[6], CB=seg[5], CC=seg[4],
    //                     CD=seg[3], CE=seg[2], CF=seg[1], CG=seg[0]
    always @(*) begin
        case (current_digit_val)
            4'd0: seg = 7'b0000001;
            4'd1: seg = 7'b1001111;
            4'd2: seg = 7'b0010010;
            4'd3: seg = 7'b0000110;
            4'd4: seg = 7'b1001100;
            4'd5: seg = 7'b0100100;
            4'd6: seg = 7'b0100000;
            4'd7: seg = 7'b0001111;
            4'd8: seg = 7'b0000000;
            4'd9: seg = 7'b0000100;
            default: seg = 7'b1111111;  // blank
        endcase
    end

endmodule
