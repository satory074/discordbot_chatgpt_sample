import re

import openai
from discord import Client, Intents, Message, Thread

TOKEN = ""  # discord botのtoken
openai.api_key = ""  # openaiのapi key

LIMIT = 200  # openaiにAPIで送る会話の上限

client: Client = Client(intents=Intents.all())


async def chatgpt(message: Message):
    """ chatGPTによるreplyを行う"""

    # メッセージから@を除去
    escape_content: str = re.sub(r"<@(everyone|here|[!&]?[0-9]{17,20})> ", "", message.content)

    if type(message.channel) is Thread:  # messageがスレッド内の場合
        thread: Thread = message.channel

        # openaiに送るメッセージ
        messages: list[dict[str, str]] = []

        # スレッドの履歴をすべて取得
        async for mes in thread.history():
            # botとユーザーの区別
            role: str = "assistant" if mes.author == client.user else "user"

            messages.append({"role": role, "content": mes.content})

        # 上限と時系列を考慮したopenaiに送るメッセージリスト
        messages = messages[:200][::-1]
    else:  # messageがスレッド外の場合（@で呼ばれた場合）
        # スレッドを作成
        name: str = escape_content[:20]  # スレッド名
        thread: Thread = await message.create_thread(name=name)

        # openaiに送るメッセージ
        messages: list[dict[str, str]] = [{"role": "user", "content": escape_content}]

    # 結果を取得
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    # Reply
    reply: str = "\n".join([choice["message"]["content"] for choice in response["choices"]])
    await thread.send(reply)


@client.event
async def on_message(message: Message):
    """ メッセージを受信したときのイベント"""

    if client.user in message.mentions or type(message.channel) is Thread:

        # bot自身のメッセージは無視
        if message.author == client.user:
            return

        # Reply
        await chatgpt(message)


client.run(TOKEN)
