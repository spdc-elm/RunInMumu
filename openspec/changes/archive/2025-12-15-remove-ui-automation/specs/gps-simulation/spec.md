# GPS Simulation Specification

## ADDED Requirements

### Requirement: Manual App Preparation
The script SHALL allow users to manually navigate to the running interface in their app before starting GPS simulation.

#### Scenario: User prepares app manually
- **WHEN** the script starts
- **THEN** it SHALL display a message instructing the user to prepare the app
- **AND** it SHALL wait for user confirmation (Enter key press) before starting simulation

### Requirement: MuMu 12 Support
The script SHALL support both legacy MuMu emulator and MuMu 12 directory structures.

#### Scenario: MuMu 12 directory detected
- **WHEN** the emulator path points to an `nx_main` subdirectory
- **THEN** the script SHALL correctly locate `MuMuManager.exe` in the parent directory
- **AND** it SHALL use the appropriate command-line parameters for MuMu 12

### Requirement: User-Friendly Error Messages
The script SHALL provide clear, actionable error messages when issues occur.

#### Scenario: Emulator not found
- **WHEN** the emulator cannot be located
- **THEN** the script SHALL display a message indicating the emulator was not found
- **AND** it SHALL suggest checking the installation or manually specifying the path in config.json

#### Scenario: Connection failure
- **WHEN** connection to the emulator fails
- **THEN** the script SHALL display a message indicating the connection failed
- **AND** it SHALL suggest ensuring the emulator is fully started

## REMOVED Requirements

### Requirement: Automated UI Navigation
**Reason**: UI automation using OpenCV template matching is fragile and requires maintaining image templates for each app version. Manual navigation is more reliable and flexible.

**Migration**: Users should manually open their app and navigate to the running screen before starting the script. The script will display a prompt to wait for user readiness.

### Requirement: Automated App Launch
**Reason**: Launching specific apps (WeChat, WeWork) automatically is not necessary when users can launch their preferred app manually.

**Migration**: Users should manually start their MuMu emulator and open their fitness app before running the script.

### Requirement: Image Template Matching
**Reason**: OpenCV dependency and image template maintenance removed as part of UI automation removal.

**Migration**: No longer applicable. Image files in `img/` directory are no longer used by the script.

## MODIFIED Requirements

### Requirement: Emulator Path Detection
The script SHALL automatically detect the MuMu emulator installation directory by first checking `config.json`, then searching common installation paths, supporting both legacy MuMu and MuMu 12 installations.

#### Scenario: Config file exists with valid path
- **WHEN** `config.json` exists and contains a valid `emu_dir` path
- **THEN** the script SHALL use that path
- **AND** it SHALL verify `MuMuManager.exe` exists (either in the directory or parent directory for MuMu 12)

#### Scenario: Config file missing or invalid
- **WHEN** `config.json` does not exist or contains an invalid path
- **THEN** the script SHALL search all drive letters for MuMu installation
- **AND** upon finding it, SHALL save the path to `config.json` for future use

#### Scenario: MuMu 12 nx_main structure
- **WHEN** the config path points to an `nx_main` subdirectory
- **THEN** the script SHALL look for `MuMuManager.exe` in the parent directory
- **AND** it SHALL successfully connect to the emulator

### Requirement: GPS Location Simulation
The script SHALL simulate GPS movement along a predefined path by sending location updates to the MuMu emulator at regular intervals with randomized jitter to simulate realistic movement.

#### Scenario: Simulate walking along route
- **WHEN** the script starts simulation
- **THEN** it SHALL send GPS coordinates to the emulator every TICK_INTERVAL_SEC seconds
- **AND** each coordinate SHALL include random jitter within JITTER_RADIUS_M meters
- **AND** speed SHALL vary by ±SPEED_JITTER_RATIO to simulate natural walking

#### Scenario: Display real-time progress
- **WHEN** simulation is running
- **THEN** the script SHALL display a table showing elapsed time, current speed, total distance, average speed, and update frequency
- **AND** the display SHALL refresh after each location update

#### Scenario: Complete at distance threshold
- **WHEN** total simulated distance reaches DIST_LIMIT_M
- **THEN** the script SHALL stop simulation
- **AND** display a completion message
