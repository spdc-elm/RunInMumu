# GPX Path Parsing

## Purpose
Parse GPS waypoints from GPX (GPS Exchange Format) XML files and provide path simplification utilities.

## Requirements

### Requirement: GPX File Parsing
The system SHALL parse GPX 1.1 format XML files to extract waypoint coordinates.

#### Scenario: Parse valid GPX file
- **WHEN** a GPX file path is provided
- **THEN** the system parses the XML using ElementTree
- **AND** locates all `<wpt>` tags under the GPX 1.1 namespace `http://www.topografix.com/GPX/1/1`
- **AND** extracts `lat` and `lon` attributes from each waypoint
- **AND** returns a list of (longitude, latitude) tuples

#### Scenario: Handle missing GPX file
- **WHEN** the specified GPX file does not exist
- **THEN** the system raises a FileNotFoundError
- **AND** propagates the error to the caller

#### Scenario: Handle malformed GPX XML
- **WHEN** the GPX file contains invalid XML
- **THEN** the system raises an XML parsing error
- **AND** propagates the error to the caller

### Requirement: Duplicate Waypoint Removal
The system SHALL remove consecutive duplicate waypoints from a coordinate list.

#### Scenario: Remove exact duplicates
- **WHEN** two consecutive waypoints have identical coordinates
- **THEN** the system keeps only the first waypoint
- **AND** removes the duplicate

#### Scenario: Remove near-duplicates within tolerance
- **WHEN** two consecutive waypoints differ by less than tolerance (default 1e-6 degrees)
- **THEN** the system treats them as duplicates
- **AND** keeps only the first waypoint

#### Scenario: Preserve first waypoint
- **WHEN** removing duplicates from any list
- **THEN** the system always includes the first waypoint in the result

#### Scenario: Handle empty waypoint list
- **WHEN** an empty list is provided
- **THEN** the system returns an empty list

### Requirement: Path Simplification
The system SHALL provide downsampling to reduce the number of waypoints.

#### Scenario: Downsample by step interval
- **WHEN** simplifying with step N
- **THEN** the system selects every Nth waypoint (indices 0, N, 2N, 3N, ...)
- **AND** always includes the first waypoint (index 0)

#### Scenario: Preserve last waypoint
- **WHEN** simplifying any path
- **THEN** the system always includes the last waypoint in the result
- **AND** adds it if not already selected by step interval

#### Scenario: Handle empty input
- **WHEN** an empty waypoint list is provided
- **THEN** the system returns an empty list

### Requirement: Python Code Generation
The system SHALL format waypoint lists as Python source code.

#### Scenario: Generate typed Python list
- **WHEN** formatting waypoints for Python
- **THEN** the system generates a variable assignment `WALK_PATH: List[Tuple[float, float]] = [`
- **AND** formats each waypoint as `(lat, lon)` with proper indentation
- **AND** adds comma after each element except the last
- **AND** closes with `]`

#### Scenario: Format coordinates with full precision
- **WHEN** formatting coordinates
- **THEN** the system preserves the original floating-point precision
- **AND** does not round or truncate values

### Requirement: Interactive CLI Tool
The system SHALL provide an interactive command-line interface when run directly.

#### Scenario: Parse and display waypoint count
- **WHEN** the tool is run on `run.gpx`
- **THEN** it parses the file and displays total waypoint count
- **AND** removes duplicates and displays the deduplicated count

#### Scenario: Offer simplification options
- **WHEN** the user is prompted for output options
- **THEN** the tool presents choices: all points, step=10, step=20, step=50
- **AND** defaults to option 1 (all points) if user presses Enter

#### Scenario: Generate output file
- **WHEN** processing is complete
- **THEN** the tool writes output to `walk_path.py`
- **AND** includes import statement `from typing import List, Tuple`
- **AND** includes the formatted `WALK_PATH` variable
- **AND** displays confirmation message with output filename

#### Scenario: Preview waypoints
- **WHEN** output is generated
- **THEN** the tool displays the first 5 waypoints in console
- **AND** shows total count if more than 5 waypoints exist

## Usage Example

```bash
python gpx_parser.py
```

```
正在解析 GPX 文件: run.gpx
总共找到 500 个路径点
去重后剩余 450 个路径点

选择输出选项:
1. 使用所有去重后的点（推荐用于精确路径）
2. 简化路径，每10个点取1个（减少数据量）
3. 简化路径，每20个点取1个（大幅减少数据量）
4. 简化路径，每50个点取1个（最少数据量）

请选择 (1-4，默认为1): 2
简化后剩余 45 个路径点

✓ 路径已保存到: walk_path.py
```

## Non-Requirements
- The system does NOT parse GPX tracks (`<trk>`) or routes (`<rte>`) - only waypoints (`<wpt>`)
- The system does NOT validate coordinate ranges (latitude ±90°, longitude ±180°)
- The system does NOT support GPX versions other than 1.1
- The system does NOT perform advanced path simplification algorithms (e.g., Douglas-Peucker)
- The system does NOT preserve GPX metadata (elevation, time, name, description)
