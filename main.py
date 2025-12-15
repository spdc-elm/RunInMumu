import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from prettytable import PrettyTable

from gpx_parser import parse_gpx, remove_duplicates

# --- 全局配置 ---
CONFIG_PATH = Path("config.json")

JITTER_RADIUS_M = 0.1  # 定位抖动半径（米），模拟定位失真
BASE_SPEED_MPS = 2.8  # 平均速度（米/秒）- 约3km/18分钟 = 2.8m/s
SPEED_JITTER_RATIO = 0.20  # 速度波动 ±20%，模拟步频变化
TICK_INTERVAL_SEC = 0.40  # GPS位置更新间隔（秒）
DIST_LIMIT_M = 4000  # 总距离阈值（米）- 约3.2公里

# --- 终端颜色定义 ---
CLR_A = "\x1b[01;38;5;117m"
CLR_P = "\x1b[01;38;5;153m"
CLR_C = "\x1b[01;38;5;123m"
HEART = "\x1b[01;38;5;195m"
CLR_RST = "\x1b[0m"


def load_config() -> dict:
    """读取配置文件"""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            sys.exit(f"{CLR_A}× config.json 格式错误: {exc}{CLR_RST}")
    return {}


def save_config(cfg: dict) -> None:
    """写回配置文件"""
    CONFIG_PATH.write_text(
        json.dumps(cfg, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def resolve_path(path_str: str) -> Path:
    """将配置中的路径解析为绝对路径"""
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path
    return CONFIG_PATH.parent / path


def _manager_exists(emu_dir: Path) -> bool:
    return emu_dir.joinpath("MuMuManager.exe").is_file() or emu_dir.joinpath("../MuMuManager.exe").is_file()


def _pick_best_emu_dir(base_dir: Path) -> Path:
    """根据目录结构返回更合适的 emu_dir (MuMu12 使用 nx_main)"""
    nx_main = base_dir / "nx_main"
    if nx_main.joinpath("adb.exe").is_file():
        return nx_main
    return base_dir


def find_emu_dir(cfg: dict) -> Path:
    """从配置或磁盘搜索 MuMu 模拟器目录"""
    emu_dir_value = cfg.get("emu_dir")
    if emu_dir_value:
        emu_dir = resolve_path(emu_dir_value)
        if _manager_exists(emu_dir):
            print(f"{CLR_C}✔ 从 config.json 成功加载模拟器路径: {emu_dir}{CLR_RST}")
            return emu_dir
        print(f"{CLR_P}在 config.json 中找到的路径无效，将尝试自动搜索...{CLR_RST}")

    print(f"{CLR_P}未找到有效配置, 开始搜索 MuMu 安装目录...{CLR_RST}")
    search_roots = [Path(f"{d}:/") for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{d}:/").exists()]
    for root in search_roots:
        try:
            for mgr_path in root.rglob("MuMuManager.exe"):
                emu_dir = _pick_best_emu_dir(mgr_path.parent)
                cfg["emu_dir"] = str(emu_dir)
                save_config(cfg)
                print(f"{CLR_C}✔ 找到并保存 MuMu 路径: {emu_dir}{CLR_RST}")
                return emu_dir
        except PermissionError:
            continue

    sys.exit(f"{CLR_A}× 未能找到 MuMu 模拟器, 请检查是否已安装或在 config.json 中手动指定路径。{CLR_RST}")


def _coerce_lat_lon(pair: Sequence[float]) -> Tuple[float, float]:
    if not isinstance(pair, Sequence) or len(pair) != 2:
        raise ValueError("坐标点必须是包含两个元素的序列")
    lat, lon = pair
    return float(lat), float(lon)


def _coerce_offset(cfg: dict) -> Tuple[float, float]:
    """解析位置偏移量 (度)"""
    offset_cfg = cfg.get("location_offset")
    if not offset_cfg:
        return 0.0, 0.0
    try:
        lat = float(offset_cfg["lat"])
        lon = float(offset_cfg["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        sys.exit(f"{CLR_A}× location_offset 配置无效: {exc}{CLR_RST}")
    return lat, lon


def load_walk_path(cfg: dict) -> Tuple[List[Tuple[float, float]], Tuple[float, float]]:
    """从配置文件或外部文件加载行走路径及偏移量"""
    offset = _coerce_offset(cfg)

    if "walk_path" in cfg:
        route = [_coerce_lat_lon(item) for item in cfg["walk_path"]]
        if route:
            print(f"{CLR_C}✔ 从 config.json 加载路径: {len(route)} 个点{CLR_RST}")
            return route, offset

    walk_path_file = cfg.get("walk_path_file")
    if walk_path_file:
        path = resolve_path(walk_path_file)
        if not path.exists():
            sys.exit(f"{CLR_A}× walk_path_file 指定的文件不存在: {path}{CLR_RST}")

        suffix = path.suffix.lower()
        if suffix == ".gpx":
            raw_points = remove_duplicates(parse_gpx(str(path)))
            route = [(float(lat), float(lon)) for lon, lat in raw_points]
        elif suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            route = [_coerce_lat_lon(item) for item in data]
        elif suffix == ".py":
            namespace: dict = {}
            exec(path.read_text(encoding="utf-8"), namespace)
            if "WALK_PATH" not in namespace:
                sys.exit(f"{CLR_A}× {path} 中未找到 WALK_PATH 变量{CLR_RST}")
            route = [_coerce_lat_lon(item) for item in namespace["WALK_PATH"]]
        else:
            sys.exit(f"{CLR_A}× 不支持的路径文件类型: {path}{CLR_RST}")

        if not route:
            sys.exit(f"{CLR_A}× 路径文件 {path} 未提供任何坐标点{CLR_RST}")

        print(f"{CLR_C}✔ 从 {path.name} 加载路径: {len(route)} 个点{CLR_RST}")
        return route, offset

    default_gpx = Path("run.gpx")
    if default_gpx.exists():
        cfg["walk_path_file"] = default_gpx.name
        save_config(cfg)
        return load_walk_path(cfg)

    sys.exit(f"{CLR_A}× 未配置 walker 路径，请在 config.json 中提供 walk_path 或 walk_path_file。{CLR_RST}")

def connect_to_emulator(emu_dir: Path) -> Path:

    """连接到正在运行的 MuMu 模拟器，并返回 MuMuManager 路径"""
    if emu_dir.joinpath("MuMuManager.exe").is_file():
        mgr_path = emu_dir / "MuMuManager.exe"
        adb_path = emu_dir / "adb.exe"
    elif emu_dir.joinpath("../MuMuManager.exe").is_file():
        mgr_path = emu_dir.parent / "MuMuManager.exe"
        adb_path = emu_dir / "adb.exe"
    else:
        sys.exit(f"{CLR_A}× 在 {emu_dir} 中找不到 MuMuManager.exe。{CLR_RST}")

    print(f"{CLR_P}正在尝试连接到模拟器...{CLR_RST}")
    try:
        adb_info_raw = subprocess.check_output([str(mgr_path), "info", "-v", "0"], encoding="utf-8")
        adb_info = json.loads(adb_info_raw)

        if "adb_port" not in adb_info or "adb_host_ip" not in adb_info:
            sys.exit(f"{CLR_A}× 获取 ADB 端口失败, 请确保模拟器正在运行。{CLR_RST}")

        adb_addr = f"{adb_info['adb_host_ip']}:{adb_info['adb_port']}"
        subprocess.run([str(adb_path), "connect", adb_addr], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"{CLR_C}✔ 成功连接到 ADB: {adb_addr}{CLR_RST}")
        return mgr_path
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as exc:
        sys.exit(f"{CLR_A}× 连接模拟器失败, 请确保模拟器已完全启动。错误: {exc}{CLR_RST}")


def meter_to_deg(lat: float, dx: float, dy: float) -> Tuple[float, float]:
    """将米转换为经纬度偏移"""
    d_lat = dy / 111_320
    d_lon = dx / (111_320 * math.cos(math.radians(lat)))
    return d_lat, d_lon


def set_location(mgr_path: Path, lon: float, lat: float, offset: Tuple[float, float]) -> None:
    """使用 MuMuManager 设置模拟器位置 (包含偏移)"""
    dx, dy = (random.uniform(-JITTER_RADIUS_M, JITTER_RADIUS_M) for _ in range(2))
    d_lat, d_lon = meter_to_deg(lat, dx, dy)

    final_lon = lon + offset[1] + d_lon
    final_lat = lat + offset[0] + d_lat

    subprocess.run(
        [
            str(mgr_path),
            "control",
            "-v",
            "0",
            "tool",
            "location",
            "-lon",
            f"{final_lon:.6f}",
            "-lat",
            f"{final_lat:.6f}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def geo_dist_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    """计算两点间的地理距离（米）"""
    return math.hypot(lat2 - lat1, lon2 - lon1) * 111_320


def simulate_walk(mgr_path: Path, route: List[Tuple[float, float]], offset: Tuple[float, float]) -> None:
    """模拟沿着路线行走"""
    if len(route) < 2:
        raise ValueError("路径点至少需要两个")

    idx, seg_dist, total_dist = 0, 0.0, 0.0
    t_start = t_prev = time.perf_counter()
    next_tick = t_prev + TICK_INTERVAL_SEC
    frame = 0

    lat, lon = route[0]
    set_location(mgr_path, lon, lat, offset)
    print(f"{CLR_C}已设置初始位置, 开始模拟行走...{CLR_RST}")

    while True:
        now = time.perf_counter()
        if now < next_tick:
            time.sleep(next_tick - now)
            now = next_tick
        next_tick += TICK_INTERVAL_SEC
        dt = now - t_prev
        t_prev = now

        lat1, lon1 = route[idx]
        lat2, lon2 = route[(idx + 1) % len(route)]
        seg_len = geo_dist_m(lat1, lon1, lat2, lon2)

        speed = BASE_SPEED_MPS * random.uniform(1 - SPEED_JITTER_RATIO, 1 + SPEED_JITTER_RATIO)
        move = speed * dt
        seg_dist += move
        total_dist += move

        while seg_len > 0 and seg_dist >= seg_len:
            seg_dist -= seg_len
            idx = (idx + 1) % len(route)
            lat1, lon1 = route[idx]
            lat2, lon2 = route[(idx + 1) % len(route)]
            seg_len = geo_dist_m(lat1, lon1, lat2, lon2)

        ratio = seg_dist / seg_len if seg_len > 0 else 0
        lat = lat1 + (lat2 - lat1) * ratio
        lon = lon1 + (lon2 - lon1) * ratio
        set_location(mgr_path, lon, lat, offset)

        frame += 1
        elapsed = now - t_start

        tbl = PrettyTable(["时间", "即时速度", "总路程", "均速", "步频"])
        tbl.add_row([
            f"{CLR_P}{elapsed:7.2f}{CLR_RST}s",
            f"{CLR_P}{speed:7.2f}{CLR_RST}m/s",
            f"{CLR_P}{total_dist:8.2f}{CLR_RST}m",
            f"{CLR_P}{total_dist/elapsed:7.2f}{CLR_RST}m/s" if elapsed > 0 else "0.00",
            f"{CLR_P}{frame/elapsed:7.2f}{CLR_RST}Hz" if elapsed > 0 else "0.00",
        ])
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{HEART}               跑步模拟进行中...               {CLR_RST}")
        print(tbl)

        if total_dist >= DIST_LIMIT_M:
            print(f"\n{CLR_A}✔ 已达到目标距离 {DIST_LIMIT_M}米, 模拟结束！{CLR_RST}")
            break


def main() -> None:
    cfg = load_config()
    emu_dir = find_emu_dir(cfg)
    mgr_path = connect_to_emulator(emu_dir)
    route, offset = load_walk_path(cfg)

    print("\n" + "=" * 40)
    print(f"{CLR_C}准备就绪！请在模拟器中手动进入跑步界面。{CLR_RST}")
    if offset != (0.0, 0.0):
        print(f"{CLR_P}已应用位置偏移: Δlat={offset[0]:.6f}, Δlon={offset[1]:.6f}{CLR_RST}")
    input(f"{CLR_P}准备好后, 按【Enter】键开始模拟走路...{CLR_RST}")

    simulate_walk(mgr_path, route, offset)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CLR_A}用户中断了脚本。再见！{CLR_RST}")
    except Exception as exc:
        print(f"\n{CLR_A}发生意外错误: {exc}{CLR_RST}")
    finally:
        input("\n按【Enter】键退出程序...")
