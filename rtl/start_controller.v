module hls_start_controller(
    input wire clk,
    input wire rst,
    input wire trigger,
    input wire ap_ready,
    input wire ap_done,
    output reg ap_start
);
reg busy;
always @(posedge clk) begin
    if (!rst) begin
        ap_start <= 0;
        busy     <= 0;
    end else begin
        if (!busy && trigger) begin
            ap_start <= 1;
            busy     <= 1;
        end
        if (busy && ap_done) begin
            ap_start <= 0;
            busy     <= 0;
        end
    end
end
endmodule