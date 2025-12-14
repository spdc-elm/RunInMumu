#!/usr/bin/env python3
"""
GPX 文件解析器 - 将 GPX 文件中的路径点转换为 Python 列表格式
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple


def parse_gpx(gpx_file: str) -> List[Tuple[float, float]]:
    """
    解析 GPX 文件，提取所有航点的经纬度坐标
    
    Args:
        gpx_file: GPX 文件路径
    
    Returns:
        包含 (经度, 纬度) 元组的列表
    """
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    
    # GPX 使用命名空间
    namespace = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    waypoints = []
    
    # 查找所有 wpt 标签
    for wpt in root.findall('.//gpx:wpt', namespace):
        lat = float(wpt.get('lat'))
        lon = float(wpt.get('lon'))
        waypoints.append((lon, lat))
    
    return waypoints


def remove_duplicates(waypoints: List[Tuple[float, float]], tolerance: float = 1e-6) -> List[Tuple[float, float]]:
    """
    去除连续重复的坐标点
    
    Args:
        waypoints: 原始坐标列表
        tolerance: 判断重复的容差值
    
    Returns:
        去重后的坐标列表
    """
    if not waypoints:
        return []
    
    result = [waypoints[0]]
    for point in waypoints[1:]:
        prev_point = result[-1]
        # 如果当前点与前一个点不同，则添加
        if abs(point[0] - prev_point[0]) > tolerance or abs(point[1] - prev_point[1]) > tolerance:
            result.append(point)
    
    return result


def simplify_path(waypoints: List[Tuple[float, float]], step: int = 10) -> List[Tuple[float, float]]:
    """
    简化路径，每隔 step 个点取一个
    
    Args:
        waypoints: 原始坐标列表
        step: 采样间隔
    
    Returns:
        简化后的坐标列表
    """
    if not waypoints:
        return []
    
    # 总是包含第一个和最后一个点
    result = [waypoints[i] for i in range(0, len(waypoints), step)]
    
    # 确保最后一个点被包含
    if waypoints[-1] not in result:
        result.append(waypoints[-1])
    
    return result


def format_python_list(waypoints: List[Tuple[float, float]]) -> str:
    """
    将坐标列表格式化为 Python 代码字符串
    
    Args:
        waypoints: 坐标列表
    
    Returns:
        Python 列表格式的字符串
    """
    lines = ["WALK_PATH: List[Tuple[float, float]] = ["]
    
    for i, (lon, lat) in enumerate(waypoints):
        comma = "," if i < len(waypoints) - 1 else ""
        lines.append(f"    ({lat}, {lon}){comma}")
    
    lines.append("]")
    
    return "\n".join(lines)


if __name__ == "__main__":
    gpx_file = "run.gpx"
    
    print(f"正在解析 GPX 文件: {gpx_file}")
    
    # 解析 GPX 文件
    waypoints = parse_gpx(gpx_file)
    print(f"总共找到 {len(waypoints)} 个路径点")
    
    # 去除重复点
    waypoints = remove_duplicates(waypoints)
    print(f"去重后剩余 {len(waypoints)} 个路径点")
    
    # 简化路径（可选）
    print("\n选择输出选项:")
    print("1. 使用所有去重后的点（推荐用于精确路径）")
    print("2. 简化路径，每10个点取1个（减少数据量）")
    print("3. 简化路径，每20个点取1个（大幅减少数据量）")
    print("4. 简化路径，每50个点取1个（最少数据量）")
    
    choice = input("\n请选择 (1-4，默认为1): ").strip() or "1"
    
    if choice == "2":
        waypoints = simplify_path(waypoints, step=10)
        print(f"简化后剩余 {len(waypoints)} 个路径点")
    elif choice == "3":
        waypoints = simplify_path(waypoints, step=20)
        print(f"简化后剩余 {len(waypoints)} 个路径点")
    elif choice == "4":
        waypoints = simplify_path(waypoints, step=50)
        print(f"简化后剩余 {len(waypoints)} 个路径点")
    
    # 生成 Python 代码
    python_code = format_python_list(waypoints)
    
    # 输出到文件
    output_file = "walk_path.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("from typing import List, Tuple\n\n")
        f.write(python_code)
        f.write("\n")
    
    print(f"\n✓ 路径已保存到: {output_file}")
    print(f"\n你可以将 {output_file} 中的 WALK_PATH 复制到 main.py 中使用。")
    
    # 同时在控制台显示前几个点作为预览
    print("\n路径预览（前5个点）:")
    for i, (lon, lat) in enumerate(waypoints[:5]):
        print(f"  {i+1}. ({lat}, {lon})")
    
    if len(waypoints) > 5:
        print(f"  ...")
        print(f"  总共 {len(waypoints)} 个点")
