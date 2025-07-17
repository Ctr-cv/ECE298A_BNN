import numpy as np
import pandas as pd
import tensorflow as tf
import larq as lq
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt

# === 1. Load dataset ===
df = pd.read_csv("bnn_training_data.csv")
X = df[[f'in{i}' for i in reversed(range(8))]].values
y = df[[f'out{i}' for i in reversed(range(4))]].values

# === 2. Use all data for training ===
X_train, y_train = X, y

# === 3. Define the BNN model ===
model = Sequential([
    lq.layers.QuantDense(8, input_shape=(8,),
                         kernel_quantizer="ste_sign",
                         kernel_constraint="weight_clip",
                         use_bias=False),
    lq.layers.QuantDense(4,
                         kernel_quantizer="ste_sign",
                         kernel_constraint="weight_clip",
                         use_bias=False),
    tf.keras.layers.Activation("sigmoid")
])

model.compile(optimizer="adam",
              loss="binary_crossentropy",
              metrics=[tf.keras.metrics.BinaryAccuracy()])

# === 4. Setup real-time plotting ===
plt.ion()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
acc_list, loss_list, epoch_list = [], [], []

# === 5. Train with live plot ===
epochs = 200
for epoch in range(1, epochs + 1):
    history = model.fit(X_train, y_train, batch_size=4, epochs=1, verbose=0)
    acc = history.history["binary_accuracy"][0]
    loss = history.history["loss"][0]

    acc_list.append(acc)
    loss_list.append(loss)
    epoch_list.append(epoch)

    ax1.clear()
    ax1.plot(epoch_list, acc_list, label="Accuracy", color='blue')
    ax1.set_title("Training Accuracy")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.set_ylim(0, 1)
    ax1.grid(True)

    ax2.clear()
    ax2.plot(epoch_list, loss_list, label="Loss", color='red')
    ax2.set_title("Training Loss")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.grid(True)

    plt.tight_layout()
    plt.pause(0.01)

plt.ioff()
plt.show(block=False)

# === 6. Summary ===
final_acc = acc_list[-1]
final_loss = loss_list[-1]
print(f"\n✅ Training finished. Final Accuracy: {final_acc:.4f}, Final Loss: {final_loss:.4f}")

# === 7. Extract and binarize weights ===
weights = model.get_weights()
w1_bin = (weights[0] > 0).astype(int)  # shape: (8, 8)
w2_bin = (weights[1] > 0).astype(int)  # shape: (8, 4)

def to_verilog_array(weight_matrix):
    return ',\n'.join(f"  8'b{''.join(str(b) for b in row)}" for row in weight_matrix)

# === 8. Verilog output ===
print("\n// L1_WEIGHTS")
print("localparam [7:0] L1_WEIGHTS[0:7] = '{")
print(to_verilog_array(w1_bin))
print("};")

print("\n// L2_WEIGHTS")
print("localparam [7:0] L2_WEIGHTS[0:3] = '{")
print(to_verilog_array(w2_bin.T))  # transpose: each row is a neuron
print("};")

print("\n✅ Verilog weights output complete.")

input("\n按 Enter 关闭图表并结束程序...")
