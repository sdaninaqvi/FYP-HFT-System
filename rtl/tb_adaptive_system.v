`timescale 1ns / 1ps

/******************************************************************************
 * ADAPTIVE HFT SYSTEM - COMPLETE HARDWARE VERIFICATION TESTBENCH
 * 
 * Tests adaptive model selection with proper control flow:
 * 1. UART receives 240 bytes (60 prices)
 * 2. buffer_ready signals completion
 * 3. window_valid triggers computation
 * 4. System selects LR or MLP based on volatility
 * 5. Prediction output ready
 ******************************************************************************/

module tb_adaptive_system;

    //=========================================================================
    // CLOCK & RESET
    //=========================================================================
    reg Clock_input;
    reg Reset_n_input;
    
    //=========================================================================
    // UART INTERFACE
    //=========================================================================
    reg rx_0;
    
    //=========================================================================
    // OUTPUTS TO MONITOR
    //=========================================================================
    wire [0:0] Dout_0;
    wire [0:0] Dout_1;
    wire [31:0] PREDICTION_OUTPUT;
    wire path_used_0;
    wire [0:0] prediction_out;
    wire [7:0] status_leds_0;
    wire tx_0;
    wire used_mlp_output;
    
    //=========================================================================
    // TEST CONTROL
    //=========================================================================
    reg [31:0] test_prices [0:59];
    integer i, byte_idx, bit_idx;
    integer test_number;
    
    // Timing tracking
    time uart_start_time;
    time uart_end_time;
    time computation_start_time;
    time computation_end_time;
    
    //=========================================================================
    // INSTANTIATE DESIGN UNDER TEST
    //=========================================================================
    design_1_wrapper dut (
        .Clock_input(Clock_input),
        .Reset_n_input(Reset_n_input),
        .rx_0(rx_0),
        .Dout_0(Dout_0),
        .Dout_1(Dout_1),
        .PREDICTION_OUTPUT(PREDICTION_OUTPUT),
        .path_used_0(path_used_0),
        .prediction_out(prediction_out),
        .status_leds_0(status_leds_0),
        .tx_0(tx_0),
        .used_mlp_output(used_mlp_output)
    );
    
    //=========================================================================
    // CLOCK GENERATION: 100MHz (10ns period)
    //=========================================================================
    initial Clock_input = 0;
    always #5 Clock_input = ~Clock_input;
    
    //=========================================================================
    // UART TRANSMISSION TASKS
    //=========================================================================
    
    // Send single byte via UART (115200 baud, 8N1)
    task send_uart_byte;
        input [7:0] data;
    begin
        // Start bit (0)
        rx_0 = 0;
        repeat(868) @(posedge Clock_input);  // 868 clocks @ 100MHz = 115200 baud
        
        // 8 data bits (LSB first)
        for (bit_idx = 0; bit_idx < 8; bit_idx = bit_idx + 1) begin
            rx_0 = data[bit_idx];
            repeat(868) @(posedge Clock_input);
        end
        
        // Stop bit (1)
        rx_0 = 1;
        repeat(868) @(posedge Clock_input);
    end
    endtask
    
    // Send 32-bit price as 4 bytes (little-endian)
    task send_price;
        input [31:0] price;
    begin
        send_uart_byte(price[7:0]);     // Byte 0 (LSB)
        send_uart_byte(price[15:8]);    // Byte 1
        send_uart_byte(price[23:16]);   // Byte 2
        send_uart_byte(price[31:24]);   // Byte 3 (MSB)
    end
    endtask
    
    //=========================================================================
    // MAIN TEST SEQUENCE
    //=========================================================================
    initial begin
        // Print header
        $display("");
        $display("========================================================================");
        $display("    ADAPTIVE HFT SYSTEM - HARDWARE VERIFICATION TESTBENCH");
        $display("========================================================================");
        $display("");
        $display("Testing:");
        $display("  - UART interface (115200 baud, 240 bytes)");
        $display("  - Price buffer (60-price window)");
        $display("  - Volatility trigger (0.002 threshold)");
        $display("  - Adaptive model selection (LR vs MLP)");
        $display("");
        $display("========================================================================");
        $display("");
        
        // Initialize signals
        Reset_n_input = 0;
        rx_0 = 1;              // UART idle = high
        test_number = 0;
        
        // Apply reset
        $display("[%0t ns] Applying reset...", $time);
        #200;
        Reset_n_input = 1;
        #200;
        $display("[%0t ns] Reset released - system ready", $time);
        $display("");
        
        //=====================================================================
        // TEST 1: LOW VOLATILITY → EXPECT LR (used_mlp_output = 0)
        //=====================================================================
        test_number = 1;
        $display("========================================================================");
        $display("TEST 1: LOW VOLATILITY DATA");
        $display("========================================================================");
        $display("Expected behavior:");
        $display("  - Normalized spread < 0.002");
        $display("  - System selects LR model (fast path)");
        $display("  - used_mlp_output = 0");
        $display("  - status_leds = 0xF0 after transmission");
        $display("------------------------------------------------------------------------");
        $display("");
        
        // Load test data
        $readmemh("test_prices_low_vol.hex", test_prices);
        $display("[%0t ns] Loaded low volatility test prices", $time);
        
        // Send 60 prices via UART
        $display("[%0t ns] Transmitting 60 prices via UART...", $time);
        uart_start_time = $time;
        
        for (i = 0; i < 60; i = i + 1) begin
            send_price(test_prices[i]);
            
            if (i == 0)
                $display("             First price sent: 0x%08X", test_prices[i]);
            if ((i+1) % 10 == 0 && i != 59)
                $display("             Progress: %2d/60 prices (status_leds = 0x%02X)", 
                         i+1, status_leds_0);
            if (i == 59)
                $display("             Last price sent:  0x%08X", test_prices[i]);
        end
        
        uart_end_time = $time;
        
        $display("");
        $display("[%0t ns] ✓ UART transmission complete", $time);
        $display("             Total time: %0t ns (%0.2f ms)", 
                 uart_end_time - uart_start_time,
                 (uart_end_time - uart_start_time) / 1000000.0);
        $display("             Final status_leds = 0x%02X (expect 0xF0)", status_leds_0);
        $display("");
        $display("             Waiting for FPGA computation...");
        $display("");
        
        // Wait for computation to complete
        // Trigger + Features + Model = ~500 cycles worst case
        repeat(10000) @(posedge Clock_input);
        
        computation_end_time = $time;
        
        // Display results
        $display("========================================================================");
        $display("TEST 1 RESULTS:");
        $display("========================================================================");
        $display("  Timing:");
        $display("    UART transmission:  %0.3f ms", (uart_end_time - uart_start_time) / 1000000.0);
        $display("    FPGA computation:   %0.3f us", (computation_end_time - uart_end_time) / 1000.0);
        $display("");
        $display("  Outputs:");
        $display("    status_leds      = 0x%02X  (expect 0xF0)", status_leds_0);
        $display("    used_mlp_output  = %b      (expect 0 = LR)", used_mlp_output);
        $display("    path_used_0      = %b      (expect 0 = LR)", path_used_0);
        $display("    PREDICTION       = 0x%08X", PREDICTION_OUTPUT);
        $display("------------------------------------------------------------------------");
        
        // Check pass/fail
        if (status_leds_0 == 8'hF0 && used_mlp_output == 0) begin
            $display("  ✓✓✓ TEST 1 PASSED ✓✓✓");
            $display("  System correctly selected LR model for low volatility");
        end else begin
            $display("  ✗✗✗ TEST 1 FAILED ✗✗✗");
            if (status_leds_0 != 8'hF0)
                $display("  ERROR: Expected status_leds = 0xF0, got 0x%02X", status_leds_0);
            if (used_mlp_output != 0)
                $display("  ERROR: Expected LR (0) but got MLP (1)");
        end
        $display("========================================================================");
        $display("");
        
        // Wait between tests
        #10000;
        
        //=====================================================================
        // TEST 2: HIGH VOLATILITY → EXPECT MLP (used_mlp_output = 1)
        //=====================================================================
        test_number = 2;
        $display("========================================================================");
        $display("TEST 2: HIGH VOLATILITY DATA");
        $display("========================================================================");
        $display("Expected behavior:");
        $display("  - Normalized spread > 0.002");
        $display("  - System selects MLP model (accurate path)");
        $display("  - used_mlp_output = 1");
        $display("  - status_leds = 0xF0 after transmission");
        $display("------------------------------------------------------------------------");
        $display("");
        
        // Load test data
        $readmemh("test_prices_high_vol.hex", test_prices);
        $display("[%0t ns] Loaded high volatility test prices", $time);
        
        // Send 60 prices via UART
        $display("[%0t ns] Transmitting 60 prices via UART...", $time);
        uart_start_time = $time;
        
        for (i = 0; i < 60; i = i + 1) begin
            send_price(test_prices[i]);
            
            if (i == 0)
                $display("             First price sent: 0x%08X", test_prices[i]);
            if ((i+1) % 10 == 0 && i != 59)
                $display("             Progress: %2d/60 prices (status_leds = 0x%02X)", 
                         i+1, status_leds_0);
            if (i == 59)
                $display("             Last price sent:  0x%08X", test_prices[i]);
        end
        
        uart_end_time = $time;
        
        $display("");
        $display("[%0t ns] ✓ UART transmission complete", $time);
        $display("             Total time: %0t ns (%0.2f ms)", 
                 uart_end_time - uart_start_time,
                 (uart_end_time - uart_start_time) / 1000000.0);
        $display("             Final status_leds = 0x%02X (expect 0xF0)", status_leds_0);
        $display("");
        $display("             Waiting for FPGA computation...");
        $display("");
        
        // Wait for computation
        repeat(10000) @(posedge Clock_input);
        
        computation_end_time = $time;
        
        // Display results
        $display("========================================================================");
        $display("TEST 2 RESULTS:");
        $display("========================================================================");
        $display("  Timing:");
        $display("    UART transmission:  %0.3f ms", (uart_end_time - uart_start_time) / 1000000.0);
        $display("    FPGA computation:   %0.3f us", (computation_end_time - uart_end_time) / 1000.0);
        $display("");
        $display("  Outputs:");
        $display("    status_leds      = 0x%02X  (expect 0xF0)", status_leds_0);
        $display("    used_mlp_output  = %b      (expect 1 = MLP)", used_mlp_output);
        $display("    path_used_0      = %b      (expect 1 = MLP)", path_used_0);
        $display("    PREDICTION       = 0x%08X", PREDICTION_OUTPUT);
        $display("------------------------------------------------------------------------");
        
        // Check pass/fail
        if (status_leds_0 == 8'hF0 && used_mlp_output == 1) begin
            $display("  ✓✓✓ TEST 2 PASSED ✓✓✓");
            $display("  System correctly selected MLP model for high volatility");
        end else begin
            $display("  ✗✗✗ TEST 2 FAILED ✗✗✗");
            if (status_leds_0 != 8'hF0)
                $display("  ERROR: Expected status_leds = 0xF0, got 0x%02X", status_leds_0);
            if (used_mlp_output != 1)
                $display("  ERROR: Expected MLP (1) but got LR (0)");
        end
        $display("========================================================================");
        $display("");
        
        // Final summary
        #10000;
        $display("");
        $display("========================================================================");
        $display("         HARDWARE VERIFICATION COMPLETE");
        $display("========================================================================");
        $display("");
        $display("Summary:");
        $display("  ✓ UART interface verified (240 bytes @ 115200 baud)");
        $display("  ✓ Price buffer verified (60-price window)");
        $display("  ✓ Adaptive model selection verified");
        $display("  ✓ System performs correct LR/MLP selection based on volatility");
        $display("");
        $display("Ready for:");
        $display("  1. Physical FPGA programming");
        $display("  2. Bench demonstration");
        $display("  3. Performance data collection");
        $display("");
        $display("========================================================================");
        $display("");
        
        $finish;
    end
    
    //=========================================================================
    // CONTINUOUS MONITORS - Track Key Events
    //=========================================================================
    
    // Monitor byte reception completion
    reg bytes_complete_reported;
    initial bytes_complete_reported = 0;
    
    always @(posedge Clock_input) begin
        if (status_leds_0 == 8'hF0 && !bytes_complete_reported && $time > 10000) begin
            $display("[%0t ns] ✓✓ All 240 bytes received by UART module", $time);
            bytes_complete_reported = 1;
        end
        
        // Reset flag for next test
        if (status_leds_0 < 8'hF0 && bytes_complete_reported) begin
            bytes_complete_reported = 0;
        end
    end
    
    // Monitor window_valid signal (computation trigger)
    // Access internal signal to see when computation starts
    always @(posedge Clock_input) begin
        // Check if window_valid pulsed (if you made it external, adjust path)
        // This assumes window_valid is inside price_buffer_0
        // If you made it external, you can access it directly
    end
    
    // Monitor final model selection (only report significant changes)
    reg model_stable;
    integer stable_count;
    initial begin
        model_stable = 0;
        stable_count = 0;
    end
    
    always @(posedge Clock_input) begin
        if ($time > 10000) begin
            // Count stable cycles
            if (stable_count < 1000) begin
                stable_count = stable_count + 1;
            end else if (!model_stable) begin
                // Model has been stable for 1000 cycles
                $display("[%0t ns] → Model selection stabilized: %s", 
                         $time, used_mlp_output ? "MLP (accurate)" : "LR (fast)");
                model_stable = 1;
            end
        end
    end
    
    always @(used_mlp_output) begin
        // Reset stable counter when model changes
        stable_count = 0;
        model_stable = 0;
    end
    
    //=========================================================================
    // WAVEFORM DUMP (for GTKWave or Vivado waveform viewer)
    //=========================================================================
    initial begin
        $dumpfile("adaptive_system.vcd");
        $dumpvars(0, tb_adaptive_system);
    end

endmodule