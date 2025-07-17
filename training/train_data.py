import numpy as np
import tensorflow as tf
import larq as lq

# === 加载模型（包含 Larq 自定义层）===
model = tf.keras.models.load_model(
    "bnn_model.h5",
    custom_objects={"QuantDense": lq.layers.QuantDense}
)

# === 测试样本 ===
test_inputs = np.array([
    [0,0,0,0,0,0,0,0],
    [1,1,1,0,0,0,0,0],
    [1,0,1,0,0,0,0,0],
    [1,1,0,0,0,0,0,0],
    [0,0,0,0,1,1,0,0]
])

# === 推理并输出 One-hot 结果 ===
print("=== 推理结果 ===")
for input_bits in test_inputs:
    input_array = np.expand_dims(input_bits, axis=0)
    soft_output = model.predict(input_array, verbose=0)
    predicted_class = np.argmax(soft_output)
    one_hot = [int(i == predicted_class) for i in range(4)]

    print(f"输入: {list(input_bits)} → softmax: {np.round(soft_output[0], 3)} → 输出: {one_hot}")
