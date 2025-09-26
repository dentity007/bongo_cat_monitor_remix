# Hardware Monitoring Libraries

This directory contains libraries required for advanced hardware monitoring features.

## LibreHardwareMonitorLib.dll

**Required for:** CPU and GPU temperature monitoring on Windows

### How to Obtain:

1. Download LibreHardwareMonitor from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
2. Build the project or download the latest release
3. Copy `LibreHardwareMonitorLib.dll` from the build output to this directory
4. Ensure the DLL is compatible with .NET Framework 4.7.2 or later

### Alternative Sources:
- NuGet package: `LibreHardwareMonitorLib`
- Pre-built binaries from the releases page

### Notes:
- This DLL enables real-time CPU and GPU temperature monitoring
- Requires administrative privileges for CPU temperature access
- Only used when hardware monitoring is enabled in settings

## Credits:
Hardware monitoring integration by chriss158 (edschbert@gmail.com)