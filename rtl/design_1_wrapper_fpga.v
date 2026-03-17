`timescale 1 ns / 1 ps
module design_1_wrapper_fpga
   (Clock_input,
    Reset_n_input,
    path_used_1,
    rx_0,
    status_leds_0,
    tx_0,
    seg_0,
    an_0,
    dp_0,
    led_upper_0);

  input  Clock_input;
  input  Reset_n_input;
  output path_used_1;
  input  rx_0;
  output [7:0] status_leds_0;
  output tx_0;
  output [6:0] seg_0;
  output [3:0] an_0;
  output dp_0;
  output [6:0] led_upper_0;

  // Internal wires for outputs that exist in design_1
  // but don't need physical pins on the board
  wire [0:0]  Dout_0_nc;
  wire [31:0] PREDICTION_OUTPUT_nc;
  wire        buffer_ready_0_nc;
  wire        path_used_0_nc;

  (* DONT_TOUCH = "yes" *) design_1 design_1_i
       (.Clock_input(Clock_input),
        .Dout_0(Dout_0_nc),
        .PREDICTION_OUTPUT(PREDICTION_OUTPUT_nc),
        .Reset_n_input(Reset_n_input),
        .buffer_ready_0(buffer_ready_0_nc),
        .path_used_0(path_used_0_nc),
        .path_used_1(path_used_1),
        .rx_0(rx_0),
        .status_leds_0(status_leds_0),
        .tx_0(tx_0),
        .seg_0(seg_0),
        .an_0(an_0),
        .dp_0(dp_0),
        .led_upper_0(led_upper_0));
endmodule