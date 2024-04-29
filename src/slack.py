import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import configparser

config = configparser.RawConfigParser()
configFilePath = r".config"
config.read(configFilePath)

# Set your Slack API token
slack_token = config.get("project", "SLACK")
client = WebClient(token=slack_token)

# Function to list all channels and their IDs
def list_channels():
	try:
		# Call the conversations.list method to retrieve a list of channels
		response = client.conversations_list()
		if response["ok"]:
			# Extract channel names and IDs from the response
			channels = response["channels"]
			for channel in channels:
				print(f"Channel Name: {channel['name']}, Channel ID: {channel['id']}")
		else:
			print("Failed to list channels:", response["error"])
	except SlackApiError as e:
		print(f"Error listing channels: {e.response['error']}")

# Function to list messages and their timestamps in a channel
def list_messages(channel_id):
	try:
		# Call the conversations.history method to retrieve channel history
		response = client.conversations_history(channel=channel_id)
		if response["ok"]:
			# Extract messages and their timestamps from the response
			messages = response["messages"]
			for message in messages:
				print(f"Message: {message['text']}, Timestamp: {message['ts']}")
		else:
			print("Failed to list messages:", response["error"])
	except SlackApiError as e:
		print(f"Error listing messages: {e.response['error']}")
		
# Function to list all teams in the workspace
def list_channels():
	try:
		# Call the teams_list method to retrieve information about all teams
		response = client.conversations_list()
		if response["ok"]:
			# Extract team information from the response
			print(response['channels'])
			return([{'name': channel['name']} for channel in response['channels']])
		else:
			print("Failed to list teams:", response["error"])
	except SlackApiError as e:
		print(f"Error listing teams: {e.response['error']}")

# Function to delete a message
def delete_message(channel_id, message_ts):
	try:
		# Call the chat_delete method to delete the message
		response = client.chat_delete(channel=channel_id, ts=message_ts)
		if response["ok"]:
			print("Message deleted successfully.")
		else:
			print("Failed to delete message:", response["error"])
	except SlackApiError as e:
		print(f"Error deleting message: {e.response['error']}")


# Function to fetch messages from a public group
def fetch_messages(channel_id):
	try:
		# Call the conversations.history method to retrieve message history
		response = client.conversations_history(channel=channel_id)
		if response["ok"]:
			# Extract messages from the response
			messages = response["messages"]
			for message in messages:
				print(message)
		else:
			print("Failed to fetch messages:", response["error"])
	except SlackApiError as e:
		print(f"Error fetching messages: {e.response['error']}")

# Function to list all teams in the workspace
def list_functions():
	# List all available functions in the client object
	functions_list = dir(client)

	# Print the list of functions
	for function_name in functions_list:
		print(function_name)

# Example usage
if __name__ == "__main__":
	# List all channels and their IDs
	for channel in list_channels():
		print(channel['name'])
	# List messages and their timestamps in a channel
	fetch_messages("C070WCSM6EP")