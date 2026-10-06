How to run mine_raw_data.py:
  - Go to GitHub
  - Top Right Profile Picture --> Settings --> Developer Settings --> Personal Access Tokens --> Tokens (classic) --> Generate new token (classic)
  - Set expiration to personal preference, add note if you'd like, don't select any scopes
  - Generate token and copy immediately (only can see token once)
  - Open local repository (either on personal or school machine), open a terminal
  - Enter the following commands on terminal of choice:
    * Command Prompt: set GITHUB_TOKEN=<insert token here>}}
    * Powershell: $env:GITHUB_TOKEN="<insert token here>"
    * Mac/Linux: export GITHUB_TOKEN=<insert token here>
  - May have to run: pip install requests
  - Run: python mine_raw_data.py
    * Optional Args:
    * --start $\text{\color{gray}{<val>}}$: Starting timestamp, inclusive (default is "2021-01-01")
    * --end $\text{\color{gray}{<val>}}$: Ending timestamp, exclusive (default is "2026-01-01")
    * --out $\text{\color{gray}{<val>}}$: Name of output file, should end in .csv (default is "raw_data.csv")
    * --max-records $\text{\color{gray}{<int>}}$: stop after N rows (testing, doesn't stop by default)
