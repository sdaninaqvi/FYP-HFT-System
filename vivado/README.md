# Vivado Build & Constraints

This folder contains the files necessary to rebuild the complete block design for the Xilinx Artix-7 (Basys 3 / XC7A35T).

* **`constraints.xdc`**: Defines the 100 MHz clock and physical pinouts for the board.
* **`build_project.tcl`**: A TCL script to automatically reconstruct the Vivado block design, IP integrator connections, and synthesis settings.

*Note: To keep the repository clean and professional, bulky Vivado `.runs` and `.cache` directories are excluded.*
