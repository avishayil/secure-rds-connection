#!/usr/bin/env bash

# Define the log file
LOG_FILE="script.log"

#echo "Connecting to the database..." >> "$LOG_FILE"
# Redirect both stdout and stderr to the log file
ssh -i $1 ec2-user@127.0.0.1 -p 9999

#echo "Script execution completed." >> "$LOG_FILE"
