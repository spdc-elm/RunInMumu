import json
import subprocess
import sys
import time
from pathlib import Path

# 测试用的几个坐标点（从你的路径中选取）
TEST_POINTS = [
    (30.308288766029804, 120.07833785355666),  # 点1
    (30.308291661538462, 120.078364684865),     # 点2
    (30.308282975010897, 120.07843176313679),   # 点3
    (30.308277183991606, 120.07849548749556),   # 点4
    (30.308259810933066, 120.07854579619936),   # 点5
]

CLR_A = "\x1b[01;38;5;117m"
CLR_P = "\x1b[01;38;5;153m"
CLR_C = "\x1b[01;38;5;123m"
CLR_RST = "\x1b[0m"


def find_emu_dir() -> Path:
    """从 config.json 找到 MuMu 模拟器目录"""
    cfg = Path("config.json")
    if cfg.exists():
        try:
            emu_dir = Path(json.loads(cfg.read_text(encoding="utf-8"))["emu_dir"])
            if emu_dir.joinpath("MuMuManager.exe").is_file():
                print(f"{CLR_C}✔ 从 config.json 加载路径: {emu_dir}{CLR_RST}")
                return emu_dir
            elif emu_dir.joinpath("../MuMuManager.exe").is_file():
                print(f"{CLR_C}✔ 从 config.json 加载路径 (MuMu 12): {emu_dir}{CLR_RST}")
                return emu_dir
        except Exception as e:
            print(f"{CLR_A}× 读取 config.json 出错: {e}{CLR_RST}")
    sys.exit(f"{CLR_A}× 请先运行 main.py 生成 config.json{CLR_RST}")


def connect_to_emulator(emu_dir: Path) -> Path:
    """连接到模拟器并返回 MuMuManager 路径"""
    if emu_dir.joinpath("MuMuManager.exe").is_file():
        mgr_path = emu_dir / "MuMuManager.exe"
        adb_path = emu_dir / "adb.exe"
    elif emu_dir.joinpath("../MuMuManager.exe").is_file():
        mgr_path = emu_dir.parent / "MuMuManager.exe"
        adb_path = emu_dir / "adb.exe"
    else:
        sys.exit(f"{CLR_A}× 找不到 MuMuManager.exe{CLR_RST}")

    print(f"{CLR_P}正在连接模拟器...{CLR_RST}")
    try:
        # 获取 ADB 信息
        result = subprocess.run(
            [str(mgr_path), "info", "-v", "0"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        print(f"\n{CLR_C}=== MuMuManager info 命令输出 ==={CLR_RST}")
        print(f"返回码: {result.returncode}")
        print(f"stdout:\n{result.stdout}")
        if result.stderr:
            print(f"stderr:\n{result.stderr}")
        print(f"{CLR_C}{'='*40}{CLR_RST}\n")
        
        adb_info = json.loads(result.stdout)
        
        if "adb_port" not in adb_info or "adb_host_ip" not in adb_info:
            sys.exit(f"{CLR_A}× 获取 ADB 端口失败, 请确保模拟器正在运行{CLR_RST}")

        adb_addr = f"{adb_info['adb_host_ip']}:{adb_info['adb_port']}"
        
        # 连接 ADB
        print(f"{CLR_P}正在连接 ADB: {adb_addr}{CLR_RST}")
        adb_result = subprocess.run(
            [str(adb_path), "connect", adb_addr],
            capture_output=True,
            text=True
        )
        print(f"ADB 连接输出: {adb_result.stdout}")
        if adb_result.stderr:
            print(f"ADB 连接错误: {adb_result.stderr}")
            
        print(f"{CLR_C}✔ 成功连接到 ADB: {adb_addr}{CLR_RST}\n")
        return mgr_path
        
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        sys.exit(f"{CLR_A}× 连接失败: {e}{CLR_RST}")


def test_set_location(mgr_path: Path, lon: float, lat: float, point_num: int) -> None:
    """测试设置位置命令"""
    
    # 构建完整命令
    cmd = [
        str(mgr_path),
        "control",
        "-v", "0",
        "tool",
        "location",
        "-lon", f"{lon:.6f}",
        "-lat", f"{lat:.6f}"
    ]
    
    print(f"\n{CLR_C}=== 测试点 {point_num} ==={CLR_RST}")
    print(f"经度: {lon:.6f}")
    print(f"纬度: {lat:.6f}")
    print(f"\n完整命令:")
    print(f"{CLR_P}{' '.join(cmd)}{CLR_RST}")
    
    # 执行命令并捕获输出
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    print(f"\n命令执行结果:")
    print(f"返回码: {result.returncode}")
    
    if result.stdout:
        print(f"stdout:\n{result.stdout}")
    else:
        print(f"stdout: (无输出)")
        
    if result.stderr:
        print(f"stderr:\n{result.stderr}")
    else:
        print(f"stderr: (无输出)")
    
    print(f"{CLR_C}{'='*60}{CLR_RST}")


def main():
    print(f"{CLR_C}{'='*60}{CLR_RST}")
    print(f"{CLR_C}  MuMu 虚拟定位测试程序{CLR_RST}")
    print(f"{CLR_C}{'='*60}{CLR_RST}\n")
    
    try:
        # 查找并连接模拟器
        emu_dir = find_emu_dir()
        mgr_path = connect_to_emulator(emu_dir)
        
        print(f"{CLR_P}将测试 {len(TEST_POINTS)} 个位置点，每个点间隔 2 秒{CLR_RST}")
        print(f"{CLR_P}请在模拟器中打开需要定位的应用，准备好后按 Enter 开始...{CLR_RST}")
        input()
        
        # 循环测试每个点
        for i, (lat, lon) in enumerate(TEST_POINTS, 1):
            test_set_location(mgr_path, lon, lat, i)
            
            if i < len(TEST_POINTS):
                print(f"\n{CLR_A}等待 2 秒后测试下一个点...{CLR_RST}")
                time.sleep(2)
        
        print(f"\n{CLR_C}✔ 测试完成！{CLR_RST}")
        print(f"\n{CLR_P}提示: 如果应用中的位置没有变化，可能的原因:{CLR_RST}")
        print(f"  1. 应用没有定位权限")
        print(f"  2. 模拟器的虚拟定位功能未开启")
        print(f"  3. 需要在模拟器设置中启用'允许模拟位置'")
        print(f"  4. MuMuManager 版本不支持该命令")
        
    except KeyboardInterrupt:
        print(f"\n{CLR_A}用户中断测试{CLR_RST}")
    except Exception as e:
        print(f"\n{CLR_A}发生错误: {e}{CLR_RST}")
        import traceback
        traceback.print_exc()
    
    input(f"\n{CLR_P}按 Enter 键退出...{CLR_RST}")


if __name__ == "__main__":
    main()
