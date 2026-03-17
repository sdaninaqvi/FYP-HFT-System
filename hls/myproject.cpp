#include <iostream>

#include "myproject.h"
#include "parameters.h"


void myproject(
    input_t input_layer_3[13],
    result_t layer8_out[1]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=input_layer_3 complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=input_layer_3,layer8_out 
    #pragma HLS DATAFLOW

    // hls-fpga-machine-learning insert load weights
#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        nnet::load_weights_from_txt<dense_5_weight_t, 208>(w2, "w2.txt");
        nnet::load_weights_from_txt<dense_5_bias_t, 16>(b2, "b2.txt");
        nnet::load_weights_from_txt<dense_6_weight_t, 128>(w5, "w5.txt");
        nnet::load_weights_from_txt<dense_6_bias_t, 8>(b5, "b5.txt");
        nnet::load_weights_from_txt<dense_7_weight_t, 8>(w7, "w7.txt");
        nnet::load_weights_from_txt<dense_7_bias_t, 1>(b7, "b7.txt");
        loaded_weights = true;    }
#endif
    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[16];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0

    layer3_t layer3_out[16];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0

    layer5_t layer5_out[8];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0

    layer6_t layer6_out[8];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0

    layer7_t layer7_out[1];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0

    nnet::dense<input_t, layer2_t, config2>(input_layer_3, layer2_out, w2, b2); // dense_5

    nnet::relu<layer2_t, layer3_t, relu_config3>(layer2_out, layer3_out); // dense_5_relu

    nnet::dense<layer3_t, layer5_t, config5>(layer3_out, layer5_out, w5, b5); // dense_6

    nnet::relu<layer5_t, layer6_t, relu_config6>(layer5_out, layer6_out); // dense_6_relu

    nnet::dense<layer6_t, layer7_t, config7>(layer6_out, layer7_out, w7, b7); // dense_7

    nnet::sigmoid<layer7_t, result_t, sigmoid_config8>(layer7_out, layer8_out); // dense_7_sigmoid

}

