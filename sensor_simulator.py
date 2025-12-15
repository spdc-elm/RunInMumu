#!/usr/bin/env python3
"""
传感器数据模拟器 - 一键生成并推送加速度传感器数据到MuMu模拟器

功能：
1. 通过ADB列出模拟器中的sensor文件
2. 根据修改时间筛选最近的文件
3. 生成符合真实运动模式的加速度数据
4. 推送到模拟器的/storage/emulated/0/sensor/目录
"""

import json
import math
import random
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

# --- 终端颜色定义 ---
CLR_A = "\x1b[01;38;5;117m"
CLR_P = "\x1b[01;38;5;153m"
CLR_C = "\x1b[01;38;5;123m"
HEART = "\x1b[01;38;5;195m"
CLR_RST = "\x1b[0m"

# --- 传感器数据参数 ---
SAMPLING_RATE_HZ = 10  # 采样率：10Hz (每100ms一个数据点)
GRAVITY = 9.8  # 重力加速度基线

# 步频参数（跑步节奏）
STEP_FREQ_MIN = 2.5  # 最小步频 (Hz) - 150步/分钟
STEP_FREQ_MAX = 3.0  # 最大步频 (Hz) - 180步/分钟

# 幅度参数（根据全部真实数据统计: mean=14.98, std=12.20）
AMPLITUDE_BASE = 15.0  # 基础幅度
AMPLITUDE_VARIATION = 38.0  # 幅度变化范围
NOISE_STDDEV = 7.0  # 噪声标准差


def load_config() -> dict:
    """读取配置文件"""
    config_path = Path("config.json")
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{CLR_A}× 配置文件格式错误: {exc}{CLR_RST}")
            return {}
    return {}


def find_adb_path(cfg: dict) -> Path:
    """从配置中找到adb路径"""
    emu_dir = cfg.get("emu_dir")
    if not emu_dir:
        sys.exit(f"{CLR_A}× 未找到模拟器配置，请先运行 main.py{CLR_RST}")
    
    emu_path = Path(emu_dir)
    adb_path = emu_path / "adb.exe"
    
    if not adb_path.exists():
        sys.exit(f"{CLR_A}× 未找到 adb.exe: {adb_path}{CLR_RST}")
    
    return adb_path


def get_recent_sensor_files(adb_path: Path, minutes: int = 120) -> List[Tuple[str, str, str]]:
    """
    获取模拟器中最近N分钟内修改的sensor文件
    
    Returns:
        [(filename, date, time), ...] 按时间倒序排列
    """
    print(f"{CLR_P}正在查询模拟器中的sensor文件...{CLR_RST}")
    
    # 使用stat命令获取更可靠的文件信息
    cmd = [
        str(adb_path),
        "shell",
        "cd /storage/emulated/0/sensor && ls -t *.txt 2>/dev/null | head -n 20"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        output = result.stdout.strip()
        
        if not output or "No such file" in output:
            print(f"{CLR_P}  目录为空或不存在{CLR_RST}")
            return []
        
        files = []
        for line in output.split('\n'):
            filename = line.strip()
            if filename.endswith('.txt'):
                # 获取文件修改时间
                stat_cmd = [
                    str(adb_path),
                    "shell",
                    f"stat -c '%y' /storage/emulated/0/sensor/{filename} 2>/dev/null || echo ''"
                ]
                try:
                    stat_result = subprocess.run(stat_cmd, capture_output=True, text=True, encoding="utf-8", timeout=2)
                    timestamp = stat_result.stdout.strip()
                    if timestamp:
                        # 格式: 2024-12-15 14:30:45.123456789 +0800
                        parts = timestamp.split()
                        if len(parts) >= 2:
                            date_str = parts[0]
                            time_str = parts[1].split('.')[0]  # 去掉纳秒
                            files.append((filename, date_str, time_str))
                        else:
                            files.append((filename, "unknown", "unknown"))
                    else:
                        files.append((filename, "unknown", "unknown"))
                except:
                    files.append((filename, "unknown", "unknown"))
        
        return files  # ls -t 已经按时间排序，最新的在前
    
    except Exception as e:
        print(f"{CLR_A}ERROR 查询文件失败: {e}{CLR_RST}")
        return []


def generate_sensor_data(duration_sec: float, avg_speed_mps: float = 2.8) -> List[float]:
    """
    生成模拟的加速度传感器数据（幅值）
    
    Args:
        duration_sec: 运动持续时间（秒）
        avg_speed_mps: 平均速度（米/秒）
    
    Returns:
        加速度幅值列表
    """
    num_samples = int(duration_sec * SAMPLING_RATE_HZ)
    data = []
    
    # 根据速度调整幅度（保持接近真实均值）
    speed_factor = avg_speed_mps / 2.8  # 归一化到默认速度
    amplitude = AMPLITUDE_BASE * (0.85 + 0.15 * speed_factor)  # 轻微调整
    
    # 随机步频（在范围内）
    step_freq = random.uniform(STEP_FREQ_MIN, STEP_FREQ_MAX)
    
    print(f"{CLR_C}生成参数:{CLR_RST}")
    print(f"  采样数: {num_samples}")
    print(f"  步频: {step_freq:.2f} Hz ({step_freq*60:.0f} 步/分钟)")
    print(f"  基础幅度: {amplitude:.2f} m/s^2")
    
    for i in range(num_samples):
        t = i / SAMPLING_RATE_HZ  # 当前时间点（秒）
        
        # 基础周期分量（步频）
        phase = 2 * math.pi * step_freq * t
        
        # 组合多个分量模拟真实步态
        periodic = (
            0.6 * math.sin(phase) +  # 基础步频
            0.3 * math.sin(2 * phase) +  # 二次谐波
            0.1 * math.sin(3 * phase)  # 三次谐波
        )
        
        # 不规则性：每几步改变幅度
        if i == 0 or i % int(SAMPLING_RATE_HZ * 1.2) == 0:
            irregular_factor = random.uniform(0.6, 1.4)
        
        # 组合：基线 + 周期分量 + 噪声
        value = (
            amplitude +  # 基础幅度
            periodic * AMPLITUDE_VARIATION * 0.45 * irregular_factor +  # 周期变化
            random.gauss(0, NOISE_STDDEV)  # 高斯噪声
        )
        
        # 限制在合理范围内（0-100 m/s²）
        value = max(0.5, min(100.0, value))
        
        data.append(round(value, 6))
    
    return data


def write_sensor_file(data: List[float], filename: str) -> Path:
    """
    将传感器数据写入本地临时文件
    
    Returns:
        临时文件路径
    """
    temp_path = Path(filename)
    
    # 格式化为JSON数组（紧凑格式，无空格）
    content = "[" + ",".join(str(v) for v in data) + "]"
    
    temp_path.write_text(content, encoding="utf-8")
    print(f"{CLR_C}OK 已生成本地文件: {temp_path} ({len(content)} 字节){CLR_RST}")
    
    return temp_path


def push_to_emulator(adb_path: Path, local_file: Path, remote_filename: str) -> bool:
    """
    通过ADB推送文件到模拟器
    
    Returns:
        是否成功
    """
    remote_path = f"/storage/emulated/0/sensor/{remote_filename}"
    
    # 确保目录存在
    print(f"{CLR_P}确保模拟器目录存在...{CLR_RST}")
    mkdir_cmd = [str(adb_path), "shell", "mkdir -p /storage/emulated/0/sensor"]
    subprocess.run(mkdir_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 推送文件
    print(f"{CLR_P}正在推送文件到模拟器...{CLR_RST}")
    push_cmd = [str(adb_path), "push", str(local_file), remote_path]
    
    try:
        result = subprocess.run(push_cmd, capture_output=True, text=True, check=True)
        print(f"{CLR_C}OK 推送成功: {remote_path}{CLR_RST}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR_A}ERROR 推送失败: {e.stderr}{CLR_RST}")
        return False


def main():
    """主流程"""
    print(f"\n{HEART}{'='*60}{CLR_RST}")
    print(f"{HEART}  传感器数据模拟器{CLR_RST}")
    print(f"{HEART}{'='*60}{CLR_RST}\n")
    
    # 1. 加载配置并找到ADB
    cfg = load_config()
    adb_path = find_adb_path(cfg)
    print(f"{CLR_C}OK 找到 ADB: {adb_path}{CLR_RST}\n")
    
    # 2. 查询最近的sensor文件
    recent_files = get_recent_sensor_files(adb_path, minutes=120)
    
    target_filename = None
    
    if not recent_files:
        print(f"\n{CLR_A}未找到已有的sensor文件{CLR_RST}")
        print(f"{CLR_P}将创建新文件（不推荐，建议先在应用中开始跑步）{CLR_RST}\n")
        
        use_new = input(f"{CLR_A}是否创建新文件? (y/N): {CLR_RST}").strip().lower()
        if use_new == 'y':
            file_uuid = str(uuid.uuid4())
            target_filename = f"{file_uuid}.txt"
            print(f"{CLR_C}将创建新文件: {target_filename}{CLR_RST}")
        else:
            print(f"{CLR_A}已取消操作{CLR_RST}")
            sys.exit(0)
    else:
        print(f"\n{CLR_C}找到 {len(recent_files)} 个sensor文件 (按修改时间排序):{CLR_RST}\n")
        
        # 显示文件列表
        for i, (filename, date_str, time_str) in enumerate(recent_files[:10], 1):
            if date_str != "unknown":
                print(f"  {i}. {filename}")
                print(f"     修改时间: {date_str} {time_str}")
            else:
                print(f"  {i}. {filename}")
            print()
        
        if len(recent_files) > 10:
            print(f"  ... 还有 {len(recent_files)-10} 个文件\n")
        
        # 让用户选择要替换的文件
        print(f"{CLR_P}请选择要替换的文件 (输入序号):{CLR_RST}")
        print(f"{CLR_P}  提示: 通常选择 1 (最近修改的文件，即本次跑步){CLR_RST}")
        
        try:
            choice_input = input(f"{CLR_A}选择 [{CLR_P}1{CLR_A}]: {CLR_RST}").strip()
            choice = int(choice_input) if choice_input else 1
            
            if 1 <= choice <= len(recent_files):
                target_filename = recent_files[choice - 1][0]
                print(f"\n{CLR_C}>> 将替换文件: {target_filename}{CLR_RST}")
            else:
                print(f"{CLR_A}ERROR 无效选择{CLR_RST}")
                sys.exit(1)
        except ValueError:
            print(f"{CLR_A}ERROR 输入无效{CLR_RST}")
            sys.exit(1)
    
    # 3. 询问用户运动时长
    print(f"\n{CLR_P}请输入本次跑步的持续时间(秒):{CLR_RST}")
    print(f"{CLR_P}  提示: 3200米 @ 2.8m/s ~= 1143秒 ~= 19分钟{CLR_RST}")
    
    try:
        duration_input = input(f"{CLR_A}时长(秒) [{CLR_P}1143{CLR_A}]: {CLR_RST}").strip()
        duration = float(duration_input) if duration_input else 1143.0
    except ValueError:
        print(f"{CLR_A}ERROR 输入无效，使用默认值 1143秒{CLR_RST}")
        duration = 1143.0
    
    # 4. 询问平均速度
    try:
        speed_input = input(f"{CLR_A}平均速度(m/s) [{CLR_P}2.8{CLR_A}]: {CLR_RST}").strip()
        avg_speed = float(speed_input) if speed_input else 2.8
    except ValueError:
        print(f"{CLR_A}ERROR 输入无效，使用默认值 2.8 m/s{CLR_RST}")
        avg_speed = 2.8
    
    print(f"\n{CLR_C}开始生成传感器数据...{CLR_RST}")
    
    # 5. 生成数据
    sensor_data = generate_sensor_data(duration, avg_speed)
    
    # 统计信息
    import statistics
    print(f"\n{CLR_C}数据统计:{CLR_RST}")
    print(f"  数据点数: {len(sensor_data)}")
    print(f"  平均值: {statistics.mean(sensor_data):.2f} m/s^2")
    print(f"  标准差: {statistics.stdev(sensor_data):.2f} m/s^2")
    print(f"  最小值: {min(sensor_data):.2f} m/s^2")
    print(f"  最大值: {max(sensor_data):.2f} m/s^2")
    
    # 6. 写入本地文件（使用选定的文件名）
    print(f"\n{CLR_C}目标文件: {target_filename}{CLR_RST}")
    local_file = write_sensor_file(sensor_data, target_filename)
    
    # 7. 推送到模拟器（同名替换）
    print()
    success = push_to_emulator(adb_path, local_file, target_filename)
    
    if success:
        print(f"\n{CLR_C}{'='*60}{CLR_RST}")
        print(f"{HEART}  SUCCESS! 传感器数据已替换！{CLR_RST}")
        print(f"{CLR_C}{'='*60}{CLR_RST}")
        print(f"\n{CLR_P}模拟器文件路径:{CLR_RST}")
        print(f"  /storage/emulated/0/sensor/{target_filename}")
        print(f"\n{CLR_A}现在可以在应用中点击[结束跑步]了！{CLR_RST}\n")
        
        # 清理本地临时文件
        try:
            local_file.unlink()
            print(f"{CLR_P}(已删除本地临时文件){CLR_RST}")
        except:
            pass
    else:
        print(f"\n{CLR_A}ERROR 操作失败，请检查错误信息{CLR_RST}\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CLR_A}用户中断操作{CLR_RST}")
    except Exception as exc:
        print(f"\n{CLR_A}发生错误: {exc}{CLR_RST}")
        import traceback
        traceback.print_exc()
    finally:
        input(f"\n{CLR_P}按【Enter】退出...{CLR_RST}")
