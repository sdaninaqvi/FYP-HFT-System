# Custom Hardware Logic (Verilog)

This directory contains the hand-written Verilog RTL that glues the HLS IP cores into a sub-microsecond parallel pipeline. 

**Core Modules:**
* `price_buffer.v`: A shift register maintaining the 60-tick window. *(Includes a major fix to resolve a Vivado 32-bit to 16-bit AXI stream truncation bug).*
* `trigger_compute.v`: Calculates market volatility in **330ns**—outpacing the inference models to ensure zero-delay routing.
* `path_selective_synchroniser.v`: Replaces standard fixed-delay logic. It uses the trigger to dynamically gate the `done` signals, allowing the calm pathway to exit in 950ns without waiting for the 1,190ns MLP.
* `prediction_mux.v`: The final multiplexer outputting the hardware buy/sell signal.
