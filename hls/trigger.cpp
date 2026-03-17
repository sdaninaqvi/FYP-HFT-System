#include "trigger.h"

void compute_trigger(
    data_t price_window[WINDOW_SIZE],
    bool* high_volatility,
    data_t* spread_out
) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS ARRAY_PARTITION variable=price_window complete dim=1
    #pragma HLS INTERFACE mode=ap_vld port=high_volatility
    #pragma HLS INTERFACE mode=ap_vld port=spread_out

    // Remove ARRAY_PARTITION — let HLS use BRAM/sequential access
    // Remove PIPELINE II=1 — sequential loop is fine, runs in parallel anyway
    // Remove UNROLL — single comparator reused across 60 cycles instead of 60 instances

    data_t high  = price_window[0];
    data_t low   = price_window[0];
    data_t close = price_window[WINDOW_SIZE - 1];

    for (int i = 1; i < WINDOW_SIZE; i++) {
        #pragma HLS PIPELINE II=1
        if (price_window[i] > high) high = price_window[i];
        if (price_window[i] < low)  low  = price_window[i];
    }

    data_t spread = (high - low) / close;
    *spread_out   = spread;

    const data_t THRESHOLD = (data_t)0.002;
    *high_volatility = (spread > THRESHOLD);
}