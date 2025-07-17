import pandas as pd
import numpy as np
import tensorflow as tf
import larq as lq
from tensorflow.keras.callbacks import EarlyStopping

# 1. Generate a learnable rule-based dataset
def create_learnable_dataset():
    data = []
    action_names = {0: "left", 1: "right", 2: "uturn", 3: "stop"}

    for i in range(256):
        bits = [int(x) for x in f"{i:08b}"]

        # Extract semantic signals from bits
        front_obstacle   = bits[0]  # in0
        left_obstacle    = bits[1]  # in1
        right_obstacle   = bits[2]  # in2
        rear_obstacle    = bits[3]  # in3
        high_speed       = bits[4]  # in4
        danger_level     = bits[5]  # in5
        system_error     = bits[6]  # in6
        emergency_stop   = bits[7]  # in7

        # Simple rule-based decision logic
        if emergency_stop == 1:
            action = 3  # stop
        elif danger_level == 1 or system_error == 1:
            action = 3  # stop
        elif front_obstacle == 0:
            if left_obstacle == 0:
                action = 0  # turn left
            elif right_obstacle == 0:
                action = 1  # turn right
            elif rear_obstacle == 0 and not high_speed:
                action = 2  # u-turn
            else:
                action = 3  # stop
        else:
            if left_obstacle == 0:
                action = 0  # turn left
            elif right_obstacle == 0:
                action = 1  # turn right
            elif rear_obstacle == 0 and not high_speed:
                action = 2  # u-turn
            else:
                action = 3  # stop

        data.append(bits + [action, action_names[action]])

    return pd.DataFrame(data, columns=[
        "in0", "in1", "in2", "in3", "in4", "in5", "in6", "in7", "label", "label_str"
    ])

# 2. Create and save dataset
df = create_learnable_dataset()
df.to_csv("Learnable_Rules_Dataset.csv", index=False)
print("Dataset saved as 'Learnable_Rules_Dataset.csv'")

# 3. Load dataset
X = df[[f"in{i}" for i in range(8)]].values.astype(np.float32)
y = df["label"].values.astype(np.int32)

model = tf.keras.Sequential([
    # Input → Hidden layer (8 neurons)
    lq.layers.QuantDense(8,
                         input_dim=8,
                         kernel_quantizer="ste_sign",
                         kernel_constraint="weight_clip",
                         use_bias=True),

    # Output layer (4 neurons)
    tf.keras.layers.Dense(4, activation="softmax")
])

# 5. Optimizer
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

# 6. Compile model
model.compile(
    optimizer=optimizer,
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# 7. Early stopping callback
early_stopping = EarlyStopping(
    monitor="loss",
    patience=20,
    min_delta=0.001,
    restore_best_weights=True
)

# 8. Train the model
history = model.fit(
    X, y,
    epochs=500,
    batch_size=32,
    verbose=1,
    callbacks=[early_stopping],
    validation_split=0.2
)

# 9. Final accuracy report
final_accuracy = history.history["accuracy"][-1]
val_accuracy = history.history["val_accuracy"][-1] if "val_accuracy" in history.history else 0
print(f"\nFinal training accuracy: {final_accuracy*100:.2f}%")
print(f"Final validation accuracy: {val_accuracy*100:.2f}%")

# 10. Safe prediction function (runtime logic)
def safe_predict(input_bits):
    # Emergency stop has absolute priority
    if input_bits[7] == 1:
        return 3  # stop

    # Block left turn if left side is blocked
    if input_bits[1] == 1 and model.predict(np.array([input_bits]), verbose=0)[0][0] > 0.5:
        return 3

    # Block right turn if right side is blocked
    if input_bits[2] == 1 and model.predict(np.array([input_bits]), verbose=0)[0][1] > 0.5:
        return 3

    prediction = model.predict(np.array([input_bits]), verbose=0)
    return np.argmax(prediction[0])

# 11. Test prediction function
print("\nSample predictions:")
test_cases = [
    ([0, 0, 0, 0, 0, 0, 0, 0], "Normal"),
    ([0, 0, 0, 0, 0, 0, 0, 1], "Emergency stop"),
    ([1, 0, 0, 0, 0, 0, 0, 0], "Front obstacle"),
    ([0, 1, 0, 0, 0, 0, 0, 0], "Left obstacle"),
    ([0, 0, 1, 0, 0, 0, 0, 0], "Right obstacle"),
    ([0, 0, 0, 1, 0, 0, 0, 0], "Rear obstacle"),
    ([0, 0, 0, 0, 0, 0, 0, 0], "Fully clear"),
    ([1, 1, 1, 1, 1, 1, 1, 0], "Blocked in all directions")
]

action_map = {0: "Left", 1: "Right", 2: "U-turn", 3: "Stop"}

for bits, desc in test_cases:
    action = safe_predict(bits)
    print(f"Input {bits} ({desc}) => Action: {action_map[action]}")

# 12. Save the model
model.save("8x8x4_bnn_controller.h5")

# 13. Model summary
print("\nModel Summary:")
model.summary()
