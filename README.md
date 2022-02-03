# Open Ephys ECP5U85-BSE-USB Development Board

- Lattice ECP5U85 FPGA
- Samtec BSE GPIO strip connectors
- USB3.0 link to host computer (max 200MB/s)

## TODO:
- Add a clock chip (either LVDS or 2.5v single ended). Ideally 100MHz, but the FPGA has a PLL
- Look for proper LED parts and adjust the resistors accordingly
- Review all the connections
- Optionally, manage to connect bidirectional 3.3V FTDI WAKEUP line to free 2.5V FPGA pin with fixed clamp diodes.