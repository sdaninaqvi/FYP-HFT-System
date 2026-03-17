# ⚙️ High-Level Synthesis (C++ IP Cores)

This folder contains the C++ source code generated from the Keras models using the `hls4ml` library. 

To meet strict latency and area constraints on the Artix-7, the data paths were rigidly quantized:
* **LR Path:** `ap_fixed<16,6>` 
* **MLP Path:** `ap_fixed<32,18>`

**Debugging Note:** A significant `DATAFLOW` sustained-start requirement was identified and resolved during this phase. The HLS control logic was modified to hold `ap_start` high, preventing pipeline stalling and ensuring the `ap_done` signals fired correctly for the RTL synchroniser.
