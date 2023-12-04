from logger import logger
import multiprocessing
from job import Job, get_and_write_data, delete_file, copy_file


def coroutine(f):
    def wrap(*args, **kwargs):
        gen = f(*args, **kwargs)
        # Лучше использовать next(gen) вместо gen.send(None)
        # Это стандарт инициацилизации корутины
        next(gen)
        return gen

    return wrap


# Убрал наследование от object (устаревший прием)
class Scheduler:
    def __init__(self, max_working_time=1, tries=0, dependencies=None, start_at=None):
        # Убрал аннотацию list[Job], она не обязательна
        self.task_list = []
        self.start_at = start_at
        self.max_working_time = max_working_time
        self.tries = tries
        self.dependencies = dependencies if dependencies is not None else []

    # Заменил super().init() на обычные свойства
    # Так как Scheduler не наследует свойства от другого суперкласса

    @coroutine
    def schedule(self):
        processes = []
        while True:
            task_list = yield
            for task in task_list:
                logger.info(f"Планировщик: запускаю задачу - {task.name}")
                # Добавил запятые для создания кортежей
                p = multiprocessing.Process(target=task.run, args=(task.args,))
                p.start()
                processes.append(p)
            for process in processes:
                process.join()
                logger.info("Процесс остановлен!")

    def run(self, jobs: tuple):
        gen = self.schedule()
        gen.send(jobs)

if __name__ == "__main__":
    condition = multiprocessing.Condition()
    url = "https://official-joke-api.appspot.com/random_joke"

    job1 = Job(
        func=get_and_write_data,
        name="Запрос в сеть",
        args=(condition, url),
    )
    job2 = Job(
        func=delete_file,
        name="Удалить файл",
        args=(condition,),
    )
    job3 = Job(
        func=copy_file,
        name="Скопировать файл",
        args=(condition,),
    )

    # Переименовал g на scheduler для лучшей читаемости
    scheduler = Scheduler()
    scheduler.run((job1, job2, job3))
