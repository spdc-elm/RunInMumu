# Design: Accelerometer Sensor Data Simulation

## Context
The target application (identified through reverse engineering) validates running activities using accelerometer data to detect fake GPS spoofing. The app stores sensor readings in `/storage/emulated/0/sensor/<uuid>.txt` and uploads them after the run completes.

## Goals
- Generate realistic accelerometer magnitude data that correlates with simulated running speed
- Match the data format and file location expected by the target app
- Provide flexible integration: automatic or manual invocation

## Non-Goals
- Real-time sensor emulation (data is pre-generated)
- Full 3-axis accelerometer simulation (only magnitude is uploaded)
- Retrofitting sensor data for past runs

## Technical Decisions

### Data Generation Algorithm

**Accelerometer magnitude formula** (based on real sensor analysis):
```
magnitude = baseline + walking_component + noise
```

Where:
- **baseline**: Gravity component (~9.8 m/s²)
- **walking_component**: Periodic oscillation based on step frequency
  - Frequency: 2.5-3.0 Hz (150-180 steps/min typical running cadence)
  - Amplitude: 10-60 m/s² depending on speed
  - Pattern: Sine wave with random phase shifts to simulate gait variation
- **noise**: Random variation (±2-5 m/s²) to simulate sensor jitter

**Speed correlation**:
- Slow pace (2.0 m/s): amplitude 15-30 m/s²
- Medium pace (3.0 m/s): amplitude 25-45 m/s²
- Fast pace (4.0+ m/s): amplitude 35-60 m/s²

### File Format

**Raw data file** (`/storage/emulated/0/sensor/<uuid>.txt`):
```
[12.768,19.361,7.184,8.437,10.151,...]
```
- Comma-separated float values
- Wrapped in square brackets
- Sampling rate: 10 Hz (100ms intervals)
- Duration: Matches GPS simulation run time

**UUID generation**:
- Use Python `uuid.uuid4()` for unique filename
- Format: `{uuid}.txt`

### File Delivery Method

**ADB Push approach**:
```bash
adb push sensor_data.txt /storage/emulated/0/sensor/{uuid}.txt
```

**Advantages**:
- Simple and direct
- Works with existing emulator connection
- No need to modify app internals

**Permission handling**:
- Files pushed via ADB are world-readable by default
- Target app should have storage permissions (already required for GPS)

### Integration Options

#### Option A: Automatic (Preferred)
- Sensor data generation happens during GPS simulation
- Data is written to emulator right before user clicks "end run"
- Requires user to wait for prompt before ending run in app

#### Option B: Manual Standalone Script
- User runs `sensor_simulator.py` separately
- Provides run duration as parameter
- Useful for debugging or custom scenarios

### Data Validation Strategy

Compare generated data against real samples:
- **Mean value**: Should be in range 25-40 m/s²
- **Standard deviation**: Should be 10-20 m/s²
- **Periodicity**: FFT should show peak at 2.5-3.0 Hz
- **Min/Max**: Should stay within 0-100 m/s² range

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Generated data looks too perfect (uniform pattern) | Add random phase shifts, variable step frequency, occasional spikes |
| Server-side ML detection of fake data | Use real sensor samples as training data, inject realistic noise patterns |
| Timing mismatch between GPS and sensor data | Ensure sensor data duration matches GPS simulation duration exactly |
| File not readable by app | Verify ADB push permissions, test with simple read operation |

## Migration Plan

**Phase 1: Standalone Implementation**
1. Create `sensor_simulator.py` as independent script
2. User manually runs it with duration parameter
3. Validate output matches expected format

**Phase 2: Integration**
4. Add hook in `main.py` to call sensor generation before exit
5. Auto-detect run duration from GPS simulation
6. Add config option `generate_sensor_data: true/false`

**Phase 3: Refinement**
7. Analyze real sensor data patterns more deeply
8. Fine-tune generation algorithm based on detection feedback
9. Add multiple pattern templates for variety

## Open Questions

1. **Should we generate sensor data for the entire emulator uptime or just the run duration?**
   - Decision: Just run duration (simpler, matches app behavior)

2. **How to handle UUID persistence? Should we reuse or always generate new?**
   - Decision: Always generate new UUID per run (matches app behavior)

3. **Should sensor data generation be synchronous or async?**
   - Decision: Synchronous (run ends quickly, no need for async)
