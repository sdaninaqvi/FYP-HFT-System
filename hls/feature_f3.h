#ifndef FEATURE_F3_H
#define FEATURE_F3_H

#include "ap_fixed.h"

#define WINDOW_SIZE 60
typedef ap_fixed<16,6> data_t;

// F3: Microprice, High_low_spread, MA_10
void compute_f3(
    data_t price_window[WINDOW_SIZE],
    data_t features[3]
);

#endif