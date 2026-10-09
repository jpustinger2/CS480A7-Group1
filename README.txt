Replication Package contains: 
  - mine_raw_data.py (code to retrieve the data in Python)
  - filter_data.py (code to filter and clean the data in Python)
  - analyze_data.py (code to construct derived variables and the final dataset in Python)
  - official_raw_data.csv (raw data)
  - official_raw_comments.csv (raw data)
  - official_filtered_data.csv (intermediate filtering step, not required but included for context)
  - official_filtered_comments.csv (intermediate filtering step, not required but included for context)
  - official_analysis_dataset.csv (final analysis ready dataset)

How to run the data pipeline: Clone the repo first (either local or remote), then follow steps for each file
 mine_raw_data.py:
  - Go to GitHub
  - Top Right Profile Picture --> Settings --> Developer Settings (Bottom of menu options)
  - Personal Access Tokens --> Tokens (classic) --> Generate new token (classic)
  - Set expiration to personal preference, add note if you'd like, don't select any scopes
  - Generate token and copy immediately (only can see token once)
  - Open a terminal in local repository folder (either on personal or school machine)
  - Enter the following commands on terminal of choice:
    * Command Prompt: set GITHUB_TOKEN=<insert token here>
    * Powershell: $env:GITHUB_TOKEN="<insert token here>"
    * Mac/Linux: export GITHUB_TOKEN=<insert token here>
  - May have to run: pip install requests
  - Run in terminal: python mine_raw_data.py
    * Optional Args:
    * --start <val>: Starting timestamp, inclusive (default is "2021-01-01")
    * --end <val>: Ending timestamp, exclusive (default is "2026-01-01")
    * --out <val>: Name of output file, should end in .csv (default is "raw_data.csv")
    * --comments-out <val>: Name of comments output file, should end in .csv (default is "raw_comments.csv")
    * --max-records <int>: stop after N rows (testing, doesn't stop by default)
  - Program will fetch all PR's, issues and PR comments from the timespan using GitHub's REST API
    * PR's and Issues output to --start, and PR comments output to --out 
    * This program takes a while - if running on SSH, ensure that your PC's sleep timeout is set long enough
 filter_data.py:
  - Ensure mine_raw_data.py has ran correctly, and both output csv's are in the same directory as filter_data.py
  - Run in terminal: python filter_data.py
    * Optional Args:
    * --data <val>: Name of data input file, should end in .csv (default is "raw_data.csv")
    * --out <val>: Name of data output file, should end in .csv (default is "filtered_data.csv")
    * --comments <val>: Name of comments input file, should end in .csv (default is "raw_comments.csv")
    * --comments-out <val>: Name of comments output file, should end in .csv (default is "filtered_comments.csv")
  - Program will filter all PR's, issues and PR comments from --data and --comments by two criteria:
    * Each PR and Issue must have "area: Documentation" somewhere in the labels field. For PR comments, it's associated PR must contain the label
    * Each PR comment will be additionally filtered to remove those with "Bot" in the author_type field
  - Once filtered, the results will be written to --out and --comments-out
 analyze_data.py:
  - Ensure filter_data.py has ran correctly, and both output csv's are in the same directory as filter_data.py
  - Run in terminal: python analyze_data.py
    * Optional Args:
    * --data <val>: Name of data input file, should end in .csv (default is "filtered_data.csv")
    * --comments <val>: Name of comments input file, should end in .csv (default is "filtered_comments.csv")
    * --out <val>: Name of data output file, should end in .csv (default is "analysis_dataset.csv")
  - Program will combine both the data and comments file into one final analysis ready dataset
    * The dataset will have one record for each issue and PR in the --data file. 
    * All positive and negative reactions/buzzwords are summed up for analysis. For PRs, totals include associated PR comments
    * The dataset contains fields for: number, record_type, status, time_open, num_assignees, num_comments, total_reactions, and the fields mentioned above.
  - The final analysis ready dataset will be written to --out

Milestones
  - Artifacts Retrieved from Time Period (mine_data.py): 212,516 Records (16,354 Issues, 51,438 PR's, 144,724 PR Comments)
  - After Bot Comment Exclusions (filter_data.py): 190,685 Records (16,354 Issues, 51,438 PR's, 122,893 PR Comments), -21,831 from previous total
  - After Documentation Label Exclusions (filter_data.py): 15,274 Records (422 Issues, 3,318 PR's, 11,507 PR Comments), -175,411 from previous total
  - Final Record Count in Analysis Dataset (analyze_data.py): 3,740 Records (422 Issues, 3,318 PR's, data from PR comments condensed into PR variables), -11,507 from previous total
    
  
