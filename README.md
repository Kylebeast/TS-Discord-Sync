# TeamSpeak Discord Sync Bot

---

## Features

- **Role Synchronization**:
  - Sync Discord roles to TeamSpeak groups.
  - Add or remove TeamSpeak roles using Discord commands.

- **Admin Commands**:
  - View the TeamSpeak roles of a user with `!checkuser`.
  - Add or remove TeamSpeak roles for a user with `!user`.

- **Show All Role IDs**:
  - List all TeamSpeak server group IDs and their names with `!showallids`.

---

## Commands

### General Commands

- **`!sync <ts_uid>`**  
  Sync your Discord roles with TeamSpeak server groups.  
  Example: `!sync C5zwKldBeHQc3DP4F4JGkuaFSvk=`  
  **Note**: `ts_uid` is the TeamSpeak user’s unique identifier.

### Admin Commands

- **`!user <ts_uid> <add/remove> <group_id>`**  
  Add or remove a TeamSpeak role for a user.  
  Example: `!user C5zwKldBeHQc3DP4F4JGkuaFSvk= add 9`

- **`!checkuser <ts_uid>`**  
  View the roles of a TeamSpeak user by their UID.  
  Example: `!checkuser C5zwKldBeHQc3DP4F4JGkuaFSvk=`

- **`!showallids`**  
  Show all TeamSpeak role IDs and their corresponding names.  
  Example: `!showallids`

---

## Requirements

### TeamSpeak Configuration

- Enable the TeamSpeak Query interface.
- Get the following details from your TeamSpeak server:
  - **Server IP**
  - **Query Port** (default: `10011`)
  - **Admin Login** credentials (`serveradmin` username and password).
  - **Virtual Server ID** (usually `1`).

### Discord Bot Configuration

- Create a Discord bot via the [Discord Developer Portal](https://discord.com/developers/applications).
- Get your bot token and invite the bot to your server.

---

## Getting Started

To get your TeamSpeak-Discord Sync Bot up and running, follow these steps:

### 1. **Set Up Configuration**

Before starting the bot, you need to make sure your TeamSpeak and Discord configurations are correct:

1. **Open the `ts3_discord_sync.py` file** in a code editor.
2. **Set your TeamSpeak server information**:
   - `ts3_server_ip`: Replace this with the IP address of your TeamSpeak server.
   - `ts3_username` and `ts3_password`: Provide your TeamSpeak Query login credentials.
   - `ts3_virtual_server_id`: Ensure this is the correct virtual server ID in your TeamSpeak server.

3. **Set your Discord Bot information**:
   - Replace the placeholder for `discord_token` with your Discord bot's token.
   
4. **Set the admin role ID**:
   - Update `admin_role_id` with the correct Discord role ID that grants admin permissions to users for admin commands.

5. **Map your Discord roles to TeamSpeak groups**:
   - Update the `role_mapping` dictionary with the correct mapping of Discord role IDs to TeamSpeak server group IDs.

### 2. **Install Dependencies**

If you haven't done so already, install the required dependencies for the bot:

```bash
pip install discord.py
pip install ts3


### 3. **Run the Bot**

Once you've set up the configurations and installed the dependencies, you can run the bot using the following command:

```bash
python ts3_discord_sync.py
