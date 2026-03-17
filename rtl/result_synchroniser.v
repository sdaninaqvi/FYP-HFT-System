`timescale 1ns / 1ps
// result_sync - path-selective synchronisation barrier
//
// Asserts trigger_valid as soon as the SELECTED inference path
// is complete. Requires high_volatility input from compute_trigger.
//
// Calm  (σ ≤ 0.002): trigger_valid at ~390 ns  (cycle 39)
// Volatile (σ > 0.002): trigger_valid at ~1,950 ns (cycle 195)

module result_sync (
    input wire clk,
    input wire rst,              // Active-low reset

    input wire window_valid,     // Single-cycle pulse from price_buffer

    input wire f3_done,          // compute_f3 complete
    input wire f13_done,         // compute_f13 complete  
    input wire trigger_done,     // compute_trigger complete
    input wire lr_done,          // lr_predict complete
    input wire mlp_done,         // myproject (MLP) complete
    input wire high_volatility,  // NEW: from compute_trigger_0

    output reg trigger_valid
);

    // Latch done pulses - HLS ap_done may be high for only one cycle
    reg trigger_done_r;
    reg f3_done_r;
    reg lr_done_r;
    reg f13_done_r;
    reg mlp_done_r;
    reg hv_latched;              // Latched volatility decision

    reg active;

// One-cycle delay on trigger_done_r to let hv_latched settle
    reg trigger_done_delay;
    always @(posedge clk) begin
        if (!rst) trigger_done_delay <= 1'b0;
        else      trigger_done_delay <= trigger_done_r;
    end

    // Full path readiness signals - use delayed version so hv_latched is stable
    wire calm_path_ready     = trigger_done_delay && f3_done_r  && lr_done_r;
    wire volatile_path_ready = trigger_done_delay && f13_done_r && mlp_done_r;

    // Selected path is ready when the regime-appropriate path completes
    wire selected_ready = hv_latched ? volatile_path_ready : calm_path_ready;

    always @(posedge clk) begin
        if (!rst) begin
            trigger_done_r <= 1'b0;
            f3_done_r      <= 1'b0;
            lr_done_r      <= 1'b0;
            f13_done_r     <= 1'b0;
            mlp_done_r     <= 1'b0;
            hv_latched     <= 1'b0;
            active         <= 1'b0;
            trigger_valid  <= 1'b0;
        end else begin
            // Default: clear the output pulse
            trigger_valid <= 1'b0;

            if (window_valid) begin
                // New window arrived - reset all latches, begin waiting
                trigger_done_r <= 1'b0;
                f3_done_r      <= 1'b0;
                lr_done_r      <= 1'b0;
                f13_done_r     <= 1'b0;
                mlp_done_r     <= 1'b0;
                hv_latched     <= 1'b0;
                active         <= 1'b1;
            end else if (active) begin
                // Latch done signals as they arrive
                if (trigger_done) begin
                    trigger_done_r <= 1'b1;
                    hv_latched     <= high_volatility;  // Capture regime decision
                end
                if (f3_done)  f3_done_r  <= 1'b1;
                if (lr_done)  lr_done_r  <= 1'b1;
                if (f13_done) f13_done_r <= 1'b1;
                if (mlp_done) mlp_done_r <= 1'b1;

                // Assert trigger_valid as soon as the selected path is done
                if (selected_ready) begin
                    trigger_valid <= 1'b1;
                    active        <= 1'b0;
                end
            end
        end
    end

endmodule