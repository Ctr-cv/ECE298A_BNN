<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This current project is a sample 8-bit counter that supports tri-state output. Our project (in work) is shown below:
We will be implementing a 4-neuron Binary Neural Network (BNN), on a Tiny TapeOut ASIC to classify a 6-bit binary input (line inputs).
The main purpose is to perform classification into 4 different classes: turn left, turn right, stop, and U-turn.
1 neuron will be assigned to each feature detection. We will be using an external python framework like Larq to train a set of 8 weights per neuron for a total of 32.
The design also supports neuron loading by using 4 bits of bidirectional (uio) at a time.

## How to test

Test is done using CocoTB, check the description in test/readme.MD

Some fillers here

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any

No additional hardwares are used in this project.
