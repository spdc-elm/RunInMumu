#!/usr/bin/env python3
"""快速测试传感器数据生成"""

import sys
sys.path.insert(0, '.')

from sensor_simulator import generate_sensor_data
import statistics

# 测试生成数据
print("测试: 生成1143秒的传感器数据...")
data = generate_sensor_data(1143.0, 2.8)

print(f"\n结果:")
print(f"  数据点数: {len(data)}")
print(f"  期望点数: {int(1143 * 10)} (1143秒 * 10Hz)")
print(f"  平均值: {statistics.mean(data):.2f} m/s^2")
print(f"  标准差: {statistics.stdev(data):.2f} m/s^2")
print(f"  最小值: {min(data):.2f} m/s^2")
print(f"  最大值: {max(data):.2f} m/s^2")

print(f"\n前10个数据点:")
print(data[:10])

print(f"\n与真实数据对比:")
print(f"  真实数据均值: 14.98 m/s^2 (全部28个样本)")
print(f"  真实数据标准差: 12.20 m/s^2")
print(f"  生成数据均值: {statistics.mean(data):.2f} m/s^2")
print(f"  生成数据标准差: {statistics.stdev(data):.2f} m/s^2")

# 检查是否合理
mean_diff = abs(statistics.mean(data) - 14.98) / 14.98 * 100
std_diff = abs(statistics.stdev(data) - 12.20) / 12.20 * 100

print(f"\n差异分析:")
print(f"  平均值差异: {mean_diff:.1f}%")
print(f"  标准差差异: {std_diff:.1f}%")

if mean_diff < 10 and std_diff < 15:
    print("\nOK 生成数据与真实数据高度相似")
elif mean_diff < 20 and std_diff < 25:
    print("\nOK 生成数据基本符合真实特征")
else:
    print("\nWARNING 数据可能需要调整")
