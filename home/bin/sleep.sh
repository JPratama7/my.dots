#!/bin/bash
PID_FILE="/tmp/hypridle_inhibitor.pid"

if [ -f "$PID_FILE" ]; then
  echo "Stopping inhibitor..."
  kill $(cat "$PID_FILE") && rm "$PID_FILE"
else
  echo "Starting inhibitor..."
  systemd-inhibit --what=idle sleep infinity &
  echo $! > "$PID_FILE"
fi