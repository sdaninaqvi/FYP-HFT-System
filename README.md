# FYP-HFT-System

# Adaptive FPGA Inference for High-Frequency Trading

[![Hardware](https://img.shields.io/badge/Hardware-Xilinx_Artix--7-blue.svg)]()
[![Clock](https://img.shields.io/badge/Clock-100_MHz-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-Hardware_Validated-success.svg)]()

**Author:** Syed Daniyal Naqvi  
**Institution:** University of Liverpool (BEng Electrical & Electronic Engineering)  
**Conference Acceptance:** British Conference of Undergraduate Research (BCUR) 2026

## Project Abstract
High-Frequency Trading (HFT) firms rely on sub-microsecond FPGA inference pipelines to secure market advantage. However, static single-model deployments fail under market volatility: lightweight models collapse in predictive accuracy, while highly accurate models fail to meet strict latency boundaries. 

This repository contains the Verilog RTL, C++ HLS IP cores, and Python test harness for a **runtime-adaptive dual-path FPGA architecture**. By calculating market volatility σ in 900ns, the hardware automatically routes tick data through either a fast Logistic Regression (LR) model during calm markets or a Multi-Layer Perceptron (MLP) during volatile regimes, achieving optimal accuracy with zero reconfiguration downtime.

## Key Performance Metrics
Validated on **777,592 Bitcoin ticks** (Binance, 2023 1-min OHLCV) deployed on a Xilinx Artix-7 (Basys 3) FPGA.

* **Calm Pathway (LR):** 950 ns 
* **Volatile Pathway (MLP):** 1,190 ns
* **Weighted System Average:** ~951 ns (99.8% calm regime dominance)
* **Accuracy Recovery:** +4.45% in volatile conditions (recovering LR degradation)
* **Resource Utilization:** 48.4% LUTs, 29 DSPs, 6 BRAMs
* **Power Consumption:** 0.246 W (Dynamic + Static)
* **Timing:** Closed at 100 MHz with +0.183ns Worst Negative Slack (WNS)

## System Architecture
![System Architecture](System_Architecture.png)

The system utilizes a Path-Selective Synchroniser. Rather than waiting for the volatility trigger sequentially, the Trigger Compute, LR Feature Extractor, and MLP Feature Extractor execute in parallel immediately upon receiving a valid 60-tick window.

## Repository Structure
* `/data/` - Python scripts for cleaning and formatting the Binance tick dataset.
* `/models/` - Keras (`.h5`) models and Python training scripts.
* `/hls/` - C++ source files translated via `hls4ml` (quantized to `ap_fixed<16,6>`).
* `/rtl/` - Custom Verilog modules (Price Buffer, Trigger Compute, Path-Selective Synchroniser, MUX).
* `/vivado/` - Block design TCL scripts and constraints (`.xdc`) files.
* `/testing/` - Python UART test harness for streaming data to the Basys 3 and validating predictions.

## Hardware Setup & Reproduction
1. **Prerequisites:** Vivado 202X.X, Python 3.10+, `hls4ml`.
2. **Synthesis:** Run the provided TCL script in `/vivado/` to rebuild the block design for the `XC7A35T` part.
3. **Deployment:** Generate the bitstream and program the Basys 3 board.
4. **Execution:** Run `python testing/uart_streamer.py` to push the historical tick data over serial (115200 baud) and monitor the hardware path selection via board LEDs and terminal output.

## References & Acknowledgements
* Machine learning to C++ translation powered by [hls4ml](https://fastmachinelearning.org/hls4ml/). 
* Duarte, J. et al. "Fast inference of deep neural networks in FPGAs for particle physics." *JINST* (2018).
* Gupta, D. et al. "FPGA for High-Frequency Trading: Reducing Latency in Financial Systems." *IEEE ICACRS* (2024).
