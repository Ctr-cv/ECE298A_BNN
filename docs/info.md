<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.

-->

## How it works

This project implements a 2-layer Binary Neural Network (BNN) in-order classify an 8-bit binary input. The goal is to demonstrate a simple neural computation pipeline using minimal digital logic, with no multipliers or floating-point operations.

The first layer consists of 4 neurons, each performing an 8-bit XNOR popcount operation with its respective 8-bit weight vector and threshold activation. The second layer takes the 4-bit output from the first layer as input to another 4 neurons, similarly applying 4-bit XNOR popcount and thresholding to produce the final 4-bit classification output.

The purpose of this BNN is to classify inputs into 4 discrete categories such as: turn left, turn right, stop, and U-turn (depending on external training). Each neuron is assigned to detect a feature based on thresholded similarity with its input.

Weights are initialized in simulation, but the design supports real-time programmable weight loading using 4 bits of the bidirectional `uio` interface at a time. A load enable signal (`uio_in[3]`) and a simple internal load state machine coordinate the loading process.

This compact BNN core is designed for educational and demonstrational purposes and can serve as a proof-of-concept for implementing simple ML on-chip without CPUs or RAM. For example, simple feature detections could all use this design.

## How to test

Testing is done using CocoTB. Please refer to the description in `test/readme.MD`.

The testbench stimulates the `ui_in` lines with various binary inputs and simulates weight loading through the `uio_in` interface. The output `uo_out` is checked for correct classification according to known weights and thresholds.

Verilog simulations and waveform viewer will be available via commands `make sim` and `gtkwave dump.vcd`. Check back later for updates.

## External hardware

No additional hardware is used in this project.
