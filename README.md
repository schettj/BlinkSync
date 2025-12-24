# BlinkSync
Sync local videos in syncmodule to a local directory using blinkpy

## Dependencies
Blinkpy https://github.com/fronzbot/blinkpy

## Usage
python3 blink.py *Sync_Module_Name* *Path_to_save_files_locally*

## Sugggested usaged
Set up a crontab job to run hourly, will pull and delete all new files and save to specified directory
Set up a crontab job to run daily, delete files in that directory older than however many days you wish to retain
