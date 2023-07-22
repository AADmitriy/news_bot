from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.filters import Text
from aiogram.types import Message

import logging

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
    'site': 'https://www.example.com',
    'page': '/news/',
    'article': {'all': 'div.article_news_list',
                'main': 'div.article_news_bold'},
    'time': 'div.article_time',
    'text': 'div.article_header a',
    'href': 'div.article_header a'
}

logging.info(website['site'] + website['page'])


def parse(mode: int):
    """
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

    site_data = parser.parse()
    if not site_data:
        logging.error('parser returned None')
        return ["Something happened! No results!"]

    result_str = ''
    for article in site_data:
        text = article[1]
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
            while len(message) < 3900 and articles:
                article = articles.pop(0) + '\n'
                message += article
            results_list.append(message)
            message = ''

        return results_list
    else:
        return [result_str]


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
    for msg in parse(0):
        await message.answer(text=msg, parse_mode="HTML")


@router.message(Text("Найважливіші новини"))
async def cmd_main_news(message: Message):
    for msg in parse(1):
        await message.answer(text=msg, parse_mode="HTML")
