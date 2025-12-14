# Change: Remove UI Automation and Simplify to GPS-Only Simulation

## Why
The original script included automated UI interaction using OpenCV for image recognition to automatically launch apps and navigate through fitness app interfaces. This approach is fragile, requires maintaining image templates, and adds unnecessary complexity. Users prefer to manually navigate to the running interface and then start the GPS simulation, which is more reliable and flexible across different apps.

## What Changes
- Remove all UI automation functionality (`click_icon`, `pre_run_ui`, `post_run_ui`, `launch_emulator`)
- Remove OpenCV and NumPy dependencies
- Simplify script to focus solely on GPS location simulation
- Add user prompt to manually prepare the app before starting simulation
- Improve emulator path detection to support MuMu 12 directory structure
- Add better error handling and user-friendly console output

## Impact
- Affected specs: `gps-simulation`
- Affected code: `main.py` (major refactoring)
- Removed files: Image templates in `img/` directory are no longer used by the script
- Dependencies: `cv2` (OpenCV) and `numpy` can be uninstalled
