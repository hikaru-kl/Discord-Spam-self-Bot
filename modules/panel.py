import argparse
import os
from typing import List
import requests

ALLOWED_COMMANDS = ["/add", "/times",
                    "/phrases", "/next", "/help", "/channels"]
ALLOWED_MEDIA = ["png", "jpeg", "webm", "gif"]


class BotPanel:
    def __init__(self, token, guild: int) -> None:
        print(guild)
        self.token = token
        self.messages: List[BotMessage] = []
        self.times = 1
        self.time = 3
        self.guild = guild
        print(f"https://discord.com/api/v9/guilds/{guild}?token={token}")
        self.channels = requests.get(
            "https://discord.com/api/v9/guilds/{}/channels?token={}".format(self.guild["id"], token)).json()
        self.channels_ids = [data["id"]
                             for data in self.channels if data["type"] != 4 and data["type"] != 2]

    def get_command(self, command: str):
        command = command.split(" ")
        if command[0] not in ALLOWED_COMMANDS:
            print(
                f"\n! > Команда {command[0]} не найдена! Введите /help для списка команд\n")
            return "HELP"
        match command[0]:
            case "/add":
                del command[0]
                parser = argparse.ArgumentParser()
                parser.add_argument(
                    "-text", "-txt", dest="text", nargs='+', default=None)
                parser.add_argument("-img", "-i", "-media",
                                    "-image", dest="image_path", nargs='+', default=None)
                parser.add_argument("-t", "-time", dest="time", default=None)
                parser.add_argument("-c", "-channel", "-id",
                                    dest="channel", default=None)
                parser.add_argument(
                    "--place", dest="place", default=None)
                parser.add_argument(
                    "--edit", dest="edit", default=None)
                args = parser.parse_args(command)

                if (args.place is not None) and (args.edit is not None):
                    print(
                        "! > Одновременно флаг --place и флаг --edit не могут быть использованы!")
                    return "HELP"
                if args.channel is None:
                    print(
                        "! > Вы не указали id канала, куда будет отправлено сообщение")
                    return "HELP"
                else:
                    if args.channel.isdigit() is False:
                        print(f"! > `{args.channel}` - не является id канала")
                        return "HELP"

                    else:
                        if int(args.channel) not in self.channels_ids:
                            print(
                                f"! > id `{args.channel}` нет в списке каналов, пропишите /channels для вывода списка")
                            return "HELP"

                if args.text is None and args.image_path is None:
                    print("! > Вы должна указать -text или -i")
                if args.time is None:
                    print(
                        "! > Вы не указали время перед отправкой сообщения, установлено по умолчанию: 3 секунды")
                if args.place is not None:
                    if not args.place.isdigit():
                        print(
                            "! > Номер сообщения для вставки должен быть целочисленным и неотрицательным")
                        return "HELP"
                    else:
                        if len(self.messages) < 1:
                            print(
                                "! > На данный момент нет сообщений, команда добавит ваше сообщение, как новое")
                            args.place = 1
                        args.place = int(args.place) - 1
                        if args.place < 0:
                            print(
                                f"! > Номер сообщения для вставки число от 1 до {len(self.messages)}")
                            return "HELP"
                    return self.set_message(args)
                elif args.edit is not None:
                    if not args.edit.isdigit():
                        print(
                            "! > Номер сообщения для редактирования должен быть целочисленным и неотрицательным")
                        return "HELP"
                    else:
                        if len(self.messages) < 1:
                            print(
                                "! > На данный момент нет сообщений для редактирования")
                            return "HELP"
                        args.edit = int(args.edit) - 1
                        if args.edit < 0:
                            print(
                                f"! > Номер сообщения для редактирования число от 1 до {len(self.messages)}")
                            return "HELP"
                    return self.edit_message(args)
                else:
                    return self.add_message(args)

            case "/channels":
                return self.show_channels()

            case "/times":
                if len(command) < 2:
                    print(
                        "! > Вы не указали колличество циклов, которое бот будет повторять свои фразы, установлено 1")
                    times = self.times
                else:
                    if not command[1].isdigit():
                        print(
                            f"! > `{command[1]}` - не является целочисленным числом, установлен 1 раз")
                        times = self.times
                    else:
                        times = int(command[1])
                return self.set_times(times)

            case "/phrases":
                return self.show_messages()

            case "/next":
                return self.next_panel()

            case "/help":
                return self.show_help()

            case "/start":
                return "START_MESSAGING"

            case _:
                return self.show_help()

    def edit_message(self, args):
        text, media_path, time, channel_id = generate_message(args)
        self.messages[args.edit] = BotMessage(
            text, media_path, time, channel_id)

    def set_message(self, args):
        text, media_path, time, channel_id = generate_message(args)
        self.messages.insert(args.place, BotMessage(
            text, media_path, time, channel_id))

    def add_message(self, args):
        text, media_path, time, channel_id = generate_message(args)
        self.messages.append(BotMessage(text, media_path, time, channel_id))
        return "NEW_MESSAGE"

    def set_times(self, times: int):
        self.times = times
        print(f"► Текущее число циклов -> {times}")
        return "HELP"

    def show_messages(self):
        if self.messages == []:
            print("! > У данного бота нет сообщений")
            return "HELP"
        result = ""
        counter = 0
        for message in self.messages:
            counter += 1
            text = message.text if message.text is not None else "отсутствует"
            media = " ;\n".join(
                message.media) if message.media is not None else "отсвутствуют"
            channel = message.channel_id
            result += f"\n• #{counter} Сообщение\nТекст: {text}\nИзображения: {media}\nКанал: {channel}\nВремя перед отправкой: {message.text}\n\n"
        print(f"{result}Всего сообщений: {counter}")
        return "HELP"

    def show_channels(self):
        name = self.guild["name"]
        result = f"Текстовые каналы сервера {name}:"
        for channel in self.channels:
            if channel["type"] != 4 and channel["type"] != 2:
                result += "\n• {} | ID: {}".format(
                    channel["name"], channel["id"])
        print(
            f"? > При выборе канала для отправки сообщений, пожалуйста, убедитесь, что у бота есть права отправлять сообщения в этот канал!\n{result}")
        return "HELP"

    def next_panel(self):
        return ("NEXT_BOT", self)

    def show_help(self, command: str = None):
        if command is None:
            print("""
Управление ботом:
    /add (Флаги: --text <текст сообщения> --i <путь до изображения> --t <время в секундах перед отправкой данного сообщения>) - добавить новое сообщение (обязателен флаг --i или --text и флаг --t)
    /times <разы> - количество раз, которое бот должен повторить цепь сообщений
    /phrases - выводит текущие фразы данного бота
    /next - перейти к настройке следующего бота
    /help - выводит это сообщение
""")
        else:
            if command not in ALLOWED_COMMANDS:
                print(
                    f"! > Команда {command} не найдена! Введите /help для списка команд\n")
        return "HELP"


class BotMessage:
    def __init__(self, text: str | None, media_path: str | None | List[str], time: float, channel_id: int) -> None:
        self.text = text
        self.media = media_path
        self.time = time
        self.channel_id = channel_id


def generate_message(args):
    text = " ".join(args.text) if args.text is not None else None
    media_path = args.image_path
    if media_path is not None:
        result_path = []
        for media in media_path:
            if not os.path.exists(media):
                print(
                    f"! > Путь `{media}` не существует, игнорирование пути")
            else:
                if (media.endswith(ext) for ext in ALLOWED_MEDIA):
                    print(
                        f"! > Путь `{media}` является не поддерживаемым форматом, поддерживаемые форматы:\npng, jpeg, webm, gif")
                else:
                    result_path.append(media)
    else:
        result_path = None
    if args.time is None:
        args.time = 3
    else:
        if args.time.isdigit():
            args.time = float(args.time)
            if args.time < 3:
                print(
                    "! > Вы указали задержку меньше 3 секунд, установлено 3 секунды"),
                args.time = 3
            elif args.time > 9999:
                print(
                    "! > Вы указали задержку больше 9999 секунд, установлено 3 секунды")
                args.time = 3
    return text, result_path, args.time, args.channel
