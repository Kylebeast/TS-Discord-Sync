import discord
from discord.ext import commands
from discord import Embed
import ts3

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# TeamSpeak Configuration
ts3_server_ip = ""  # TeamSpeak server IP
ts3_server_query_port = 10011  # Default TeamSpeak query port
ts3_username = "s"  # Your TS3 query login name
ts3_password = ""  # Your TS3 query login password
ts3_virtual_server_id = 1  # TS3 virtual server ID


admin_role_id =   # Put your admin role here


# Role Mapping (Discord Role ID -> TS3 Server Group ID)
role_mapping = {
    1312590368860147732: 9,  # Discord Role ID -> TS3 Group ID
    1312590395997163605: 10,
}


def check_ts3_connection():
    print("Checking TeamSpeak connection...")
    try:
        with ts3.query.TS3Connection(ts3_server_ip, ts3_server_query_port) as ts3conn:
            ts3conn.login(client_login_name=ts3_username, client_login_password=ts3_password)
            ts3conn.use(sid=ts3_virtual_server_id)
            print("Successfully connected to TeamSpeak server.")
            return True
    except ts3.query.TS3QueryError as e:
        print(f"TeamSpeak connection error: {e.resp.error['msg']}")
        return False
    except Exception as e:
        print(f"Unexpected error during TeamSpeak connection: {str(e)}")
        return False


def get_group_names(ts3conn):
    """Retrieve a dictionary mapping group IDs to group names."""
    try:
        group_list = ts3conn.servergrouplist()
        return {int(group["sgid"]): group["name"] for group in group_list}
    except ts3.query.TS3QueryError as e:
        print(f"Error retrieving group names: {e.resp.error['msg']}")
        return {}
    except Exception as ex:
        print(f"Unexpected error retrieving group names: {ex}")
        return {}



@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print("Verifying TeamSpeak connection...")
    if not check_ts3_connection():
        print("Failed to connect to TeamSpeak server. Please check your configuration.")
    else:
        print("TeamSpeak connection verified successfully.")


@bot.command(name="sync", help="Usage: !sync <ts_uid> - Sync your Discord roles with TeamSpeak roles.")
async def sync(ctx, ts_uid: str):
    """Sync Discord roles with TeamSpeak roles."""
    if not ctx.guild:
        await ctx.send("This command can only be used in a server.")
        return

    member = ctx.author
    discord_roles = [role.id for role in member.roles]
    ts3_groups = [role_mapping[role_id] for role_id in discord_roles if role_id in role_mapping]

    if not ts3_groups:
        embed = Embed(
            title="Failed to Sync Roles",
            description="You do not have any matching roles to sync.",
            color=0xFF0000  
        )
        embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)
        return

    roles_added = []

    try:
        with ts3.query.TS3Connection(ts3_server_ip, ts3_server_query_port) as ts3conn:
            ts3conn.login(client_login_name=ts3_username, client_login_password=ts3_password)
            ts3conn.use(sid=ts3_virtual_server_id)

            try:
                client_info = ts3conn.clientgetnamefromuid(cluid=ts_uid)
                cldbid = client_info[0]["cldbid"]
            except ts3.query.TS3QueryError as e:
                embed = Embed(
                    title="Failed to Sync Roles",
                    description=f"UID `{ts_uid}` not found on the TeamSpeak server or invalid TSUID.",
                    color=0xFF0000  
                )
                embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
                await ctx.send(embed=embed)
                return

            group_names = get_group_names(ts3conn)

            client_groups = ts3conn.servergroupsbyclientid(cldbid=cldbid)
            existing_group_ids = [int(group["sgid"]) for group in client_groups]

            for group_id in ts3_groups:
                if group_id not in existing_group_ids:
                    try:
                        ts3conn.servergroupaddclient(sgid=group_id, cldbid=cldbid)
                        roles_added.append(group_names.get(group_id, f"Group ID: {group_id}"))  
                        print(f"Successfully added group {group_id} to UID {ts_uid}.")
                    except ts3.query.TS3QueryError as e:
                        print(f"Error adding group {group_id} to UID {ts_uid}: {e.resp.error['msg']}")
                    except Exception as ex:
                        print(f"Unexpected error adding group {group_id} to UID {ts_uid}: {ex}")
                else:
                    print(f"Group {group_id} already assigned to UID {ts_uid}, skipping.")

            embed = Embed(
                title="Roles Synced Successfully!",
                description=f"Roles have been synced for UID:\n`{ts_uid}`",
                color=0x00FF00  
            )
            embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
            embed.add_field(name="Synced By", value=f"{ctx.author.mention}", inline=True)

            if roles_added:
                added_roles_str = "\n".join(roles_added)
                embed.add_field(name="Roles Added", value=added_roles_str, inline=False)
            else:
                embed.add_field(name="Roles Added", value="No new roles were added. All roles are already assigned.", inline=False)

            await ctx.send(embed=embed)

    except Exception as e:
        embed = Embed(
            title="An Error Occurred",
            description=f"An unexpected error occurred:\n`{str(e)}`",
            color=0xFF0000  
        )
        embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)


@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = Embed(
            title="Error: Missing Argument",
            description="You must provide a TeamSpeak UID to use this command.\n\n**Usage:** `!sync <ts_uid>`",
            color=0xFF0000  
        )
        embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)
    else:
        embed = Embed(
            title="An Unexpected Error Occurred",
            description=f"Error: {str(error)}",
            color=0xFF0000  r
        )
        embed.set_footer(text="Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)


@bot.command(name="user", help="Usage: !user <ts_uid> <add/remove> <group_id> - Manage roles for a TeamSpeak user.")
async def user(ctx, ts_uid: str, action: str, group_id: int):
    
    if admin_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("You do not have permission to use this command.")
        return

    if action.lower() not in ["add", "remove"]:
        await ctx.send("Invalid action. Use 'add' or 'remove'.")
        return

    try:
        with ts3.query.TS3Connection(ts3_server_ip, ts3_server_query_port) as ts3conn:
            ts3conn.login(client_login_name=ts3_username, client_login_password=ts3_password)
            ts3conn.use(sid=ts3_virtual_server_id)

            try:
                client_info = ts3conn.clientgetnamefromuid(cluid=ts_uid)
                cldbid = client_info[0]["cldbid"]
            except ts3.query.TS3QueryError as e:
                embed = Embed(
                    title="Failed to Manage Role",
                    description=f"UID `{ts_uid}` not found on the TeamSpeak server or invalid TSUID.",
                    color=0xFF0000  
                )
                embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
                await ctx.send(embed=embed)
                return

            if action.lower() == "add":
                try:
                    ts3conn.servergroupaddclient(sgid=group_id, cldbid=cldbid)
                    embed = Embed(
                        title="Role Added Successfully",
                        description=f"Role (Group ID: `{group_id}`) has been added to UID `{ts_uid}`.",
                        color=0x00FF00  
                    )
                    embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
                    await ctx.send(embed=embed)
                except ts3.query.TS3QueryError as e:
                    await ctx.send(f"Failed to add role: `{e.resp.error['msg']}`")
            elif action.lower() == "remove":
                try:
                    ts3conn.servergroupdelclient(sgid=group_id, cldbid=cldbid)
                    embed = Embed(
                        title="Role Removed Successfully",
                        description=f"Role (Group ID: `{group_id}`) has been removed from UID `{ts_uid}`.",
                        color=0xFFFF00  
                    )
                    embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
                    await ctx.send(embed=embed)
                except ts3.query.TS3QueryError as e:
                    await ctx.send(f"Failed to remove role: `{e.resp.error['msg']}`")

    except Exception as e:
        embed = Embed(
            title="An Error Occurred",
            description=f"An unexpected error occurred:\n`{str(e)}`",
            color=0xFF0000  
        )
        embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)

@user.error
async def user_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: `!user <ts_uid> <add/remove> <group_id>`")
    else:
        await ctx.send("An error occurred while processing your request.")
        print(f"Unexpected error: {error}")


@user.error
async def user_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: `!user <ts_uid> <add/remove> <group_id>`")
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("You do not have permission to use this command.")
    else:
        await ctx.send("An error occurred while processing your request.")
        print(f"Unexpected error: {error}")




@bot.command(name="checkuser", help="Usage: !checkuser <ts_uid> - View roles of a TeamSpeak user.")
async def checkuser(ctx, ts_uid: str):
   

    if admin_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("You do not have permission to use this command.")
        return

    try:
        with ts3.query.TS3Connection(ts3_server_ip, ts3_server_query_port) as ts3conn:
            ts3conn.login(client_login_name=ts3_username, client_login_password=ts3_password)
            ts3conn.use(sid=ts3_virtual_server_id)

            try:
                client_info = ts3conn.clientgetnamefromuid(cluid=ts_uid)
                cldbid = client_info[0]["cldbid"]
            except ts3.query.TS3QueryError as e:
                embed = Embed(
                    title="Failed to Retrieve Roles",
                    description=f"UID `{ts_uid}` not found on the TeamSpeak server or not a valid TSUID.",
                    color=0xFF0000  
                )
                embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
                await ctx.send(embed=embed)
                return

            client_groups = ts3conn.servergroupsbyclientid(cldbid=cldbid)
            group_names = get_group_names(ts3conn)   
            user_roles = [
                f"{group_names[int(group['sgid'])]} ({group['sgid']})" for group in client_groups
            ]

            embed = Embed(
                title="TeamSpeak User Roles",
                description=f"Roles for UID: `{ts_uid}`",
                color=0x00FFFF  
            )
            embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
            embed.add_field(
                name="Roles",
                value="\n".join(user_roles) if user_roles else "No roles assigned.",
                inline=False
            )

            await ctx.send(embed=embed)

    except Exception as e:
        embed = Embed(
            title="An Error Occurred",
            description=f"An unexpected error occurred:\n`{str(e)}`",
            color=0xFF0000  
        )
        embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)


@checkuser.error
async def checkuser_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: `!checkuser <ts_uid>`")
    else:
        await ctx.send("An error occurred while processing your request.")
        print(f"Unexpected error: {error}")


@bot.command(name="showallids", help="Displays all TeamSpeak role IDs and their corresponding names.")
async def showallids(ctx):
    
    if admin_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("You do not have permission to use this command.")
        return

    try:
        with ts3.query.TS3Connection(ts3_server_ip, ts3_server_query_port) as ts3conn:
            ts3conn.login(client_login_name=ts3_username, client_login_password=ts3_password)
            ts3conn.use(sid=ts3_virtual_server_id)

            server_groups = ts3conn.servergrouplist()

            group_list = [
                f"**{group['name']}** (ID: `{group['sgid']}`)" for group in server_groups
            ]

            embed = Embed(
                title="TeamSpeak Role IDs",
                description="\n".join(group_list) if group_list else "No roles found.",
                color=0x00FFFF 
            )
            embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
            await ctx.send(embed=embed)

    except Exception as e:
        embed = Embed(
            title="An Error Occurred",
            description=f"An unexpected error occurred:\n`{str(e)}`",
            color=0xFF0000  
        )
        embed.set_footer(text="Admin Sync Bot • Powered by TeamSpeak")
        await ctx.send(embed=embed)


@showallids.error
async def showallids_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("This command does not require any arguments.")
    else:
        await ctx.send("An error occurred while processing your request.")
        print(f"Unexpected error: {error}")


bot.run("YOUR_TOKEN_HERE")
