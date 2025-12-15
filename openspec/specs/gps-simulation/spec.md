# GPS Simulation

## Purpose
Simulate GPS movement along a predefined route in the MuMu Android Emulator to automate fitness/running activities.

## Requirements

### Requirement: Emulator Detection and Connection
The system SHALL automatically locate and connect to the MuMu Android Emulator.

#### Scenario: Auto-discover emulator installation
- **WHEN** the emulator directory is not configured
- **THEN** the system searches all available drives for `MuMuManager.exe`
- **AND** saves the discovered path to `config.json` for future use

#### Scenario: Use cached emulator path
- **WHEN** a valid `emu_dir` exists in `config.json`
- **THEN** the system loads the path directly without searching
- **AND** displays a confirmation message

#### Scenario: Connect to running emulator
- **WHEN** the emulator is running
- **THEN** the system retrieves ADB connection info via `MuMuManager.exe info -v 0`
- **AND** connects to the emulator using the `adb connect` command
- **AND** confirms successful connection

#### Scenario: Handle emulator not running
- **WHEN** the emulator is not running or ADB info retrieval fails
- **THEN** the system exits with an error message instructing the user to start the emulator

### Requirement: Route Loading
The system SHALL support loading GPS routes from multiple file formats.

#### Scenario: Load route from GPX file
- **WHEN** `walk_path_file` points to a `.gpx` file
- **THEN** the system parses the GPX XML structure
- **AND** extracts waypoints (longitude, latitude) from `<wpt>` tags
- **AND** removes duplicate consecutive points within tolerance (1e-6 degrees)
- **AND** displays the number of loaded waypoints

#### Scenario: Load route from JSON file
- **WHEN** `walk_path_file` points to a `.json` file
- **THEN** the system parses the JSON array of coordinate pairs
- **AND** converts each pair to (latitude, longitude) tuple

#### Scenario: Load route from Python file
- **WHEN** `walk_path_file` points to a `.py` file
- **THEN** the system executes the Python file
- **AND** extracts the `WALK_PATH` variable containing coordinate list

#### Scenario: Load route from inline config
- **WHEN** `walk_path` array exists in `config.json`
- **THEN** the system uses the inline coordinate list directly

#### Scenario: Fallback to default GPX file
- **WHEN** no path configuration exists and `run.gpx` file is present
- **THEN** the system automatically sets `walk_path_file` to `run.gpx`
- **AND** saves this setting to `config.json`

#### Scenario: Handle missing route configuration
- **WHEN** no valid route source is configured or found
- **THEN** the system exits with an error message requesting path configuration

### Requirement: GPS Movement Simulation
The system SHALL simulate realistic GPS movement with configurable parameters.

#### Scenario: Initialize starting position
- **WHEN** simulation begins
- **THEN** the system sets the emulator location to the first waypoint
- **AND** applies configured location offset
- **AND** adds random jitter within `JITTER_RADIUS_M` (default 2.0m)

#### Scenario: Interpolate position along route
- **WHEN** each tick interval (default 0.40s) elapses
- **THEN** the system calculates distance traveled based on current speed
- **AND** interpolates position between current and next waypoint
- **AND** wraps around to start when reaching the end of route

#### Scenario: Apply speed variation
- **WHEN** calculating movement distance
- **THEN** the system applies base speed `BASE_SPEED_MPS` (default 2.8 m/s)
- **AND** adds random variation within `SPEED_JITTER_RATIO` range (default ±20%)

#### Scenario: Apply position jitter
- **WHEN** setting location on emulator
- **THEN** the system adds random offset within `JITTER_RADIUS_M` in both X and Y directions
- **AND** converts meter offsets to degree adjustments based on latitude

#### Scenario: Apply location offset
- **WHEN** `location_offset` is configured in `config.json`
- **THEN** the system adds the configured lat/lon delta to all positions before setting location

#### Scenario: Display real-time progress
- **WHEN** simulation is running
- **THEN** the system clears the console and displays a table with:
  - Elapsed time (seconds)
  - Instantaneous speed (m/s)
  - Total distance traveled (meters)
  - Average speed (m/s)
  - GPS update frequency (Hz)

#### Scenario: Reach distance limit
- **WHEN** total distance exceeds `DIST_LIMIT_M` (default 3200m)
- **THEN** the system stops simulation
- **AND** displays completion message

### Requirement: Location Setting via MuMuManager
The system SHALL set GPS coordinates using the MuMu emulator's command-line interface.

#### Scenario: Execute location command
- **WHEN** setting a new GPS position
- **THEN** the system executes `MuMuManager.exe control -v 0 tool location -lon <lon> -lat <lat>`
- **AND** suppresses stdout and stderr output

### Requirement: User Interaction Flow
The system SHALL require minimal user interaction while providing clear status feedback.

#### Scenario: Manual UI preparation
- **WHEN** the system is ready to start simulation
- **THEN** it displays a message instructing the user to manually navigate to the running app
- **AND** waits for user to press Enter before starting GPS simulation

#### Scenario: Handle user interruption
- **WHEN** the user presses Ctrl+C during execution
- **THEN** the system catches the KeyboardInterrupt
- **AND** displays a friendly exit message
- **AND** waits for Enter before closing

#### Scenario: Handle unexpected errors
- **WHEN** an unhandled exception occurs
- **THEN** the system displays the error message
- **AND** waits for Enter before closing

### Requirement: Coordinate System Conversion
The system SHALL accurately convert between geographic coordinates and metric distances.

#### Scenario: Calculate geographic distance
- **WHEN** measuring distance between two waypoints
- **THEN** the system calculates Euclidean distance in degrees
- **AND** multiplies by 111,320 meters per degree

#### Scenario: Convert meter offset to degree offset
- **WHEN** applying jitter in meters
- **THEN** the system converts latitude offset as `dy / 111320`
- **AND** converts longitude offset as `dx / (111320 * cos(latitude_radians))`

## Non-Requirements
- The system does NOT automate UI interactions (clicking buttons, navigating screens)
- The system does NOT support emulators other than NetEase MuMu
- The system does NOT validate whether the simulated route is within allowed running zones
- The system does NOT handle multi-instance emulator setups
