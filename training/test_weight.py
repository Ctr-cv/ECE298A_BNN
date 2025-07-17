import tensorflow as tf
import numpy as np

# ✅ 自定义动作标签映射
actions = ["left", "right", "forward", "stop"]

# ✅ 载入 softmax 输出模型
model = tf.keras.models.load_model("bnn_model.h5")

# ✅ 测试输入（8位）
test_inputs = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],  # 可以自定义更多
]

print("=== 推理结果 ===")
for test_input in test_inputs:
    x = np.array([test_input])
    prediction = model.predict(x, verbose=0)[0]

    # ✅ 将 softmax 概率转为 one-hot 二进制向量
    predicted_index = np.argmax(prediction)
    pred_one_hot = [1 if i == predicted_index else 0 for i in range(4)]
    predicted_action = actions[predicted_index]

    print(f"输入: {test_input} → 概率输出: {np.round(prediction, 3).tolist()} → 二进制: {pred_one_hot} → 动作: {predicted_action}")
