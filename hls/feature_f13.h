#ifndef FEATURE_F13_H
#define FEATURE_F13_H

#include "ap_fixed.h"

#define WINDOW_SIZE 60
typedef ap_fixed<16,6> data_t;

void compute_f13(
    data_t price_window[WINDOW_SIZE],
    data_t features[13]
);

#endif