# Configuration Management

## Purpose
Manage application configuration through a persistent JSON file with automatic defaults and caching.

## Requirements

### Requirement: Configuration File Loading
The system SHALL load configuration from `config.json` in the current working directory.

#### Scenario: Load existing valid configuration
- **WHEN** `config.json` exists and contains valid JSON
- **THEN** the system parses the file content
- **AND** returns the configuration as a dictionary

#### Scenario: Handle missing configuration file
- **WHEN** `config.json` does not exist
- **THEN** the system returns an empty dictionary
- **AND** continues execution without error

#### Scenario: Handle invalid JSON format
- **WHEN** `config.json` contains malformed JSON
- **THEN** the system exits with an error message displaying the JSON parse error

### Requirement: Configuration File Saving
The system SHALL persist configuration changes to `config.json`.

#### Scenario: Save configuration dictionary
- **WHEN** saving configuration
- **THEN** the system writes JSON with 4-space indentation
- **AND** uses UTF-8 encoding
- **AND** preserves Unicode characters (ensure_ascii=False)

### Requirement: Path Resolution
The system SHALL resolve configured paths to absolute paths.

#### Scenario: Resolve absolute path
- **WHEN** a configuration value contains an absolute path
- **THEN** the system returns the path as-is after expansion

#### Scenario: Resolve relative path
- **WHEN** a configuration value contains a relative path
- **THEN** the system resolves it relative to `config.json` directory

#### Scenario: Expand user home directory
- **WHEN** a path contains `~` or `~/`
- **THEN** the system expands it to the user's home directory
- **AND** then applies absolute/relative resolution

### Requirement: Configuration Schema
The system SHALL support the following configuration keys.

#### Scenario: Emulator directory configuration
- **WHEN** `emu_dir` key is present
- **THEN** it specifies the path to MuMu emulator installation directory
- **AND** the path should contain `MuMuManager.exe` or `../MuMuManager.exe`

#### Scenario: Walk path inline configuration
- **WHEN** `walk_path` key is present
- **THEN** it contains an array of [latitude, longitude] coordinate pairs
- **AND** each coordinate must be a valid floating-point number

#### Scenario: Walk path file configuration
- **WHEN** `walk_path_file` key is present
- **THEN** it specifies the path to a route file (.gpx, .json, or .py)
- **AND** the path is resolved relative to config.json directory

#### Scenario: Location offset configuration
- **WHEN** `location_offset` key is present
- **THEN** it contains an object with `lat` and `lon` numeric values
- **AND** these values are added as degree offsets to all GPS coordinates

#### Scenario: Missing required configuration
- **WHEN** neither `walk_path` nor `walk_path_file` is configured
- **THEN** the system attempts to use `run.gpx` as default
- **AND** if found, saves `walk_path_file: "run.gpx"` to config

### Requirement: Automatic Caching
The system SHALL automatically cache discovered values to avoid repeated searches.

#### Scenario: Cache emulator directory
- **WHEN** the system discovers MuMu installation via disk search
- **THEN** it saves the `emu_dir` to `config.json`
- **AND** displays a confirmation message

#### Scenario: Cache default GPX file
- **WHEN** the system uses `run.gpx` as default fallback
- **THEN** it saves `walk_path_file: "run.gpx"` to `config.json`

## Configuration Example

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

## Non-Requirements
- The system does NOT validate configuration values beyond type checking
- The system does NOT support environment variable expansion in paths
- The system does NOT provide a UI for editing configuration
- The system does NOT migrate or upgrade old configuration formats
