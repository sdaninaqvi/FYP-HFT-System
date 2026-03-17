#include "feature_f3.h"

void compute_f3(
    data_t price_window[WINDOW_SIZE],
    data_t features[3]
) {
    #pragma HLS INTERFACE mode=ap_ctrl_hs port=return
    #pragma HLS ARRAY_PARTITION variable=price_window complete dim=1
    #pragma HLS ARRAY_PARTITION variable=features complete dim=1
    // Pipeline for throughput
    #pragma HLS PIPELINE II=1

    data_t close = price_window[WINDOW_SIZE-1];
    data_t high = price_window[WINDOW_SIZE-1];
    data_t low = price_window[WINDOW_SIZE-1];

    // Find high/low over last 10 ticks (approximate)
    for(int i = WINDOW_SIZE-10; i < WINDOW_SIZE; i++) {
        #pragma HLS UNROLL
        if(price_window[i] > high) high = price_window[i];
        if(price_window[i] < low) low = price_window[i];
    }

    // Feature 0: Microprice (Simplified)
    features[0] = close - ((high + low) / (data_t)2.0);

    // Feature 1: High_low_spread
    features[1] = (high - low) / close;

    // Feature 2: MA_10
    data_t sum = 0;
    for(int i = WINDOW_SIZE-10; i < WINDOW_SIZE; i++) {
        #pragma HLS UNROLL
        sum += price_window[i];
    }
    features[2] = sum / (data_t)10.0;
}