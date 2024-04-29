import requests

import json
from pathlib import Path

collection = Path("data")


def get_contributions(token, username, since_date, until_date):
    headers = {
        "Authorization": f"bearer {token}",
    }
    body = {
        "query": f"""
            query {{
                user(login: "{username}") {{
                    name
                    contributionsCollection {{
                        contributionCalendar {{
                            totalContributions
                            weeks {{
                                contributionDays {{
                                    contributionCount
                                    date
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        """
    }

    response = requests.post(
        "https://api.github.com/graphql", json=body, headers=headers
    )
    data = response.json()
    # print(data)
    return data


def get_organization_members(token, organization):
    print(f"get members from {organization}")
    headers = {
        "Authorization": f"bearer {token}",
    }
    body = {
        "query": f"""
            query {{
                organization(login: "{organization}") {{
                    membersWithRole(first: 100) {{
                        totalCount
                        edges {{
                            node {{
                                login
                                name
                                email
                            }}
                            role
                        }}
                    }}
                }}
            }}
        """
    }

    response = requests.post(
        "https://api.github.com/graphql", json=body, headers=headers
    )
    data = response.json()
    return [
        {
            "login": member["node"]["login"],
            "name": member["node"]["name"],
            "role": member["role"],
            "email": member["node"]["email"],
            "contributions": None,
        }
        for member in data["data"]["organization"]["membersWithRole"]["edges"]
    ]


def on_callback(data):
    # print(data)
    return data


def update_leaderboard(token, git_data, period, fetch_from_cloud=True):
    for user in git_data["team"]:
        if fetch_from_cloud:
            print(
                f'get {user["role"] or "USER"}\t{user["name"] or user["login"]} ({user["email"] or user["login"]})'
            )
            contributions = get_contributions(
                token, user["login"], period[0], period[1]
            )
            contributions_calendar = contributions["data"]["user"][
                "contributionsCollection"
            ]["contributionCalendar"]

            user["contributions"] = contributions_calendar
        # owned_contributions = [repo['defaultBranchRef']['target']['history']['totalCount'] if repo['defaultBranchRef'] else 0 for repo in contributions_data['data']['user']['repositories']['nodes']]
        # Initialize period sum for the user
        user["periodSum"] = 0

        # Iterate over contribution days and add to periodSum if date falls within the specified period
        for week in user["contributions"]["weeks"]:
            for day in week["contributionDays"]:
                if period[0] <= day["date"] < period[1]:
                    user["periodSum"] += day["contributionCount"]

        # user['periodSum'] -= sum(owned_contributions)
        # if user['periodSum'] < 0: user['periodSum']=0
    # Sort users by totalContributions (descending order)
    git_data["leader_board"] = sorted(
        git_data["team"], key=lambda x: x["periodSum"], reverse=True
    )
    return git_data


def get_organization_data(
    period, organization, token, log=False, on_local_store=on_callback
):
    jsonpath = collection / (organization + ".json")

    git_data = {"team_sum": 0, "leader_board": None, "team": None, "period": period}
    try:
        with open(jsonpath) as json_file:
            data = json.load(json_file)
            local_git_data = update_leaderboard(
                token, data, period, fetch_from_cloud=False
            )
            on_local_store(local_git_data)
            # return local_git_data if the selected period is within the stored data period
            if period[1] <= data["period"][1]:
                return local_git_data
            else:
                # Retrieve user IDs for all members of the organization
                git_data["team"] = get_organization_members(token, organization)
    except:
        print(f"{jsonpath} not found")
        git_data["team"] = get_organization_members(token, organization)

    git_data = update_leaderboard(token, git_data, period)

    longest_username = ""
    git_data["team_sum"] = 0

    if git_data["leader_board"]:
        # Find the longest username
        for user in git_data["leader_board"]:
            user_name = user["name"] or user["login"]
            if len(user_name) > len(longest_username):
                longest_username = user_name

        if log:
            print(f"\nGithub Contributions {organization}'s team\n")
        # Print sorted user data with periodSum
        for user in git_data["leader_board"]:
            user_name = user["login"]
            # Calculate the length of the username considering double width characters
            username_length = sum(2 if ord(c) > 127 else 1 for c in user_name)
            padding_length = len(longest_username) - username_length
            padding = " " * padding_length
            if log:
                print(
                    f"{user['role'] or 'USER'}\t{user_name}{padding}\ttotal: {user['contributions']['totalContributions']} \tperiod: {user['periodSum']}"
                )
            git_data["team_sum"] += user["periodSum"]

    print(
        f"\nContributions in period {period[0]} - {period[1]}: {git_data['team_sum']}\n"
    )

    collection.mkdir(exist_ok=True)
    jsonpath.write_text(
        json.dumps(git_data, indent=4, sort_keys=True, ensure_ascii=False)
    )

    return git_data
