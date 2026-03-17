# 🧠 Model Training & Investigation

This directory contains the Python (Keras) scripts used to train the baseline models and define the hardware routing threshold.

**Key Engineering Findings:**
During data investigation, a critical failure boundary was identified. In volatile market conditions—specifically when the standard deviation of returns ($\sigma$) exceeds `0.002`—the lightweight Logistic Regression (LR) model's accuracy degrades to 47.18% (worse than random chance). 

This mathematical threshold ($\sigma > 0.002$) is the core justification for the dual-path FPGA architecture, ensuring the system only pays the latency penalty of the Multi-Layer Perceptron (MLP) when absolutely necessary to protect predictive accuracy.
