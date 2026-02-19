
# Класс "Задача"
class Task:
    def __init__(self, task_id, name, description, status, duration):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.status = status
        self.duration = duration

    # Геттеры и сеттеры для атрибутов задачи
    def get_task_id(self):
        return self.task_id

    def set_task_id(self, task_id):
        self.task_id = task_id

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.description

    def set_description(self, description):
        self.description = description

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration



# Класс "Проект"
class Project:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.get_task_id() != task_id]

    def get_all_tasks(self):
        return self.tasks

    # Итератор для перебора задач проекта
    def __iter__(self):
        return iter(self.tasks)


# Класс "Анализ"
class Analysis:
    @staticmethod
    def count_tasks(project):
        return len(project.get_all_tasks())

    @staticmethod
    def count_tasks_by_status(project, status):
        count = 0
        for task in project.get_all_tasks():
            if task.get_status() == status:
                count += 1
        return count

    @staticmethod
    def find_longest_task(project):
        longest_task = None
        max_duration = 0
        for task in project.get_all_tasks():
            if task.duration > max_duration:
                longest_task = task
                max_duration = task.duration
        return longest_task


class EnhancedAnalysis(Analysis):
    @staticmethod
    def find_tasks_with_keywords(project, keywords):
        found_tasks = []
        for task in project.get_all_tasks():
            for keyword in keywords:
                if keyword in task.get_name() or keyword in task.get_description():
                    found_tasks.append(task)
                    break
        return found_tasks


