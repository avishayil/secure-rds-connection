
@ECHO OFF
REM Define the log file
set LOG_FILE="script.log"

echo "Connecting to the EC2 instance..." >> %LOG_FILE%
REM Redirect both stdout and stderr to the log file
REM add support for private key parameter
REM provide the -i with <private key path>
@ECHO ON
ssh -i %1 -p 9999 ec2-user@127.0.0.1

@ECHO OFF
echo "Script execution completed." >> %LOG_FILE%