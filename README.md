# News_bot
Simple, customizable bot for scraping news sites

![preview](bot_record_2.gif)

## Used technology
* Python 3.11.0
* aiogram 3.x (Telegram Bot framework)
* beautifulsoup4 4.12.2 (Python library for pulling data out of HTML and XML files)

## Installation

Create directory of your choice, let's say '/somedir/example' . Inside in create virtual enviroment 
and copy this repository.

Than download requirements to venv by activating it and running 'pip install -r requirements.txt'.

Grab '.env_example' file rename it to '.env'. Open it and set your own bot_token.

Go to 'handlers/common.py' file and change website dict, setting your own selectors.

Finally, go the dir with bot.py and start your bot with 'py bot.py' command.



### Please, be careful, if bot would have a lot of users it could possibly overload server causing some material loss to the site owner.
### Created in educational purpose for real news bot better to use API
