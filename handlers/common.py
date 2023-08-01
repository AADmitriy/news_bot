from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.filters import Text
from aiogram.types import Message

import logging
import time as time_module

from .scrapers.content import Content

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)

router = Router()

# change css selectors to parse your site
# article ['all'] and ['main'] selectors are full path
# time, text, href are descendants of article tag their path is relative
website = {
    'site': 'https://www.example.ua',
    'page': '/news/',
    'article': {'all': 'div.article_news_list',
                'main': 'div.article_news_main'},
    'time': 'div.article_time',
    'text': 'div.article_header p',
    'href': 'div.article_link a'
}

logging.info(website['site'] + website['page'])


def parse(mode: int):
    """
    Gets data from site using Content instance,
    formats it and then splits.
    Args:
        param mode: define whether to scrape all articles
                    or only main articles
    Return:
        List of str messages or list with one error message
    """
    if mode == 0:
        # give info what to retrieve from site
        parser = Content(website['site'], website['page'], article=website['article']['all'],
                         time=website['time'], text=website['text'], href=website['href'])
    elif mode == 1:
        parser = Content(website['site'], website['page'], article=website['article']['main'],
                         time=website['time'], text=website['text'], href=website['href'])
    else:
        logging.warning('Was given incorrect mode')
        return ["Something happened! No results!"]

    # retrieves all info that was specified
    site_data = parser.parse()
    if not site_data:
        logging.error('parser returned None')
        return ["Something happened! No results!"]

    result_str = ''

    # site_data is list that contains lists with article values [ [time, text, href], [time, text, href] ]
    for article in site_data:
        text = article[1]
        # if article has no text, we do not add it to result_str
        if not text:
            continue

        time = article[0]
        href = article[2]

        result_str += '[{0}] -- {1} <a href="{2}" > [ Дивитись статтю ] </a>'.format(time, text, href) + '\n'

    if not result_str:
        logging.warning("'result_str' in empty")
        return ["Something happened! No results!"]

    # if result_str > 4096 symbols it can't fit in one telegram message
    # this why it must be split
    if len(result_str) > 4000:
        results_list = []
        articles = result_str.split('\n')
        message = ''

        while articles:
            # assumes that the title of the article will not be longer than 196 characters
            while len(message) < 3900 and articles:
                article = articles.pop(0) + '\n'
                message += article
            results_list.append(message)
            message = ''

        return results_list
    else:
        return [result_str]


class ParserWithTimer:
    """
    Class that stores cache of parse function,
    updating it if 5 minutes lasted from last func call
    """
    def __init__(self, mode, func=time_module.perf_counter):
        """
        Args:
            param mode: mode that is used for parse func
            param func: a function that returns the time,
                        what after is used to check the expiration of the cache
        """
        self._func = func
        self.mode = mode
        self._start = None
        self.text = None

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started!')
        self._start = self._func()

    def get_time(self):
        end = self._func()
        return end - self._start

    def get_text(self):
        """
        This func checks whether cache is exists and whether is expired,
        if there is no fresh cache, creates new cache and start timer
        return: result of parse function
        """
        if self.text and self.get_time() < 300.0:  # 5 * 60 = 300 sec
            return self.text
        self._start = None
        self.text = parse(self.mode)
        self.start()
        return self.text


pars_0 = ParserWithTimer(0)
pars_1 = ParserWithTimer(1)


@router.message(Command(commands="start"))
async def cmd_start(message: Message):
    kb = [
        [
            types.KeyboardButton(text="Всі новини"),
            types.KeyboardButton(text="Найважливіші новини")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
    )
    await message.answer(text="Які новини показати?", reply_markup=keyboard)


@router.message(Text("Всі новини"))
async def cmd_all_news(message: Message):
    text = pars_0.get_text()
    for msg in text:
        await message.answer(text=msg, parse_mode="HTML")


@router.message(Text("Найважливіші новини"))
async def cmd_main_news(message: Message):
    text = pars_1.get_text()
    for msg in text:
        await message.answer(text=msg, parse_mode="HTML")
