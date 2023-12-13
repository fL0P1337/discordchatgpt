import datetime
import embeds
import io
import os
from datetime import datetime
import aiohttp
import disnake
import g4f
import nest_asyncio
import python_weather
from disnake.ext import commands
from gtts import gTTS
from pytube import YouTube
from rembg import remove
from PIL import Image
nest_asyncio.apply()
time = datetime.now()
activity = disnake.Activity(
    name="!help / Currently working",
    type=disnake.ActivityType.playing,
)

bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), help_command=None,activity=activity)
client = python_weather.Client(unit=python_weather.IMPERIAL,locale=python_weather.Locale.RUSSIAN)
@bot.event
async def on_ready():
    ready_to_work = str(time)+": "+f" Bot {bot.user} is ready to work!"
    logs_on_ready = ['\n'+
    "[INFO] "+ready_to_work]
    with open('logs/logsDS.txt', 'a') as f:
        f.write('\n'.join(logs_on_ready))
    print(logs_on_ready.pop(0))
@bot.command()
async def help(ctx):
    await ctx.reply(embed=embeds.help_msg())
    embeds.logger("!help", ctx.author, ctx," ")
@bot.slash_command(description="Will show you credits like used libs and author of this bot")
async def credits(inter):
    await inter.response.send_message(embed=embeds.credits_msg())
    embeds.logger("!credits", inter.author, inter, " ")
@bot.slash_command(description="Most important function in this bot")
async def randomcat(inter):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/cat') as resp:
                    data = io.BytesIO(await resp.read())
                    await inter.response.send_message(embed=embeds.req_done(" ").set_image(file=disnake.File(data,"cool_image.png")))
                    embeds.logger("!randomcat", inter.author, inter, data)
    except Exception as error:
        await inter.response.send_message(embed = embeds.req_failed(error=error))
@bot.slash_command(description="chatGPT will write whatever you ask!")
async def chatgpt(inter, *, your_prompt: str):
    try:
        await inter.response.send_message(embed=embeds.req_claim())
        resp_msg = await g4f.ChatCompletion.create_async(model=g4f.models.default,messages=[
                    {"role": "user",
                    "content": your_prompt}], )
        await inter.edit_original_response(embed=embeds.req_done(resp_msg))
        embeds.logger("!chatgpt", inter.author, your_prompt, resp_msg)
    except Exception as error:
        await inter.edit_original_response(embed = embeds.req_failed(description=error))
@bot.slash_command(description="Convert YouTube video into mp3!")
async def ytmp3(inter, *, youtube_link: str):
    try:
        await inter.response.send_message(embed=embeds.req_claim())
        yt = YouTube(youtube_link)
        filename = "files\\ytmp3\\converted"+".mp3"
        yt.streams.filter(only_audio=True).first().download(filename=filename)
        await inter.edit_original_response(embed=embeds.req_done("Видео загружено!\nНачинаю процесс конвертации..."))
        with open(filename,"rb") as fp:
            await inter.edit_original_response(embed= embeds.req_done("Успешно сконвертировано!"), file=disnake.File(fp,yt.title+".mp3"))
            embeds.logger("!ytmp3", inter.author, youtube_link, filename)
    except Exception as error:
        await inter.edit_original_response(embed=embeds.req_failed(error))
        embeds.logger("!ytmp3", inter.author, inter, error)
@bot.slash_command(description="Find current weather in any city of the world")
async def weather(inter, *, any_city: str):
    try:
        await inter.response.send_message(embed=embeds.req_claim())
        weather = await client.get(any_city)
        celsius = (weather.current.temperature - 32) * 5 / 9
        feels = (weather.current.feels_like - 32) * 5 / 9
        date = weather.current.date
        wind_speed = str(weather.current.wind_speed)
        description_msg = (f"Текущая погода в городе {any_city.capitalize()}: \n"
                          f"Текущее состояние погоды: {weather.current.description}\n"
                          f"Текущая атмосферная температура: {round(celsius)}°C (ощущается как {round(feels)}°C)\n"
                          f"Текущая скорость ветра: {wind_speed}км/ч")
        await inter.edit_original_response(embed=embeds.req_done(description_msg))
        embeds.logger("!weather", inter.author, any_city, description_msg)
    except Exception as error:
       await inter.edit_original_response(embed=embeds.req_failed(error))
       embeds.logger("!weather", inter.author, any_city, error)
@bot.slash_command(description="Google text to speach will convert your message to speach!")
async def gtts(inter, language: str,*, message: str):
    try:
        textGTTS = message
        tts = gTTS(text=textGTTS, lang=language)
        out_file = "files\\gtts\\gtts.mp3"
        tts.save(out_file)
        with open(out_file, "rb") as fp:
            await inter.response.send_message(embed=embeds.req_done("Успешно!"),file=disnake.File(fp,message+".mp3"))
            embeds.logger("!gtts", inter.author, language+" "+message, out_file)
    except Exception as error:
        await inter.response.send_message(embeds.req_failed(error))
        embeds.logger("!gtts", inter.author, message, error)
@bot.command(description="Remove backround from any photos")
async def rembg(ctx):
    try:
        for attachment in ctx.message.attachments:
            await ctx.reply(embed=embeds.req_claim())
            await attachment.save('files\\rembg\\'+attachment.filename)
            input_path = f"files\\rembg\\{attachment.filename}"
            output_path = f"files\\rembg\\{attachment.filename}_rembg.png"
            img = Image.open(input_path)
            output = remove(img)
            output.save(output_path)
        await ctx.reply(embed = embeds.req_done(" ").set_image(file=disnake.File(output_path)))
        embeds.logger("!rembg", ctx.author, attachment.filename, output_path)
    except Exception as error:
        await ctx.message.reply(embed=embeds.req_failed(error))
        embeds.logger("!rembg", ctx.author, attachment.filename, error)
bot.run('your_token')
