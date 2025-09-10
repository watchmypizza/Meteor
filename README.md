# What is this bot and how does it work?

The bot is supposed to be an all-in-one bot for moderation (Dyno), levels (Arcane) and Counting (Counting)

You can use chat commands (UNIX inspired) using the prefix **"$ "**

**The space between the command and the prefix is mandatory, or the command won't execute.**

Currently the bot has an amount of **36** commands. Though the number may vary every time the bot updates. Don't expect this number to be updated everytime there is a new command.

# Roadmap

[x] Base functionality, running bot

[x] Moderation commands

[x] Counting commands

[x] Per-Server configuration

[x] Level system

[x] Customisable level roles

[ ] Customisable prefix

[ ] Modals and buttons

[ ] Tickets functionality (Replacing ticketbot)

[ ] Automod

[ ] Smart automod (Using ollama)

I will add more to this list depending on suggestions or what I come up with.

# Command Overview

The bot has a total of 36 commands (including sub-commands). This number may update every once in a while, but don't expect it to be often.

--- Configuration Commands ---

/configure levelroles >> Configure levelroles to add / remove them (you can add as many as you want)

/configure logging >> Select a message logging channel

/configure welcomer >> Select a channel like #welcome for welcome and goodbye messages

/configure announcement >> Select a announcement channel for the $ wall command

/configure modlogs >> Set a dedicated mod-logs channel to log moderation actions

/configure botrole >> Set a role that is the bot role, members under this role will not be counted as members in the $ ls command

--- Counting Commands ---

/counting configure >> Configure the counting aspect of the bot and tweak specific settings

/counting reset >> Reset the current count

/counting channel >> (mandatory) Select a dedicated counting channel (ex. #counting)

/counting start >> Start counting in the counting channel

/counting stop >> Stop / pause counting in the counting channel (This will not reset your count)

--- Level Commands ---

/level show >> Show the level of yourself or from another user

/level lock >> Lock a user's level and XP

/level set >> Set the level/XP of a user

/level exclude >> Exclude a channel from earning XP (ex. #counting, #spam)

/level leaderboard >> Display the levelling leaderboard of your server

--- Miscellaneous ---

$ ls >> Shows information about the server

$ cat >> Open a file that is in the GitHub repo in read mode

$ pwd >> Show the current path the bot is running on

$ man <Command> >> Shows a description of the command

$ wall <Message> >> Post a message to the announcement channel

/latency >> Measure your latency to the bot

/membercount >> Show the current membercount (this excludes the bot role aswell)

/slash >> This is the first slash command added to the bot, it serves to get the active developer badge

/suki >> A friend of mine suggested to add and name the command as is today, grabs a random cat image and sends a ephemeral

/warnings >> Allows you to view your own warnings displayed as an ephemeral

--- Moderation ---

$ rm -r(f) <User> --message <Reason> >> The option -rf bans a user, the option -r only kicks a user.

$ clear >> Clear a specific amount of messages

$ usermod -l <new username> <old username> >> Change the display name of a user

/mute <User> <Duration> <Reason> >> Times a user out for a specified amount of time

/warn <User> <Reason> >> Warns a user for the reason, also sends a DM to the user automatically

/warnings <User> >> Shows the warnings for a user if they have any. (Looking at your own warnings does not require moderation privileges)

/removewarn <User> <Number> >> Remove a warning from a user, you can view the number of warnings of a specific user by executing above command.