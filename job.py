from logger import logger
from urllib.request import urlopen
from pathlib import Path
import ssl
import json
import shutil


def get_and_write_data(condition, url):
    context = ssl._create_unverified_context()
    file = "punchline.txt"
    with condition:
        with urlopen(url, context=context) as req:
            # Переставил проверку статуса ответа до его чтения
            if req.status != 200:
                raise Exception(
                    "Error during execute request. {}: {}".format(
                        req.status, req.reason
                    )
                )
            resp = req.read().decode("utf-8")
            # Убрал лишнее присваивание, данные записываются в переменную data
            # А читаемые данные записываются в переменную resp
            data = json.loads(resp)
        if isinstance(data, dict):
            path = Path(file)
            setup = data["setup"]
            punchline = data["punchline"]
            print(f"Setup: {setup} n" f"Punchline: {punchline}")
            with open(path, mode="a") as config:
                # Стоит использовать json.dump() вместо str(data)
                # Чтобы данные правильно перевелись в формат JSON
                json.dump(data, config)
        else:
            logger.error(type(data))
            logger.error(ValueError)
            raise ValueError


def copy_file(condition, x=None):
    file = "punchline.txt"
    to_path = "./jokes/"
    with condition:
        # Здесь нужно быть аккуратным, так как предполагается, что эта функция
        # вызывается в многопоточной среде и использует примитив Condition
        # для синхронизации
        # Если примитив не используется, то wait() стоит убрать
        condition.wait(timeout=1)
        try:
            shutil.copy(file, to_path)
            # Добавил лог о успешном копировании
            # Чтобы все важные действия были залогированы
            logger.info("Файл скопирован")
        except FileNotFoundError as ex:
            logger.error("Файл не найден %s", ex)


def delete_file(condition, x=None):
    file = "punchline.txt"
    obj = Path(file)
    with condition:
        # Здесь нужно быть аккуратным, так как предполагается, что эта функция
        # вызывается в многопоточной среде и использует примитив Condition
        # для синхронизации
        # Если примитив не используется, то wait() стоит убрать
        condition.wait(timeout=1)
        try:
            # Нужно проверять существует ли файл перед попыткой его удаления
            if obj.exists():
                obj.unlink()
                logger.info(f"Удалил файл {file}")
            else:
                # Добавил лог о том, что файла не существует
                logger.info(f"Файл {file} не существует")
        except FileNotFoundError as ex:
            logger.error(ex)


class Job:
    def __init__(self, func=None, name=None, args=None):
        # Здесь аргументы должны быть кортежем, если не предоставлены
        # Так как предполагается использование тех аргументов,
        # которые передаем при инициализации экземляров
        self.args = args if args is not None else ()
        self.name = name
        self.func = func

    def run(self):
        if self.func is not None:
            tar = self.func(*self.args)
            logger.info("тип объекта в Job.run %s", type(tar))
            logger.debug("запуск объекта %s", tar)
        else:
            raise ValueError("Func attribute not set in Job")
