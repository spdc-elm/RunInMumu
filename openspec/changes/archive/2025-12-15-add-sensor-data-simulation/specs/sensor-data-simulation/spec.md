## ADDED Requirements

### Requirement: Accelerometer Data Generation
The system SHALL generate realistic accelerometer magnitude data that correlates with simulated running activity.

#### Scenario: Generate data based on run duration
- **WHEN** sensor simulation is triggered with a run duration in seconds
- **THEN** the system generates data points at 10 Hz sampling rate (100ms intervals)
- **AND** the total number of points equals `duration_seconds * 10`

#### Scenario: Correlate magnitude with running speed
- **WHEN** generating acceleration magnitude values
- **THEN** the system uses baseline gravity (~9.8 m/s²) plus walking oscillation
- **AND** oscillation amplitude scales with speed:
  - Slow pace (2.0 m/s): amplitude 15-30 m/s²
  - Medium pace (3.0 m/s): amplitude 25-45 m/s²
  - Fast pace (4.0+ m/s): amplitude 35-60 m/s²

#### Scenario: Simulate step frequency pattern
- **WHEN** generating walking oscillation component
- **THEN** the system applies periodic sine wave with frequency 2.5-3.0 Hz (150-180 steps/min)
- **AND** adds random phase shifts to simulate natural gait variation
- **AND** includes occasional amplitude spikes to simulate foot impacts

#### Scenario: Add realistic noise
- **WHEN** generating each data point
- **THEN** the system adds random Gaussian noise with standard deviation 2-5 m/s²
- **AND** ensures all values stay within physically plausible range (0-100 m/s²)

#### Scenario: Match statistical properties of real data
- **WHEN** analyzing generated sensor data
- **THEN** the mean value should fall in range 25-40 m/s²
- **AND** standard deviation should be 10-20 m/s²
- **AND** FFT analysis should show peak at step frequency (2.5-3.0 Hz)

### Requirement: Sensor Data File Creation
The system SHALL write sensor data in the format expected by the target application.

#### Scenario: Format data as JSON array
- **WHEN** writing sensor data to file
- **THEN** the system formats values as comma-separated floats
- **AND** wraps the array with square brackets: `[val1,val2,val3,...]`
- **AND** uses at most 6 decimal places for each float value

#### Scenario: Generate unique UUID filename
- **WHEN** creating a sensor data file
- **THEN** the system generates a UUID v4 identifier
- **AND** uses format `{uuid}.txt` for the filename

#### Scenario: Write to temporary local file
- **WHEN** generating sensor data
- **THEN** the system first writes to a local temporary file
- **AND** confirms successful write before attempting emulator transfer

### Requirement: Emulator File Transfer
The system SHALL transfer generated sensor data to the emulator's expected location.

#### Scenario: Push file via ADB
- **WHEN** transferring sensor data to emulator
- **THEN** the system executes `adb push <local_file> /storage/emulated/0/sensor/<uuid>.txt`
- **AND** uses the existing ADB connection from GPS simulation

#### Scenario: Verify file transfer success
- **WHEN** ADB push command completes
- **THEN** the system checks the command exit code
- **AND** displays error message if transfer failed
- **AND** confirms success with file path in emulator

#### Scenario: Create sensor directory if missing
- **WHEN** `/storage/emulated/0/sensor/` does not exist on emulator
- **THEN** the system creates the directory via `adb shell mkdir -p /storage/emulated/0/sensor`
- **AND** proceeds with file transfer

### Requirement: Integration with GPS Simulation
The system SHALL coordinate sensor data generation with GPS-based running simulation.

#### Scenario: Auto-detect run duration
- **WHEN** GPS simulation completes
- **THEN** the system captures the total elapsed time
- **AND** uses this value as the duration parameter for sensor data generation

#### Scenario: Generate sensor data before run end
- **WHEN** GPS simulation reaches distance limit
- **THEN** the system pauses and generates sensor data
- **AND** transfers data to emulator
- **AND** displays message: "Sensor data ready. You can now end the run in the app."

#### Scenario: Optional sensor simulation
- **WHEN** config option `generate_sensor_data` is false
- **THEN** the system skips sensor data generation entirely
- **AND** GPS simulation proceeds normally

#### Scenario: Standalone sensor generation mode
- **WHEN** `sensor_simulator.py` is run directly with `--duration` parameter
- **THEN** the system generates sensor data for specified duration
- **AND** transfers to emulator
- **AND** operates independently of GPS simulation

### Requirement: Configuration and Customization
The system SHALL support configuration of sensor data generation parameters.

#### Scenario: Configure step frequency range
- **WHEN** config specifies `step_frequency_range` (e.g., [2.5, 3.0] Hz)
- **THEN** the system generates oscillations within that frequency range

#### Scenario: Configure speed-amplitude mapping
- **WHEN** config specifies custom amplitude ranges per speed
- **THEN** the system uses those values instead of defaults

#### Scenario: Load reference data from real samples
- **WHEN** `use_reference_pattern` is enabled in config
- **THEN** the system loads a random file from `real_sensor/` directory
- **AND** analyzes its statistical properties
- **AND** generates new data matching those properties

## Non-Requirements
- The system does NOT simulate full 3-axis accelerometer data (x, y, z components)
- The system does NOT emulate sensor data in real-time during the run
- The system does NOT implement the GZip compression and Base64 encoding (handled by app)
- The system does NOT directly upload sensor data to the server (handled by app)
- The system does NOT validate or verify server-side acceptance of the data
