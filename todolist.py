from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import task as Task


class Todo:
    menu = """1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add a task
6) Delete a task
0) Exit
"""
    database = 'todo.db'

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{Todo.database}?check_same_thread=False')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.query_task = self.session.query(Task)
        self.active = True

    def missed_tasks(self):
        today = datetime.today().date()
        missed = self.query_task.filter(Task.deadline < today).order_by(Task.deadline).all()
        if missed:
            for i, task in enumerate(missed, start=1):
                print(f'{i}. {task.task}. {self.format_day_month(task.deadline)}')
        else:
            print('All tasks have been completed!')

    def delete_task(self):
        print('Choose the number of the task you want to delete:')
        self.get_all_tasks()
        task_number = int(input())
        task = self.query_task.order_by(Task.deadline).all()[task_number - 1]
        self.session.delete(task)
        self.session.commit()
        print('The task has been deleted!')

    def get_all_tasks(self):
        all_tasks = self.query_task.order_by(Task.deadline).all()
        if all_tasks:
            for i, task in enumerate(all_tasks):
                print(f'{i + 1}. {task.task}. {self.format_day_month(task.deadline)}')
        else:
            print('Nothing to do!')
        print()

    def get_today_tasks(self):
        today = datetime.today().date()
        print(f'Today {today:%d %B}:')
        self.show_tasks_day(today)

    def get_week_tasks(self):
        today = datetime.today().date()
        for i in range(7):
            day = today + timedelta(days=i)
            print(f'{day:%A} {self.format_day_month(day)}:')
            self.show_tasks_day(day)
            print()

    def show_tasks_day(self, day):
        day_query = self.query_task.filter(Task.deadline == day).order_by(Task.deadline).all()
        if day_query:
            for i, task in enumerate(day_query):
                print(f'{i + 1}. {task.task}')
        else:
            print('Nothing to do!')

    def add_task(self):
        print()
        print('Enter a task')
        task_name = input()
        print('Enter a deadline')
        deadline_input = input()
        deadline_formatted = datetime.strptime(deadline_input, '%Y-%m-%d').date()

        new_task = Task(task=task_name, deadline=deadline_formatted)
        self.session.add(new_task)
        self.session.commit()
        print('The task has been added!')

    def show_menu(self):
        print(self.menu)

    def process_action(self, action):
        match action:
            case 1:
                self.get_today_tasks()
            case 2:
                self.get_week_tasks()
            case 3:
                self.get_all_tasks()
            case 4:
                self.missed_tasks()
            case 5:
                self.add_task()
            case 6:
                self.delete_task()
            case 0:
                self.active = False
                print('Bye!')
        print()

    @staticmethod
    def format_day_month(date):
        return f'{str(date.day)} {date.strftime("%b")}'


if __name__ == '__main__':
    todo_app = Todo()
    while True:
        todo_app.show_menu()
        action = int(input())
        todo_app.process_action(action)
        if not todo_app.active:
            break
