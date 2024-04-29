import requests

# Set up your Jira credentials and URL
JIRA_URL = 'YOUR_JIRA_URL'
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'

# Construct the API endpoint to fetch issues from a board
board_id = 'YOUR_BOARD_ID'
api_url = f'{JIRA_URL}/rest/agile/1.0/board/{board_id}/issue'

# Set up authentication
auth = (USERNAME, PASSWORD)

# Send a GET request to fetch issues
response = requests.get(api_url, auth=auth)

# Check if the request was successful
if response.status_code == 200:
    # Extract issue data from the response
    issues = response.json().get('issues', [])
    
    # Process the issues
    for issue in issues:
        # Extract relevant information from the issue JSON
        issue_key = issue['key']
        summary = issue['fields']['summary']
        status = issue['fields']['status']['name']
        
        # Print the extracted information
        print(f"Issue Key: {issue_key}, Summary: {summary}, Status: {status}")
else:
    print(f"Failed to fetch issues. Status code: {response.status_code}")
