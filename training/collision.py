import pandas as pd

df = pd.read_csv("bnn_training_data.csv")
input_cols = [f"in{i}" for i in range(8)]
grouped = df.groupby(input_cols)

conflicts = grouped["label"].nunique()
conflicted_inputs = conflicts[conflicts > 1]

print(f"冲突样本数：{len(conflicted_inputs)}")
print("前几项冲突示例：")
print(conflicted_inputs.head())
