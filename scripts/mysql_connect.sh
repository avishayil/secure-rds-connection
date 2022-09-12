#!/usr/bin/env bash

while getopts r:s: flag
do
    case "${flag}" in
        r) region=${OPTARG};;
        s) stack=${OPTARG};;
    esac
done

STACKNAME=$stack
REGION=$region

DBNAME="$(aws cloudformation describe-stacks --stack-name=$STACKNAME --region=$REGION | jq -r '.Stacks[].Outputs[0].OutputValue')"
USERNAME="$(aws cloudformation describe-stacks --stack-name=$STACKNAME --region=$REGION | jq -r '.Stacks[].Outputs[1].OutputValue')"
AURORAEP="$(aws cloudformation describe-stacks --stack-name=$STACKNAME --region=$REGION | jq -r '.Stacks[].Outputs[2].OutputValue')"

TOKEN="$(aws rds generate-db-auth-token --hostname=$AURORAEP --port 3306 --username=$USERNAME --region=$REGION)"

# set -x
mysql -h 127.0.0.1 -P 9999 --enable-cleartext-plugin --user=$USERNAME --password=$TOKEN
# set +x
