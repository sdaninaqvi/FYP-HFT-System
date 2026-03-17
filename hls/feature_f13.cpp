#include "feature_f13.h"

void compute_f13(
    data_t price_window[WINDOW_SIZE],
    data_t features[13]
) {
    #pragma HLS INTERFACE ap_ctrl_hs port=return
    #pragma HLS ARRAY_PARTITION variable=price_window complete dim=1
    #pragma HLS ARRAY_PARTITION variable=features complete dim=1
    // NO PIPELINE - let it be sequential to show cost
    
    data_t close = price_window[WINDOW_SIZE-1];
    data_t prev = price_window[WINDOW_SIZE-2];
    
    // Feature 0: Microprice
    data_t high = close, low = close;
    for(int i = WINDOW_SIZE-10; i < WINDOW_SIZE; i++) {
        if(price_window[i] > high) high = price_window[i];
        if(price_window[i] < low) low = price_window[i];
    }
    features[0] = close - ((high + low) / 2);
    
    // Feature 1: High_low_spread
    features[1] = (high - low) / close;
    
    // Feature 2: MA_10
    data_t sum_10 = 0;
    for(int i = WINDOW_SIZE-10; i < WINDOW_SIZE; i++) {
        sum_10 += price_window[i];
    }
    features[2] = sum_10 / 10;
    
    // Feature 3: MACD (approximate as MA_12 - MA_26)
    data_t sum_12 = 0, sum_26 = 0;
    for(int i = WINDOW_SIZE-26; i < WINDOW_SIZE; i++) {
        if(i >= WINDOW_SIZE-12) sum_12 += price_window[i];
        sum_26 += price_window[i];
    }
    features[3] = (sum_12/12) - (sum_26/26);
    
    // Feature 4: ROC_5
    features[4] = (close - price_window[WINDOW_SIZE-6]) / price_window[WINDOW_SIZE-6];
    
    // Feature 5: ROC_10
    features[5] = (close - price_window[WINDOW_SIZE-11]) / price_window[WINDOW_SIZE-11];
    
    // Feature 6: RSI (simplified)
    data_t gains = 0, losses = 0;
    for(int i = WINDOW_SIZE-14; i < WINDOW_SIZE; i++) {
        data_t diff = price_window[i] - price_window[i-1];
        if(diff > 0) gains += diff;
        else losses += -diff;
    }
    data_t avg_gain = gains / 14;
    data_t avg_loss = losses / 14;
    features[6] = 100 - (100 / (1 + (avg_gain / (avg_loss + (data_t)0.0001))));
    
    // Feature 7: Bollinger_Pos
    data_t sum_20 = 0;
    for(int i = WINDOW_SIZE-20; i < WINDOW_SIZE; i++) {
        sum_20 += price_window[i];
    }
    data_t ma_20 = sum_20 / 20;
    
    data_t var_sum = 0;
    for(int i = WINDOW_SIZE-20; i < WINDOW_SIZE; i++) {
        data_t diff = price_window[i] - ma_20;
        var_sum += diff * diff;
    }
    data_t std_20 = var_sum / 20;  // Simplified (should be sqrt)
    features[7] = (close - ma_20) / (2 * std_20 + (data_t)0.0001);
    
    // Feature 8: ATR (simplified as high-low range)
    features[8] = (high - low);
    
    // Feature 9-12: Simplified placeholders
    // (Volume features - we don't have volume in price_window)
    // Use price-based proxies
    features[9] = (close - price_window[WINDOW_SIZE-5]) / 5;  // Velocity
    features[10] = features[9] - features[4];  // Acceleration proxy
    features[11] = (close > ma_20) ? (data_t)1.0 : (data_t)0.0;  // Above/below MA
    features[12] = std_20;  // Volatility
}