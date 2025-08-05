# Read libraries
read_liberty /path/to/sky130_fd_sc_hd__tt_025C_1v80.lib

# Read netlist
read_verilog your_top_module_netlist.v
link_design your_top_module

# Create clocks (adjust to your design)
create_clock -name clk -period 10 [get_ports clk]

# Set input/output delays
set_input_delay 1 -clock clk [all_inputs]
set_output_delay 1 -clock clk [all_outputs]

# Set false paths if needed
set_false_path -from [get_ports rst_n]

# Perform analysis
report_checks -path_delay min_max -fields {slew cap input_pin}
report_wns
report_tns
report_power