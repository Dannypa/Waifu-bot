import logging
import random
import time
import aiogram
import config
import data
from waifuim import WaifuAioClient
from curse import random_curse

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename="waifuBot.log"
)
bot = aiogram.Bot(token=config.TOKEN)
dp = aiogram.Dispatcher(bot)
mari_pics = []


def load_mari_pics():
    with open(config.MARI_PHOTOS_IDS_FILENAME, 'r') as f:
        for line in f.readlines():
            mari_pics.append(line.strip())


@dp.message_handler(commands=['start'])
async def start_command(message: aiogram.types.Message):
    await bot.send_message(message.chat.id, data.start_text)


@dp.message_handler(content_types=[aiogram.types.ContentType.NEW_CHAT_MEMBERS])
async def new_member(message: aiogram.types.Message):
    for member in message.new_chat_members:
        if member.username == 'WaifuBot':
            await bot.send_message(message.chat.id, text=data.greeting_text)


@dp.message_handler(commands=['help'])
async def help_command(message: aiogram.types.Message):
    await bot.send_message(message.chat.id, data.help_text)


@dp.message_handler(commands=['mari'])
async def mari_command(message: aiogram.types.Message):
    await send_mari_pic(message.chat.id)


async def send_mari_pic(cid, reply_to_message_id=None, extremely_funny_line=""):
    index = random.randint(0, len(mari_pics) - 1)
    if reply_to_message_id is None:
        await bot.send_photo(cid, caption=extremely_funny_line, photo=mari_pics[index])
    else:
        await bot.send_photo(cid, caption=extremely_funny_line, reply_to_message_id=reply_to_message_id,
                             photo=mari_pics[index])


@dp.message_handler(commands=['image'])
async def image_command(message: aiogram.types.Message):
    for _ in range(config.RETRY_NUMBER):
        try:
            wf = WaifuAioClient()
            args = message.get_args()
            print(args)
            for arg in args.split():
                if arg == "loli":
                    await bot.send_message(chat_id=message.chat.id,
                                           text=data.no_loli_text)
                    return
                if arg not in data.tags:
                    await bot.send_message(chat_id=message.chat.id, text=data.unknown_tag_text.format(random_curse()))
                    return
            res = await wf.search(included_tags=args.split())
            await wf.close()
            await bot.send_photo(chat_id=message.chat.id, photo=str(res))
            return
        except Exception as e:
            logging.error(e)
            time.sleep(1)
    await bot.send_message(message.chat.id, data.error_text)


@dp.message_handler(content_types=['text', 'photo'])
async def random_pic(message: aiogram.types.Message):
    r = random.random()
    if r < config.PIC_PROBABILITY:
        await send_mari_pic(message.chat.id, reply_to_message_id=message.message_id,
                            extremely_funny_line=random.choice(data.extremely_funny_lines))


def main():
    load_mari_pics()
    aiogram.executor.start_polling(dp, timeout=600)


if __name__ == '__main__':
    main()
