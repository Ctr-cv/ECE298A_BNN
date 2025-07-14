import tensorflow as tf
import larq as lq
import numpy as np

# === 1. Load BNN model with Larq layers ===
model = tf.keras.models.load_model(
    "8x8x4_bnn_controller.h5",
    custom_objects={"QuantDense": lq.layers.QuantDense}
)

# === 2. Extract weights and biases from all layers ===
weights = []
biases = []

for layer in model.layers:
    if hasattr(layer, "get_weights"):
        w = layer.get_weights()
        if w:
            weights.append(w[0])
            biases.append(w[1])
        else:
            weights.append(None)
            biases.append(None)

print("Model structure:")
for i, layer in enumerate(model.layers):
    print(f"Layer {i}: {layer.name} — weights: {weights[i].shape if weights[i] is not None else 'None'}")

# === 3. Quantize weights from {-1, +1} to {0, 1} ===
def quantize_weights(w):
    return np.where(w >= 0, 1, 0).astype(np.uint8)

# === 4. Format for Verilog ===
def format_bin_array_2d(arr, name):
    lines = [f"// {name}", f"localparam [7:0] {name}[0:{arr.shape[0]-1}] = '{{"]
    for row in arr:
        bits = ''.join(str(b) for b in row)
        hexval = f"{int(bits, 2):#010b}"  # e.g. 0b11011010
        lines.append(f"  8'b{bits},")
    lines[-1] = lines[-1].rstrip(',')  # remove trailing comma
    lines.append("};\n")
    return "\n".join(lines)

# === 5. Export hidden & output layer weights ===
with open("bnn_weights.vh", "w") as f:
    # Layer 1: 8 → 8
    w1 = quantize_weights(weights[0].T)  # shape (8, 8)
    f.write(format_bin_array_2d(w1, "L1_WEIGHTS"))

    # Layer 2: 8 → 4
    w2 = quantize_weights(weights[1].T)  # shape (4, 8)
    f.write(format_bin_array_2d(w2, "L2_WEIGHTS"))

    # Layer 3: 4 → 4 (float weights for softmax, not binarized)
    w3 = weights[2].T  # shape (4, 4)
    f.write("// L3_WEIGHTS (float, output layer)\n")
    for i, row in enumerate(w3):
        row_vals = ", ".join([f"{v:+.6f}" for v in row])
        f.write(f"// neuron {i}: {row_vals}\n")

print("✅ Export complete: bnn_weights.vh")
