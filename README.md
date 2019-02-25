# Passwd-Parser
The following python script correlates data between user and groups of a linux system

- Supported user file format `<name>:<x>:<user_id>:<group_id>:<description>`
- Supported group file format `<name>:<x>:<group_id>:<users>`
- The program prints correlated data as json object to stdout
- The program maintains an error.log file in the same directory

Setup Requirements (on Ubuntu 18.04):
- Python 2.7 `sudo apt intsall python-minimal`

Usage:
- Run help `python passwd-parser.py --help`
- Run with default file paths (/etc/passwd & /etc/group) `python passwd-parser.py`
- Run with default passwd file and specific group file `python passwd-parser.py -g <path_to_group_file>`
- Run with default group file and specific passwd file `python passwd-parser.py -p <path_to_passwd_file>`
- Run with specific group and passwd files `python passwd-parser.py -p <path_to_passwd_file> -g <path_to_group_file>`
- Cron Job (Runs every 15 min)
    - `*/15 * * * * <path_to_python_bin> <path_to_script>/passwd-parser.py > <output_file_path>.json 2>&1`
- Example
    - `DATEVAR=date +%Y-%m-%d_%H:%M:%S`
    - `*/15 * * * * /usr/bin/python /home/ubuntu/passwd-parser/passwd-parser.py > /home/ubuntu/passwd-parser/$($DATEVAR).json 2>&1`
    