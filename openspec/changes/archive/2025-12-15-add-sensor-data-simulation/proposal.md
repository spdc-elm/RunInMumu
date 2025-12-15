# Change: Add Accelerometer Sensor Data Simulation

## Why
The target fitness application validates GPS-based running activities by cross-checking with accelerometer sensor data. Without realistic sensor data, the simulated run will be rejected or flagged as suspicious.

Based on reverse engineering, the app:
1. Registers an accelerometer sensor listener (`SensorManager.registerListener` with `Sensor.TYPE_ACCELEROMETER`)
2. Collects acceleration magnitude data at ~100ms intervals
3. Writes raw data to `/storage/emulated/0/sensor/<uuid>.txt`
4. On run completion, GZip-compresses and Base64-encodes the data
5. Uploads to server via `sensorZipFile` API endpoint

## What Changes
- Add new capability: Sensor Data Simulation
- Create a companion script to generate realistic accelerometer data based on GPS movement
- Write sensor data to the emulator's expected file location before user ends the run
- Data generation correlates with:
  - Simulated running speed (faster = higher magnitude)
  - Step frequency (periodic oscillation pattern)
  - Natural variation and noise

## Impact
- Affected specs: New capability `sensor-data-simulation`
- Affected code: New script `sensor_simulator.py` (can be called from `main.py` or run separately)
- Deployment method: ADB push files to `/storage/emulated/0/sensor/` on the emulator

## Non-Breaking
This change is additive and does not modify existing GPS simulation logic.
