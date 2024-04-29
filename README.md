# Group Insight
<p align="center">
  <img src="https://github.com/nweissberg/GroupInsight/blob/main/src/images/app.png" alt="GitHub Contribution Tracker" width="500px">
</p>

## Description
The Group Insight is a Python application that allows you to track the contributions of members in a GitHub organization over a specified time period. It provides a graphical interface to visualize the contribution activity of each member within the organization.

## How to Use
1. Install Python if not already installed. You can download Python from [here](https://www.python.org/downloads/).

2. Install project dependencies by running the following command:
```
pip install -r requirements.txt
```

3. Modify the .config file to set your GitHub organization, access token, and other settings.
```
[project]
organization = your_organization_github_id
token = your_github_api_token
slack = your_slack_api_key

[session]
start_date = 2024-04-01
end_date = 2024-04-28
```

4. Run the application:
- Windows: Double-click `init.bat`
- macOS/Linux: Double-click `init.command`

5. The application window will open, displaying contribution activity and leaderboards for the specified GitHub organization.

6. Use the date pickers to adjust the time period for tracking contributions.

7. Click on a member's name in the leaderboard to view their contribution activity.

8. Close the application window when finished.

## Dependencies
- Python 3
- tkinter
- tkcalendar
- Pillow
