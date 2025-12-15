#!/usr/bin/env python3
"""
测试ADB文件查询功能
"""
import sys
from pathlib import Path

# 加载主模块
sys.path.insert(0, '.')
from sensor_simulator import load_config, find_adb_path, get_recent_sensor_files

print("测试: 查询模拟器中的sensor文件\n")

# 1. 加载配置
cfg = load_config()
print(f"配置文件: OK")

# 2. 找到ADB
adb_path = find_adb_path(cfg)
print(f"ADB路径: {adb_path}\n")

# 3. 查询文件
files = get_recent_sensor_files(adb_path, minutes=120)

if files:
    print(f"\n找到 {len(files)} 个文件:\n")
    for i, (filename, date, time) in enumerate(files, 1):
        print(f"{i}. {filename}")
        if date != "unknown":
            print(f"   时间: {date} {time}")
        print()
else:
    print("\n未找到文件或目录不存在")

print("\n测试完成！")
