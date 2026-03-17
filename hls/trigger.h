#ifndef TRIGGER_H
#define TRIGGER_H

#include "ap_fixed.h"

#define WINDOW_SIZE 60
typedef ap_fixed<16,6> data_t;

void compute_trigger(
    data_t price_window[WINDOW_SIZE],
    bool* high_volatility,
    data_t* spread_out
);

#endif