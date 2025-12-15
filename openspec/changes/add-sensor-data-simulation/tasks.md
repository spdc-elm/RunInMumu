# Implementation Tasks

## 1. Sensor Data Generation
- [x] 1.1 Create `sensor_simulator.py` module
- [x] 1.2 Implement function to generate acceleration magnitude array based on:
  - Total run duration (user input)
  - Speed profile (correlate with speed variations)
  - Step frequency (typical running cadence: 150-180 steps/min, 2.5-3.0 Hz)
- [x] 1.3 Add realistic noise and variation (analyzed 28 real sensor samples, 319k+ data points)
- [x] 1.4 Generate data at 100ms intervals (10 Hz sampling rate)

## 2. File Operations
- [x] 2.1 Query existing sensor files via ADB `ls -t` (sorted by modification time)
- [x] 2.2 Let user select which file to replace (default: most recent)
- [x] 2.3 Format data as comma-separated float values in JSON array format
- [x] 2.4 Use ADB to push file to `/storage/emulated/0/sensor/` on emulator (same filename replacement)
- [x] 2.5 Verify file transfer success with error handling

## 3. Integration Approach
- [x] 3.1 Implemented Option B: Standalone script user runs manually
- [x] 3.2 Interactive CLI with colored output and clear prompts
- [x] 3.3 Smart defaults (1143s duration, 2.8 m/s speed)
- [x] 3.4 Display confirmation message with file path when complete

## 4. Testing & Validation
- [x] 4.1 Compare generated data patterns with real sensor samples
  - Mean: 15.47 vs 14.98 (3.3% diff) ✓
  - StdDev: 10.09 vs 12.20 (17.3% diff) ✓
- [x] 4.2 Create test scripts (`test_sensor_gen.py`, `compare_sensor_data.py`)
- [x] 4.3 Create ADB query test (`test_adb_query.py`)
- [ ] 4.4 Real-world test: Verify app accepts and uploads the data (user validation required)

## 5. Documentation
- [x] 5.1 Create `SENSOR_USAGE.md` with comprehensive usage instructions
- [x] 5.2 Add detailed code comments explaining algorithm
- [x] 5.3 Document data generation principles and statistical validation
- [x] 5.4 Include troubleshooting section

## 6. Implementation Notes

**Key Design Decisions:**
- **File replacement**: Uses same filename as app-generated file (not new UUID)
- **File selection**: User chooses from list, defaults to most recent (index 1)
- **Data quality**: Matches real data statistics (mean ±3%, stddev ±17%)
- **Algorithm**: Multi-harmonic sine wave + Gaussian noise + irregular stepping

**Files Created:**
- `sensor_simulator.py` - Main implementation (10.9KB)
- `SENSOR_USAGE.md` - User documentation (updated)
- `test_sensor_gen.py` - Quick validation test
- `compare_sensor_data.py` - Statistical comparison tool
- `test_adb_query.py` - ADB file query test
