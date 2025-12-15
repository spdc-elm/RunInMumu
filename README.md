# RunInMumu - MuMu模拟器跑步模拟工具

基于MuMu模拟器的GPS和传感器数据模拟工具，用于自动化跑步应用测试。

## 快速开始

### 1. GPS路径模拟

```bash
python main.py
```

- 自动检测MuMu模拟器
- 加载GPX路径文件
- 模拟GPS移动（支持速度变化、位置抖动）
- 实时显示进度

### 2. 传感器数据替换

**在应用中点击"结束跑步"之前运行：**

```bash
python sensor_simulator.py
```

- 列出最近的sensor文件
- 选择要替换的文件（通常选1）
- 输入运动时长和速度
- 自动生成并替换数据

### 3. 结束跑步

在模拟器中点击"结束跑步"，数据将被上传。

## 核心功能

### GPS模拟 (`main.py`)
- ✓ 自动发现MuMu模拟器安装路径
- ✓ 支持GPX/JSON/Python多种路径格式
- ✓ 循环路径支持（适合操场跑圈）
- ✓ 速度抖动（±20%）和位置抖动（±2米）
- ✓ 位置偏移配置
- ✓ 实时进度显示

### 传感器模拟 (`sensor_simulator.py`)
- ✓ ADB查询并列出已有sensor文件
- ✓ 同名替换（匹配应用生成的文件）
- ✓ 真实数据统计特征（基于28个样本，31万+数据点）
- ✓ 步频仿真（150-180步/分钟）
- ✓ 多谐波波形 + 高斯噪声

## 配置文件

`config.json`:
```json
{
    "emu_dir": "D:\\software\\MuMu Player 12\\nx_main",
    "walk_path_file": "run.gpx",
    "location_offset": {
        "lat": 0.0036674,
        "lon": 0.0114375
    }
}
```

## 工具脚本

- `gpx_parser.py` - GPX文件解析和路径简化
- `test_sensor_gen.py` - 传感器数据生成测试
- `compare_sensor_data.py` - 数据质量对比分析
- `test_adb_query.py` - ADB文件查询测试

## 文件结构

```
RunInMumu/
├── main.py                    # GPS模拟主程序
├── sensor_simulator.py        # 传感器数据模拟器
├── gpx_parser.py             # GPX解析工具
├── config.json               # 配置文件
├── run.gpx                   # GPS路径文件
├── real_sensor/              # 真实传感器数据样本（28个）
├── SENSOR_USAGE.md          # 传感器模拟详细文档
└── openspec/                # OpenSpec规范文档
    ├── specs/               # 功能规范
    │   ├── gps-simulation/
    │   ├── configuration-management/
    │   └── gpx-path-parsing/
    └── changes/             # 变更提案
        └── add-sensor-data-simulation/
```

## 依赖

- Python 3.10+
- MuMu模拟器（NetEase）
- PrettyTable (`pip install prettytable`)

## 数据质量

传感器数据生成质量对比：

| 指标 | 真实数据 | 生成数据 | 差异 |
|------|---------|---------|------|
| 平均值 | 14.98 m/s² | 15.47 m/s² | 3.3% |
| 标准差 | 12.20 m/s² | 10.09 m/s² | 17.3% |
| 采样率 | 10 Hz | 10 Hz | 0% |

## 注意事项

1. **运行顺序**：先运行GPS模拟(`main.py`)，再运行传感器模拟(`sensor_simulator.py`)
2. **手动准备**：需要手动在应用中进入跑步界面
3. **时机**：在应用中点击"结束"之前运行传感器模拟
4. **文件选择**：通常选择最新的文件（序号1）
5. **参数匹配**：传感器数据的时长应与实际GPS模拟时长一致

## 技术细节

详见：
- [传感器使用文档](SENSOR_USAGE.md)
- [OpenSpec规范](openspec/specs/)
- [变更提案](openspec/changes/add-sensor-data-simulation/)

## License

MIT

## 致谢

基于真实传感器数据分析和逆向工程实现。
