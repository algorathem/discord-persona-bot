# Custom Persona Discord Bot

A Discord bot designed for Discord communities to send messages via custom avatars, manage roles for new members and specific user groups, and facilitate interaction and engagement. Perfect for communities, clubs, or projects that want fun persona-based messaging and automated role management.

## Features

* Send messages as different avatars using `!say` command
* Assign roles to new members
* Caches webhooks per channel for faster message sending
* Admin/Owner permission control for commands

## Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. **Create a `.env` file** in the root directory:

```env
BOT_OWNER_ID="YOUR_DISCORD_USER_ID"
DISCORD_TOKEN="YOUR_BOT_TOKEN"
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the bot**

```bash
python main.py
```

## Usage

* **Send a message as an avatar**

```text
!say scholar Hello everyone!
```

Available avatars: `scholar`, `herald`, `envoy`

* **Role assignment**

  * New users get a default role assignment
  * React with an emoji to change roles

## Permissions

* Commands are restricted to **Bot Owner** or users with `Admin` role
* Ensure the bot has **Manage Roles** and **Manage Webhooks** permissions

## Notes

* Webhooks are cached per channel to reduce lag
* Compatible with Python 3.11+
