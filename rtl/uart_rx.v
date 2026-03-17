module uart_rx #(
    parameter CLK_FREQ = 100_000_000,  // 100 MHz
    parameter BAUD_RATE = 115200
)(
    input wire clk,
    input wire rst,
    input wire rx,           // UART RX pin
    output reg [7:0] data,   // Received byte
    output reg valid,        // Data valid pulse
    output wire busy         // Receiver busy
);

    localparam CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;  // 868 clocks per bit
    localparam HALF_BIT = CLKS_PER_BIT / 2;
    
    // States
    localparam IDLE  = 3'd0;
    localparam START = 3'd1;
    localparam DATA  = 3'd2;
    localparam STOP  = 3'd3;
    
    reg [2:0] state;
    reg [15:0] clk_count;
    reg [2:0] bit_index;
    reg [7:0] data_reg;
    
    assign busy = (state != IDLE);
    
    always @(posedge clk) begin
        if (!rst) begin
            state <= IDLE;
            clk_count <= 0;
            bit_index <= 0;
            data <= 0;
            valid <= 0;
            data_reg <= 0;
        end else begin
            valid <= 0;  // Default: no valid data
            
            case (state)
                IDLE: begin
                    clk_count <= 0;
                    bit_index <= 0;
                    if (rx == 0) begin  // Start bit detected
                        state <= START;
                    end
                end
                
                START: begin
                    if (clk_count == HALF_BIT) begin
                        if (rx == 0) begin  // Confirm start bit
                            clk_count <= 0;
                            state <= DATA;
                        end else begin
                            state <= IDLE;  // False start
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
                
                DATA: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        clk_count <= 0;
                        data_reg[bit_index] <= rx;  // Sample bit
                        
                        if (bit_index == 7) begin
                            bit_index <= 0;
                            state <= STOP;
                        end else begin
                            bit_index <= bit_index + 1;
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
                
                STOP: begin
                    if (clk_count == CLKS_PER_BIT - 1) begin
                        if (rx == 1) begin  // Valid stop bit
                            data <= data_reg;
                            valid <= 1;
                        end
                        state <= IDLE;
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end
    
endmodule
