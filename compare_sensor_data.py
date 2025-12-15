#!/usr/bin/env python3
"""
对比生成数据和真实数据的统计特征
"""
import json
import random
import statistics
from pathlib import Path

from sensor_simulator import generate_sensor_data


def load_real_sample(sample_file: Path):
    """加载真实传感器数据样本"""
    content = sample_file.read_text(encoding="utf-8")
    data = json.loads(content)
    return data


def analyze_data(data, label):
    """分析数据统计特征"""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"  数据点数: {len(data)}")
    print(f"  平均值: {statistics.mean(data):.2f} m/s^2")
    print(f"  标准差: {statistics.stdev(data):.2f} m/s^2")
    print(f"  中位数: {statistics.median(data):.2f} m/s^2")
    print(f"  最小值: {min(data):.2f} m/s^2")
    print(f"  最大值: {max(data):.2f} m/s^2")
    
    # 计算分位数
    sorted_data = sorted(data)
    p25 = sorted_data[len(data)//4]
    p75 = sorted_data[len(data)*3//4]
    print(f"  25%分位: {p25:.2f} m/s^2")
    print(f"  75%分位: {p75:.2f} m/s^2")


def main():
    print("\n" + "="*60)
    print("  传感器数据对比分析")
    print("="*60)
    
    # 1. 加载真实数据样本
    real_samples_dir = Path("real_sensor")
    samples = list(real_samples_dir.glob("*.txt"))
    
    if not samples:
        print("错误: 未找到真实数据样本")
        return
    
    # 随机选择3个样本
    selected_samples = random.sample(samples, min(3, len(samples)))
    
    print(f"\n加载了 {len(selected_samples)} 个真实数据样本:")
    for s in selected_samples:
        print(f"  - {s.name}")
    
    # 2. 分析真实数据
    all_real_data = []
    for sample_file in selected_samples:
        data = load_real_sample(sample_file)
        all_real_data.extend(data)
    
    analyze_data(all_real_data, "真实数据统计 (多个样本合并)")
    
    # 3. 生成模拟数据
    print("\n正在生成模拟数据...")
    duration = len(all_real_data) / 10.0  # 假设10Hz采样率
    generated_data = generate_sensor_data(duration, 2.8)
    
    analyze_data(generated_data, "生成数据统计")
    
    # 4. 对比结果
    print(f"\n{'='*60}")
    print("对比结果")
    print(f"{'='*60}")
    
    real_mean = statistics.mean(all_real_data)
    gen_mean = statistics.mean(generated_data)
    mean_diff = abs(real_mean - gen_mean) / real_mean * 100
    
    real_std = statistics.stdev(all_real_data)
    gen_std = statistics.stdev(generated_data)
    std_diff = abs(real_std - gen_std) / real_std * 100
    
    print(f"  平均值差异: {mean_diff:.2f}%")
    print(f"  标准差差异: {std_diff:.2f}%")
    
    if mean_diff < 10 and std_diff < 20:
        print("\n  ✓ 生成数据与真实数据高度相似！")
    elif mean_diff < 20 and std_diff < 30:
        print("\n  ~ 生成数据基本符合真实数据特征")
    else:
        print("\n  ! 生成数据可能需要进一步调整")


if __name__ == "__main__":
    main()
