# Project Context

## Purpose
This project is a Python script designed to automate participation in a running/fitness activity within the MuMu Android Emulator. It simulates GPS movement along a predefined path and interacts with the user interface of a specific mobile application to start, monitor, and complete the activity.

## Tech Stack
- **Language:** Python 3
- **Core Libraries:**
  - **PrettyTable:** For displaying formatted, tabular data in the console during operation.
- **External Tools:**
  - **MuMuManager.exe:** Command-line tool for controlling the MuMu emulator (location setting).
  - **adb.exe:** Android Debug Bridge for connecting to the emulator.

## Project Conventions

### Code Style
- **Naming:** Functions and variables use `snake_case`. Constants are in `UPPER_SNAKE_CASE`.
- **Typing:** The code uses type hints (e.g., `List`, `Tuple`, `Path`) for clarity.
- **Formatting:** F-strings are standard for string formatting. The code includes comments, some of which are in Chinese and contain emojis.
- **Console Output:** ANSI escape codes are used to produce colored text in the terminal for better readability.

### Architecture Patterns
- **Structure:** The script is procedural, organized into a sequence of functions representing different phases:
  1.  `find_emu_dir`: Locates the MuMu Emulator installation directory.
  2.  `connect_to_emulator`: Connects to the already-running emulator via ADB.
  3.  `simulate_walk`: Simulates GPS movement along a predefined path and provides real-time progress feedback.
- **Configuration:** Key parameters like the walking path, speed, and distance limit are defined as constants at the top of the file. The emulator path is cached in `config.json` for faster subsequent runs.
- **Interaction:** The script interfaces with the emulator via the `MuMuManager.exe` command-line tool to set GPS coordinates. No UI automation is performed; users manually navigate to the appropriate screen before running the script.

### Testing Strategy
- There is currently no automated testing suite (e.g., unit tests, integration tests) defined for this project. Verification is done by observing the script's execution and its effects in the emulator.

### Git Workflow
- **Branching Strategy:** Direct commits to `main` branch for small projects. For larger changes, create feature branches with descriptive names (e.g., `feature/add-auto-pause`, `fix/location-accuracy`).
- **Commit Messages:** Write clear, concise commit messages in present tense. Examples: "Update README.md", "Add GPS simulation logic", "Fix emulator connection error".
- **Commit Frequency:** Commit logical units of work. Each commit should represent a complete, working change when possible.
- **Pull Requests:** Not required for solo development. For collaborative work, use pull requests for code review before merging to `main`.

## Domain Context
- The script automates fitness/running applications on the MuMu Android emulator by simulating GPS movement.
- It simulates a user physically moving by feeding a series of GPS coordinates to the emulator's location service at regular intervals.
- Users manually navigate to the running interface before starting the script, eliminating the need for UI automation.

## Important Constraints
- **Emulator Dependency:** The script is tightly coupled to the NetEase MuMu Emulator and its specific CLI tools (`MuMuManager.exe`, `adb.exe`). It will not work with other emulators without modification.
- **Manual UI Navigation:** Users must manually navigate to the running screen in their app before starting the script.
- **Platform:** The script is designed to run on Windows, as evidenced by the search paths for the emulator and use of Windows-specific commands.

## External Dependencies
- **NetEase MuMu Emulator:** The Android emulator environment where the target application runs.
- **Target Android Applications:** Any fitness or running application that uses GPS location data from the Android system.
