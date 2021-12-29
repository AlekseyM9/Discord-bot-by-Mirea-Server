import random

import discord.ext.commands
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle
import qr_code
import youtube_dl
import os

bot = commands.Bot(command_prefix='{{', intents=discord.Intents.all())
# Сброс команды
bot.remove_command('help')
id_channel = 922173142598815757
# Компоненты для работы кнопок
DiscordComponents(bot)


# Включение бота и подтверждение что он залогинелся
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    # Статус бота
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Mirea'))


# Повторение сообщения в чате каждые 12 часов
@tasks.loop(hours=12)
async def called_once_a_day():
    message_channel = bot.get_channel(id_channel)
    await message_channel.send(f'Доброго времени суток, @everyone!'
                               f'\n-Перед тем как собирётесь покидать канал, отметьте @Aleksey_M9, покидаю канал. '
                               f'Или используйте комманду' ' {{send и отметьте свой ник.')


# Включение таймера
@called_once_a_day.before_loop
async def before():
    await bot.wait_until_ready()


called_once_a_day.start()


# Реакция бота на подключение новых людей
@bot.event
async def on_member_join(member):
    message_channel = bot.get_channel(id_channel)
    await message_channel.send(f'Привет, {member.mention}! Ты попал на канал {member.guild.name}. '
                               f'Чтобы узнать мои команды пропиши'' {{help')


# Вывод команд используемых на сервере
@bot.command(pass_context=True)
async def help(ctx):
    # Создание таблички
    embed = discord.Embed(title='Подсказки:',
                          color=discord.Color.random(),
                          )
    # Ввод и вывод данных
    embed.set_image(
        url='https://icdn.lenta.ru/images/2021/07/16/13/20210716132921942/detail_ec68c38296ad69e8abfa53f1032dea85.jpg')

    embed.add_field(name='{{server', value='Свежие данные')
    embed.add_field(name='{{google', value='Поисковик')
    embed.add_field(name='{{qr', value='[ссылка]')
    embed.add_field(name='{{key', value='🔐')
    embed.add_field(name='{{youtube', value='Музыка')
    embed.add_field(name='{{game', value='🪨✂🧻')
    embed.add_field(name='{{random', value='🎱')
    embed.add_field(name='{{private', value='Команды администратора')

    await ctx.send(embed=embed)


# Информация о сервре
@bot.command()
async def server(ctx):
    # Передача информации
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    member_count = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon_url)

    # Создание таблички
    embed = discord.Embed(
        title=name + ' Информация о сервере:',
        description=description + '👻',
        color=discord.Color.blue(),
    )
    # Ввод и вывод данных
    embed.set_thumbnail(url=icon)
    embed.add_field(name='Администратор:', value=owner, inline=True)
    embed.add_field(name='ID Сервера:', value=id, inline=True)
    embed.add_field(name='Подписчки:', value=member_count, inline=True)
    await ctx.send(embed=embed)


# Выход на поисковик google
@bot.command(pass_context=True)
async def google(ctx):
    embed = discord.Embed(
        title='Погодите-ка',
        description='Эта ссылка ведет на: Поисковик Google!',
        url='https://www.google.ru/',
        color=discord.Color.random(),
    )
    # Вывод гиперссылки на сайт
    embed.set_image(url='https://kgo.googleusercontent.com/profile_vrt_raw_bytes_1587515358_10512.png')
    await ctx.send(embed=embed)
    # Кнопки для сервисов
    await ctx.send('Другие сервисы:', components=[
        [Button(label='Disc', style=ButtonStyle.URL, url='https://www.google.com/intl/ru_ru/drive/',
                custom_id="button1"),
         Button(label='YouTube', style=ButtonStyle.URL, url='https://www.youtube.com/', custom_id="button2")]
    ])
    # Ожидание нажатия кнопки
    interaction = await bot.wait_for("Button_click", check=lambda i: i.custom_id == "button")
    await interaction.send(content="Button clicked!", ephemeral=False)


# Создание qr-кода с его последующим сохранением
@bot.command(pass_context=True)
async def qr(ctx, *, arg):
    # Запрос ссылки на создание
    qr_code.make_qr(arg)
    await ctx.send('Ваш qr code сформирован:', file=discord.File('qrcode.png'))


# Генератор паролей
@bot.command()
async def key(ctx):
    import uuid
    embed = discord.Embed(
        title=f'🔑 {uuid.uuid4()}')
    # Вывод ключа
    await ctx.send(embed=embed)


# Информация о ютубе
@bot.command(pass_context=True)
async def youtube(ctx):
    # Создание таблички с вводом данных
    embed = discord.Embed(color=discord.Color.red(), )
    embed.add_field(name='YouTube:',
                    value='{{play [ссылка]\n {{pause\n {{resume\n {{stop\n {{leave',
                    )
    embed.set_image(
        url='https://www.youtube.com/img/desktop/yt_1200.png')
    # Вывод данных
    await ctx.send(embed=embed)


# Включение трека
@bot.command()
async def play(ctx, url: str):
    # Куда скачивается файл
    song_there = os.path.isfile(".mp3")
    try:
        if song_there:
            os.remove(".mp3")
    except PermissionError:
        await ctx.send("Дождитесь окончания воиспроизведения текущей музыки или используйте команду {{stop.")
        return

    # Подключение к голосовому каналу
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name='Основной')
    await voice_channel.connect()
    await ctx.send('Подождите немного...')
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Необхолимые данные для скачивания трека
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    # Где находится скаченый трек
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, ".mp3")
    voice.play(discord.FFmpegPCMAudio(".mp3"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.10


# Пауза трека
@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Музыка на паузе.")
    else:
        await ctx.send("Ошибка паузы.")


# Продолжение трека
@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("Музыка продолжает проигрываться.")
    else:
        await ctx.send("Ошибка проигрыша.")


# Выключение трека
@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send("Музыка остановлена.")


# Выход из голосового канала
@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
        await ctx.send("Ghost 👻 отключен от голосового канала.")
    else:
        await ctx.send("Ошибка отключения")


# Игра
@bot.command(pass_context=True)
@commands.guild_only()
async def game(ctx):
    # Вывод сообщения
    await ctx.send(ctx.message.author.mention + 'Сыграем? 🪨 ✂ 🧻')

    wins = 0
    draws = 0
    losses = 0

    # Отборажение истории игр
    while True:
        await ctx.send('%s Победы, %s Ничьи, %s Поражения \n' % (wins, draws, losses))
        # Выбор слота
        while True:
            await ctx.send('Выбирай 🪨, ✂, 🧻 или ❌')
            player = await bot.wait_for('message')
            print(player)
            if player.content == '❌':
                await ctx.send('Уходишь ' + ctx.message.author.mention + '? Если захочешь снова сыграть пропиши {{game')
                return
            if player.content == '🪨' or player.content == '✂' or player.content == '🧻':
                break

        # Вывод слота против бота
        if player.content == '🪨':
            await ctx.send('🪨 \n vs.')
        elif player.content == '✂':
            await ctx.send('✂ \n vs.')
        elif player.content == '🧻':
            await ctx.send('🧻 \n vs.')

        # Выбор рандомного слота бота
        random_number = random.randint(1, 3)
        if random_number == 1:
            computer = '🪨'
            await ctx.send('🪨.')
        elif random_number == 2:
            computer = '✂'
            await ctx.send('✂.')
        elif random_number == 3:
            computer = '🧻'
            await ctx.send('🧻.')

        # Отображение Победы, Ничьи и Поражения. При различных случаях выбора слота
        if player.content == computer:
            await ctx.send('Единомышление 🤝🏻')
            draws = draws + 1
        elif player.content == '🪨' and computer == '✂':
            await ctx.send('Победа')
            wins = wins + 1
        elif player.content == '🪨' and computer == '🧻':
            await ctx.send('Доминация над человечеством 🦾')
            losses = losses + 1
        elif player.content == '🧻' and computer == '🪨':
            await ctx.send('Доминация над sky.net 💪🏻')
            wins = wins + 1
        elif player.content == '🧻' and computer == '✂':
            losses = losses + 1
            await ctx.send('Ты проиграл 🤖')
        elif player.content == '✂' and computer == '🧻':
            await ctx.send('С победой 🪙')
            wins = wins + 1
        elif player.content == '✂' and computer == '🪨':
            await ctx.send('Поражение 🗿')
            losses = losses + 1


# Функция random для вывода рандомного числа от 0 до 100
@bot.command(pass_context=True)
async def random(ctx):
    embed = discord.Embed(
        title=f'✅ Рандомное число - {randint(0, 1000000)}')
    # Вывод рандомного числа
    await ctx.send(embed=embed)


# Вывод команд используемых администратором
@bot.command(pass_context=True)
async def private(ctx):
    # Создание таблички
    embed = discord.Embed(title='Команды администратора:',
                          color=discord.Color.random(),
                          )
    embed.set_image(
        url='https://www.open-vision.ru/images/cover-02_1433258478-630x315.png.webp')
    embed.add_field(name='{{clear', value='💭➡️🗑️')
    embed.add_field(name='{{kick', value='Наказание')
    embed.add_field(name='{{ban', value='Черный список')
    embed.add_field(name='{{unban', value='Белый список')
    embed.add_field(name='{{off', value='Выключение бота')

    await ctx.send(embed=embed)


# Отчистка сообщений
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
# Ограничение роли
# amount=number ограгиченое количество при этом можно использовать просто {{clear
# amount: int неограниченое количество сколько просишь столько и отчистит
async def clear(ctx, amount: int):
    # Лимит удаляемых сообщений завасити от числа, которое мы задаем
    await ctx.channel.purge(limit=amount)


# Сообщение для пользователя о необходимости использования аргументов
@clear.error
async def clear_error(ctx, error):
    # Ошибка commands.MissingPermissions - появляется при недоси=таточном кол-ве прав у пользователя, который вызывает эту команду
    # Ошибка commands.MissingRequiredArgument - появляется, когда в методе вызова команды не нашелся аргумент
    if isinstance(error, commands.MissingPermissions):
        # Сообщение для пользователя что у него недостаточно прав
        await ctx.send(
            f'{ctx.author.mention}, у вас недостаточно прав для использования этой команды!')

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f'{ctx.author.mention}, вы забыли указать количество через пробел!')


# Кик пользователя
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    # Вывод информации о кикнутом пользователе
    embed = discord.Embed(title='Kick', colour=discord.Colour.dark_purple())
    await ctx.channel.purge(limit=1)
    await member.kick(reason=reason)
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name='Kick member', value='Наказан Пользователь : {}'.format(member.name))
    await ctx.send(embed=embed)


# Сообщение для пользователя о необходимости использования аргументов
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, обязательно укажите пользователя!')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав!')


# Бан пользователя
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    await member.ban(reason=reason)
    # Вывод информации о бане пользователя
    embed = discord.Embed(title='Информация о блокировке участника',
                          description=f'{member.mention}, был заблокирован в связи с нарушением правил',
                          color=discord.Color.dark_theme())

    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name=f'ID: {member.id}', value=f'Заблокированный участник : {member.name}')
    embed.set_footer(text='Был заблокирован администратором {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)


# Сообщение для пользователя о необходимости использования аргументов
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, укажите участника!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав!')


# Разбан пользователя
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit=1)

    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user

        await ctx.guild.unban(user)
        await ctx.send(f'Unbanned user {user.mention}')
        embed = discord.Embed(title='Информация о разблокировке участника',
                              description=f'{member.mention}, был разблокирован',
                              color=discord.Color.dark_theme())

        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.add_field(name=f'ID: {member.id}', value=f'Разблокированный участник : {member.name}')
        embed.set_footer(text='Был разблокирован администратором {}'.format(ctx.author.name),
                         icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        return


# Сообщение для пользователя о необходимости использования аргументов
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, укажите участника!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав!')


# Отправка сообщения через бота другому пользователю в личку или самому себе
@bot.command(pass_context=True)
async def send(ctx, member: discord.Member):
    await member.send(f' {member.mention}, будем на связи. '
                      f'Дай знать, если чем-то не понравился канал, вот контакт для связи AMRussia500@bk.ru '
                      f'от {ctx.author.mention}')


# Реакция бота на отключение людей
@bot.event
async def on_member_remove(member):
    message_channel = bot.get_channel(id_channel)
    await message_channel.send(f'{member.mention}, очень жаль, что вы уходите. '
                               f'Будем рады видеть вас снова на сервере {member.guild.name}')


# Асинхронный метод реализующий команду аварийной остановки бота
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def off(ctx):
    # Подтверждение что вышел из сети
    print('We have went out as {0.user}'.format(bot))
    await ctx.send('Ghost offline 😴')
    await exit()


# Сообщение для пользователя о необходимости использования аргументов
@off.error
async def off_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас недостаточно прав для использования этой команды !!!')


bot.run('OTIyMTE4MDY2MDIyNzc2ODky.Yb8zXw.Pu54FohetMwCLwbZLcaAKfqdATk')
