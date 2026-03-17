`timescale 1ns / 1ps

module bitcoin_uart_interface #(
    parameter NUM_PRICES = 60,
    parameter PRICE_WIDTH = 32
)(
    input wire clk,
    input wire rst,
    input wire rx,
    output wire tx,
    output reg [PRICE_WIDTH-1:0] new_price,
    output reg price_valid,
    input wire [31:0] prediction_in,
    input wire path_used_in,
    output wire [7:0] status_leds,
    output reg buffer_ready
);
    wire [7:0] rx_data;
    wire rx_valid;
    wire rx_busy;
    
    uart_rx #(
        .CLK_FREQ(100_000_000),
        .BAUD_RATE(115200)
    ) uart_rx_inst (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .data(rx_data),
        .valid(rx_valid),
        .busy(rx_busy)
    );
    
    reg [7:0] byte_buffer [0:239];
    reg [7:0] byte_count;
    reg [5:0] price_count;
    reg receiving;
    reg capture_price;
    
    assign status_leds = buffer_ready ? 8'hF0 : byte_count;
    assign tx = 1'b1;
    
    always @(posedge clk) begin
        if (!rst) begin
            byte_count    <= 0;
            price_count   <= 0;
            price_valid   <= 0;
            new_price     <= 0;
            receiving     <= 0;
            buffer_ready  <= 0;
            capture_price <= 0;
        end else begin
            price_valid   <= 0;
            capture_price <= 0;
            
            // Clear buffer_ready when new data starts arriving
            if (rx_valid && price_count == 0 && byte_count == 0) begin
                buffer_ready <= 0;
            end
            
            // Delayed capture: one cycle after the 4th byte was written,
            // byte_buffer and byte_count have both committed, so the
            // indices are now correct and all four bytes are readable.
            if (capture_price) begin
                new_price <= {byte_buffer[byte_count-1],
                              byte_buffer[byte_count-2],
                              byte_buffer[byte_count-3],
                              byte_buffer[byte_count-4]};
                price_valid <= 1;
                price_count <= price_count + 1;
                
                if (price_count == NUM_PRICES - 1) begin
                    buffer_ready <= 1;
                    price_count  <= 0;
                    byte_count   <= 0;
                    receiving    <= 0;
                end
            end
            
            if (rx_valid) begin
                byte_buffer[byte_count] <= rx_data;
                byte_count <= byte_count + 1;
                receiving  <= 1;
                
                // Flag capture for NEXT cycle, when the nonblocking
                // writes to byte_buffer and byte_count have committed
                if ((byte_count + 1) % 4 == 0 && byte_count > 0) begin
                    capture_price <= 1;
                end
            end
        end
    end
    
endmodule
