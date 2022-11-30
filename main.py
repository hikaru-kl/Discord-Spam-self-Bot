import threading
import os
import requests
from art import *
from modules.panel import BotPanel

API = "https://discord.com/api/v9/"
accounts = 0
valid_tokens = []
bots = []


def start():
    global accounts
    global valid_tokens
    if not os.path.exists("tokens.txt"):
        open("tokens.txt", "w").close()
        print("! > Перед началом пользования, заполните файл tokens.txt")
        exit()
    with open("tokens.txt", "r") as f:
        tokens = [token.replace("\n", "") for token in f.readlines()]
    if len(tokens) < 1:
        print("! > Введите хотя бы 1 токен в файл tokens.txt")
        exit()
    text = ""
    invalid_tokens = []
    for token in tokens:
        data = requests.get(API + f"users/@me?token={token}").json()
        if "code" in data.keys():
            description = "Ошибка: " + data["message"] + " || invalid"
            invalid_tokens.append(token)
        else:
            description = data["username"] + " id: " + data["id"] + " || valid"
        text += f"{token} || {description}\n"
    if len(invalid_tokens) == len(tokens):
        print(f"Список токенов:\n{text}")
        print("! > Нет действительных токенов, выход из программы...")
        quit()
    print(text2art("DismgBot", font="small"))
    print(f"Список токенов:\n{text}\n\nВведите токен:")
    accounts = text
    valid_tokens = list(set(tokens) - set(invalid_tokens))
    while True:
        token = str(input(">>> "))
        if token not in tokens:
            print("? > Такого токена нет, выберите токен из списка")
        elif token in invalid_tokens:
            print(
                "? > Вы выбрали не действительный токен, пожалуйста, выберите рабочий токен")
        else:
            break
    return token


def get_guild(token: str):
    data = requests.get(API + f"users/@me/guilds?token={token}").json()
    ids = [str(id_["id"]) for id_ in data]
    text = ""

    for guild in data:
        text += "ID: {} | {}\n".format(guild["id"], guild["name"])
    print(f"{text}\n\nВведите ID сервера:")
    while True:
        id_ = str(input(">>> "))
        if id_ not in ids:
            print("? > Такого id нет")
            continue
        return data[ids.index(id_)]


def command_mode(token: str, guild: dict):
    print("""
Управление ботом:
    /add (Флаги: -text <текст сообщения> -i <путь до изображения> -t <время в секундах перед отправкой данного сообщения>) - добавить новое сообщение (обязателен флаг -i или -text и флаг -t)
    /times <разы> - количество раз, которое бот должен повторить цепь сообщений
    /channels - список каналов, доступных на данном сервере
    /phrases - выводит текущие фразы данного бота
    /next - перейти к настройке следующего бота
    /help - выводит это сообщение
""")
    while True:
        data = requests.get(API + f"users/@me?token={token}").json()
        console = BotPanel(token, guild)
        username = data["username"]
        id_ = data["id"]
        while True:
            response = console.get_command(
                str(input(f"\nБот: {username} | {id_}\n>>> ")))
            match response:
                case "STOP":
                    break
                case "NEW_MESSAGE":
                    print("► Новое сообщение успешно добавлено!")
                case "SET_TIMES":
                    print("► Количесвто итераций успешно установлено!")
                case "HELP":
                    continue
                case "START_MESSAGING":
                    bots.append(response)
                    return
                case _:
                    if isinstance(response, tuple):
                        if response[0] == "NEXT_BOT":
                            bots.append(response[1])
                            print(f"Бот #{len(bots)} сохранён!")
                            break
                    print("► Успешно!")

        print(accounts)
        print(f"{accounts}\n\nВведите токен:")
        while True:
            token = str(input(">>> "))
            if token not in valid_tokens:
                print("? > Такого токена нет, выберите токен из списка")
            else:
                break


def main():
    token = start()
    guild = get_guild(token)
    command_mode(token=token, guild=guild)


if __name__ == '__main__':
    main()
