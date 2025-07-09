import tensorflow as tf
import numpy as np
import larq as lq

# 加载模型
model = tf.keras.models.load_model(
    "8x8x8x4_bnn_controller.h5",
    custom_objects={"QuantDense": lq.layers.QuantDense}
)


# 打印模型层结构
for i, layer in enumerate(model.layers):
    print(f"Layer {i}: {layer.name} — weights: {len(layer.get_weights())}")

# 提取每层权重（layer0-2 是 QuantDense，layer3 是 Dense）
weights = [layer.get_weights()[0] for layer in model.layers if len(layer.get_weights()) > 0]
biases = [layer.get_weights()[1] for layer in model.layers if len(layer.get_weights()) > 0]

# 将二值化层权重转换为 ±1
binary_weights = [np.where(w >= 0, 1, -1).astype(int) for w in weights[:3]]  # 前3层是二值

# 输出为 Verilog .h 格式
def format_array_2d(arr, name, is_float=False):
    lines = [f"// {name}", f"localparam {('real' if is_float else 'signed')} [{arr.shape[1]-1}:0] {name}[0:{arr.shape[0]-1}] = '{{"]
    for row in arr:
        row_str = ", ".join([f"{v:+.6f}" if is_float else f"{int(v):+d}" for v in row])
        lines.append(f"  '{{ {row_str} }},")
    lines[-1] = lines[-1].rstrip(',')  # remove trailing comma
    lines.append("};\n")
    return "\n".join(lines)

def format_array_1d(arr, name):
    values = ", ".join([f"{v:.6f}" for v in arr])
    return f"// {name}\nlocalparam real {name}[0:{len(arr)-1}] = '{{ {values} }};\n"

# 导出所有层
with open("bnn_weights.vh", "w") as f:
    f.write(format_array_2d(binary_weights[0], "layer1_weights"))
    f.write(format_array_2d(binary_weights[1], "layer2_weights"))
    f.write(format_array_2d(binary_weights[2], "layer3_weights"))
    f.write(format_array_2d(weights[3], "output_weights", is_float=True))  # 输出层 float
    f.write(format_array_1d(biases[3], "output_biases"))  # 输出层 bias

