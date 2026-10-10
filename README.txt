Replication Package contains: 
  - mine_raw_data.py (code to retrieve the data in Python)
  - filter_data.py (code to filter and clean the data in Python)
  - analyze_data.py (code to construct derived variables and the final dataset in Python)
  - official_raw_data.csv (raw data)
  - official_raw_comments.csv (raw data)
  - official_filtered_data.csv (intermediate filtering step, not required but included for context)
  - official_filtered_comments.csv (intermediate filtering step, not required but included for context)
  - official_analysis_dataset.csv (final analysis ready dataset)

Data collected on: October 9, 2026 (final mining run). Re-running later may give slightly different results.

Note: the scripts' default output names (raw_data.csv, etc.) match the submitted files without the "official_" prefix.

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
    * PR's and Issues output to --out, and PR comments output to --comments-out 
    * Only PR conversation comments are collected (not inline code-review comments, and no comments on issues)
    * The observation period (--start/--end) is applied here, while retrieving
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
    * Each PR and Issue must have "area: Documentation" somewhere in the labels field. For PR comments, its associated PR must contain the label
    * Each PR comment will be additionally filtered to remove those with "Bot" in the author_type field
    * Bot handling: bot-authored comments are removed. Bot-authored issues and PR's themselves are retained, because the PR variables also draw on human comments.
  - Once filtered, the results will be written to --out and --comments-out
 analyze_data.py:
  - Ensure filter_data.py has ran correctly, and both output csv's are in the same directory as analyze_data.py
  - Run in terminal: python analyze_data.py
    * Optional Args:
    * --data <val>: Name of data input file, should end in .csv (default is "filtered_data.csv")
    * --comments <val>: Name of comments input file, should end in .csv (default is "filtered_comments.csv")
    * --out <val>: Name of data output file, should end in .csv (default is "analysis_dataset.csv")
  - Program will combine both the data and comments file into one final analysis ready dataset
    * The dataset will have one record for each issue and PR in the --data file. 
    * All positive and negative reactions/buzzwords are summed up for analysis. For PRs, totals include associated PR comments
    * Reaction definitions: positive = +1, laugh, hooray, heart, rocket; negative = -1, confused, eyes. Total reactions is the sum of all reaction types.
    * Buzzword definitions: the positive and negative keyword lists are defined at the top of analyze_data.py. Matches are whole-phrase and case-insensitive, counted in the title and body (and in the comment text for PR's).
    * time_open is the time from creation to closure (or to merge for merged PR's), written as days, hours, minutes and seconds (e.g. 2d 5h 4m 30s); it is empty for records still open
    * num_comments is the GitHub comment count for issues, and the number of non-bot conversation comments for PR's
    * The dataset contains these fields: number, record_type, status, time_open, num_assignees, num_comments, total_reactions, positive_reactions, negative_reactions, positive_buzzwords, negative_buzzwords
  - The final analysis ready dataset will be written to --out

Milestones
  - Artifacts Retrieved from Time Period (mine_raw_data.py): 212,516 Records (16,354 Issues, 51,438 PR's, 144,724 PR Comments)
  -  After observation-period filter (applied during retrieval by --start/--end, so no records are removed afterward): 212,516 Records (16,354 Issues, 51,438 PR's, 144,724 PR Comments)
  - After exclusions (filter_data.py):
     * After Bot Comment Exclusions: 190,685 Records (16,354 Issues, 51,438 PR's, 122,893 PR Comments), -21,831 from previous total
     * After Documentation Label Exclusions: 15,247 Records (422 Issues, 3,318 PR's, 11,507 PR Comments), -175,438 from previous total
  - Final Observations (analyze_data.py): 3,740 Records (422 Issues, 3,318 PR's, data from PR comments condensed into PR variables), -11,507 from previous total
    
