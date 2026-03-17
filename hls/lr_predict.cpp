#include <iostream>

#include "lr_predict.h"
#include "parameters.h"


void lr_predict(
    input_t input_layer[3],
    result_t layer3_out[1]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=input_layer complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=input_layer,layer3_out 
    #pragma HLS PIPELINE

    // hls-fpga-machine-learning insert load weights
#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        nnet::load_weights_from_txt<model_default_t, 3>(w2, "w2.txt");
        nnet::load_weights_from_txt<model_default_t, 1>(b2, "b2.txt");
        loaded_weights = true;    }
#endif
    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[1];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0

    nnet::dense<input_t, layer2_t, config2>(input_layer, layer2_out, w2, b2); // dense

    nnet::sigmoid<layer2_t, result_t, sigmoid_config3>(layer2_out, layer3_out); // dense_sigmoid

}

