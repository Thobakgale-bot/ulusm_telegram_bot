# Ulusm Telegram Bot

**Ulusm Telegram Bot** is a custom Telegram bot designed to manage user interactions for private group invitations, country eligibility checking, and much more. This bot includes features like generating single-use invite links, country-based eligibility restrictions, and providing information about services and payment gateways.

## Features

- **Command Restrictions:** Commands are locked until the user issues the `/start` command to initiate a conversation.
- **Country Eligibility:** The bot checks if a user's country is eligible to join the group. Users from South American countries are ineligible.
- **Single-use Invite Links:** Eligible users can request to join a private group via a single-use invite link.
- **Poll Interaction:** Users are asked via a poll if they want to join the group. If they select "Yes," the bot generates a unique invite link.
- **Command Handling:** Users can access commands like `/help`, `/content`, `/contact`, and more after initiating the conversation.

## Prerequisites

- **Python 3.8+**
- **Telegram Bot Token** (from BotFather)
- **Telegram Group Invite Permissions** (the bot must have the permission to create invite links)
- **`countries.json` file** containing valid country names.

### Example `countries.json` structure:
```json
[
    {"name": "Afghanistan"},
    {"name": "Albania"},
    {"name": "Algeria"},
    ...
]
```

## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/ulusm-telegram-bot.git
cd ulusm-telegram-bot

```
2. Install the required dependencies: It's recommended to create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

## Usage

Start the bot: Users must begin interaction by sending the /start command. This unlocks all the other commands.

Available Commands:

`/start:` Initializes the conversation and unlocks other commands.
`/help:` Displays a list of available commands and descriptions.
`/content: `Provides information about services offered by the bot.
`/contact:` Displays contact details for the bot admin.
`/gateways:` Lists supported payment gateways.
`/rules:` Shows the rules and policies of the bot.
`/join_group:` Prompts the user for their country to check if they're eligible for group entry.
Poll to Join Group: After providing their country using /join_group, users will be presented with a poll asking if they would like to join the group. If they answer "Yes" and meet the eligibility criteria, a one-time invite link will be generated.

Users from South American countries are ineligible to join.
If the user has already been provided with an invite link, they will not receive another one.
Invite Link: A single-use invite link will be sent to eligible users after they respond "Yes" to the poll. The link is unique and can only be used once.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Feel free to fork this repository and submit pull requests to enhance the bot's functionality.


