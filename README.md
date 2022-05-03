# Quotes Bot
A Discord bot for your funny quotes!

This bot monitors registered channels on the Discord servers it is a member of. It is meant to be easily deployable so anyone can launch their own Quotes Bot for their community and manage the SQLite database however they want.

## Data Collection Informations
If you use or consider using this bot, here are the data collection informations you need to know.

This bot will collect data from a designated "quotes" channel. Any messages posted in the channel will be processed. The data (the quote) is only stored if it meets the correct format. If it doesn't meet the expected format, the quote is not stored in the bot's local database. In the database, each server has a table created with it's guild ID prefixed with `s`. The quotes are stored with the mentionned user ID of the user supposedly being quoted inside the table of the Discord server the message has been posted.

Handling of the data in the database collected by the bot is to the responsibility of whoever is hosting an instance of this bot. I am not responsible for any mishandling of the data collected by this code.

## Setup

Although this bot can be setup on Windows, I will only provide a setup script and setup information for Linux operating systems.

First, clone this repository or download and extract the code from the newest release.
```bash
git clone https://github.com/Shijikori/quotes-bot.git
```

Then start the `setup-botenv.sh` script. This will setup the virtual environment(venv) for python to run inside.
```bash
./setup-botenv.sh
```

Next, you will want to copy `template-dotenv` to `.env` and fill out the information from the developer portal for your own bot.
```bash
cp template-dotenv .env

nano .env
```

Finally, once you have filled out the `.env` file, you can run the following commands.
```bash
source .botenv/bin/activate

python bot.py
```
The first command activates the venv. The following command launches the python bot.

## General bot usage

See the Wiki tab for general bot usage informations.

## Planned features and development

* [X] Remove unecessary code
* [ ] Query quotes with keywords (with and without provided user)
* [X] Read and store the contents of past messages in registered channels
* [X] Designate a quotes channel using a command
* [ ] MySQL version (uncertain)
* [ ] Make a wiki on GitHub

### Thanks to GitHub user gabrielb-l for working with me on the first version of this project!
