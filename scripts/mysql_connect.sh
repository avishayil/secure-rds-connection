#!/usr/bin/env bash

# Define the log file
LOG_FILE="script.log"

while getopts r:s: flag
do
    case "${flag}" in
        r) region=${OPTARG};;
        s) stack=${OPTARG};;
    esac
done

STACKNAME=$stack
REGION=$region

echo "Fetching database information..." >> "$LOG_FILE"
STACK_OUTPUTS="$(aws cloudformation describe-stacks --stack-name=$STACKNAME --region=$REGION)"

DBNAME="$(echo "$STACK_OUTPUTS" | jq -r '.Stacks[].Outputs[] | select(.OutputKey | contains("DBConstructAuroraDatabaseName")) | .OutputValue')"
USERNAME="$(echo "$STACK_OUTPUTS" | jq -r '.Stacks[].Outputs[] | select(.OutputKey | contains("DBConstructAuroraRDSUserName")) | .OutputValue')"
AURORAEP="$(echo "$STACK_OUTPUTS" | jq -r '.Stacks[].Outputs[] | select(.OutputKey | contains("DBConstructAuroraClusterEndpoint")) | .OutputValue')"

echo "Generating authentication token..." >> "$LOG_FILE"
TOKEN="$(aws rds generate-db-auth-token --hostname=$AURORAEP --port 3306 --username=$USERNAME --region=$REGION)"

echo "Connecting to the database..." >> "$LOG_FILE"
# Redirect both stdout and stderr to the log file
mysql -h 127.0.0.1 -P 9999 --enable-cleartext-plugin --user=$USERNAME --password=$TOKEN

echo "Script execution completed." >> "$LOG_FILE"
