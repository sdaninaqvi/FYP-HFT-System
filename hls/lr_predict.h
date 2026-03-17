#ifndef LR_PREDICT_H_
#define LR_PREDICT_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "hls_stream.h"

#include "defines.h"


// Prototype of top level function for C-synthesis
void lr_predict(
    input_t input_layer[3],
    result_t layer3_out[1]
);

// hls-fpga-machine-learning insert emulator-defines


#endif
