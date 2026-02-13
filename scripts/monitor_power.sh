#!/bin/bash
set -euo pipefail

# monitor_power.sh
#
# This script monitors the CPU/Package power draw using Intel RAPL
# and logs the instantaneous wattage along with a timestamp to a specified file.
# It's designed to be run periodically (e.g., via crontab) to collect historical data.
# The collected data can then be analyzed by a separate application (e.g., a Python script).
#
# Usage: sudo ./monitor_power.sh
# Requires:
# - Intel CPU with RAPL support
# - `intel_rapl_msr` kernel module loaded (often done automatically)
# - `bc` for floating-point arithmetic
# - Read permissions for /sys/class/powercap/intel-rapl:0/energy_uj
#
# Configuration:
# - ENERGY_FILE: Path to the Intel RAPL energy counter.
# - POWER_LOG_FILE: Path where power data will be logged.

# Configuration variables
ENERGY_FILE="/sys/class/powercap/intel-rapl:0/energy_uj"
POWER_LOG_FILE="/mnt/Data/scripts/power_monitor/logs/power_monitor.log" # Log file for power data
GPU_SMI_AVAILABLE=false # Global flag to track if nvidia-smi is available

# Functions

# check_prerequisites
# Description: Verifies that the RAPL energy file exists and is readable.
#              Checks for nvidia-smi availability.
#              Exits with an error message if RAPL prerequisites are not met.
# Arguments: None
# Returns: 0 on success, exits on RAPL failure. Sets GPU_SMI_AVAILABLE global flag.
check_prerequisites() {
    if [ ! -f "$ENERGY_FILE" ]; then
        echo "Error: RAPL energy file not found at $ENERGY_FILE." >&2
        echo "Please ensure Intel RAPL is enabled. You might need to run: sudo modprobe intel_rapl_msr" >&2
        exit 1
    fi

    if [ ! -r "$ENERGY_FILE" ]; then
        echo "Error: Permission denied to read $ENERGY_FILE." >&2
        echo "Please run the script with sufficient privileges (e.g., sudo): sudo ./monitor_power.sh" >&2
        exit 1
    fi

    if command -v nvidia-smi &> /dev/null; then
        GPU_SMI_AVAILABLE=true
    else
        echo "Warning: nvidia-smi command not found. GPU power data will not be collected." >&2
        GPU_SMI_AVAILABLE=false
    fi
}

# setup_logging
# Description: Ensures the log directory specified by POWER_LOG_FILE exists.
#              If the log file is new or empty, it writes a header line to it.
# Arguments: None
# Returns: 0 on success, exits on failure to create directory.
setup_logging() {
    local log_dir
    log_dir="$(dirname "$POWER_LOG_FILE")"
    mkdir -p "$log_dir" || { echo "Error: Could not create log directory $log_dir" >&2; exit 1; }

    if [ ! -s "$POWER_LOG_FILE" ]; then
        echo "Timestamp,CPU_Watts,GPU_Watts" > "$POWER_LOG_FILE"
    fi
}

# get_current_watts
# Description: Reads the Intel RAPL energy counter twice, with a 1-second delay,
#              to calculate the instantaneous power draw in Watts.
# Arguments: None
# Returns: The calculated wattage (float) echoed to stdout.
get_current_watts() {
    local E0 E1 WATTS
    E0=$(cat "$ENERGY_FILE")
    sleep 1
    E1=$(cat "$ENERGY_FILE")

    # Calculate Watts: (difference in microjoules / 1,000,000)
    WATTS=$(echo "scale=2; ($E1 - $E0) / 1000000" | bc)
    echo "$WATTS"
}

# log_watts_data
# Description: Appends the given CPU wattage and GPU wattage along with a timestamp to the
#              POWER_LOG_FILE.
# Arguments:
#   $1 - The CPU wattage value to log.
#   $2 - The GPU wattage value to log.
# Returns: None
log_watts_data() {
    local cpu_watts_val="$1"
    local gpu_watts_val="$2"
    local TIMESTAMP
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${TIMESTAMP},${cpu_watts_val},${gpu_watts_val}" >> "$POWER_LOG_FILE"
}

# get_gpu_watts
# Description: Queries nvidia-smi for the current GPU power draw.
#              Returns 0 if nvidia-smi is not available or fails to get data.
# Arguments: None
# Returns: The calculated GPU wattage (float) echoed to stdout, or 0.
get_gpu_watts() {
    if "$GPU_SMI_AVAILABLE"; then
        # Query power.draw for all GPUs, take the first one (assuming single GPU for laptop)
        local gpu_watts
        gpu_watts=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | head -n 1)
        if [[ -z "$gpu_watts" ]]; then
            echo "0.00" # Return 0 if nvidia-smi failed to output power
        else
            echo "$gpu_watts"
        fi
    else
        echo "0.00" # GPU_SMI_AVAILABLE is false
    fi
}

# main
# Description: Orchestrates the script's execution flow.
# Arguments: None
# Returns: None
main() {
    check_prerequisites
    setup_logging
    
    local current_cpu_watts
    current_cpu_watts=$(get_current_watts)

    local current_gpu_watts
    current_gpu_watts=$(get_gpu_watts)
    
    log_watts_data "$current_cpu_watts" "$current_gpu_watts"
    
    echo "Current CPU/Package Draw: ${current_cpu_watts}W | Current GPU Draw: ${current_gpu_watts}W"
}

main "$@"
