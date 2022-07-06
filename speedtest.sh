#!/bin/bash

OUTPUT_FILE="/usr/src/speedtest/speedMeasure.txt"

while true; do
  date >> "$OUTPUT_FILE"
  speedtest-cli --simple >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  sleep 1800
done
