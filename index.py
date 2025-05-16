import hashlib
import json
import os
import getpass
from datetime import datetime

from cryptography.fernet import Fernet


# --- Инициализация шифрования ---
def crypto_init():
    """Инициализирует шифрование Fernet."""
    key_file_path = 'secret.key'
    if not os.path.exists(key_file_path):
        key = Fernet.generate_key()
        with open(key_file_path, 'wb') as key_file:
            key_file.write(key)

    try:
        with open(key_file_path, 'rb') as key_file:
            return Fernet(key_file.read())
    except IOError as e:
        print(f"Ошибка при чтении файла ключа: {e}")
        return None  # Или другое значение по умолчанию, чтобы указать на ошибку

cipher = crypto_init()

class EncryptionHelper:
    """Вспомогательный класс для шифрования и дешифрования данных."""

    @staticmethod
    def encrypt(data: str) -> bytes:
        """Шифрует строку с использованием Fernet."""
        if cipher:
            return cipher.encrypt(data.encode())
        else:
            print("Ошибка: Шифрование не инициализировано.")
            return data.encode() # Возвращаем незашифрованные данные (для отладки или обработки ошибок)

    @staticmethod
    def decrypt(encrypted_data: bytes) -> str:
        """Дешифрует зашифрованные данные с использованием Fernet."""
        if cipher:
            return cipher.decrypt(encrypted_data).decode()
        else:
            print("Ошибка: Шифрование не инициализировано.")
            return encrypted_data.decode() # Возвращаем зашифрованные данные (для отладки или обработки ошибок)

# --- Классы ---

class Person:
    """Базовый класс для представления человека (студента или преподавателя)."""

    def __init__(self, first_name: str, last_name: str, patronymic: str):
        self._first_name = EncryptionHelper.encrypt(first_name)
        self._last_name = EncryptionHelper.encrypt(last_name)
        self._patronymic = EncryptionHelper.encrypt(patronymic)

    @property
    def full_name(self) -> str:
        """Возвращает полное имя человека."""
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    @property
    def first_name(self) -> str:
        """Возвращает имя человека."""
        return EncryptionHelper.decrypt(self._first_name)

    @property
    def last_name(self) -> str:
        """Возвращает фамилию человека."""
        return EncryptionHelper.decrypt(self._last_name)

    @property
    def patronymic(self) -> str:
        """Возвращает отчество человека."""
        return EncryptionHelper.decrypt(self._patronymic)

    def get_fio(self) -> str:
        """Возвращает ФИО"""
        return self.full_name

class User:
    """Класс для представления пользователя с логином и паролем."""

    def __init__(self, login: str, password: str):
        """Инициализирует пользователя, хеширует пароль."""
        self.login = login
        self._salt = os.urandom(32)
        self._hashed_password = self._hash_password(password)

    def _hash_password(self, password: str) -> bytes:
        """Хеширует пароль с использованием PBKDF2."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            self._salt,
            100000
        )

    def check_password(self, password: str) -> bool:
        """Проверяет, соответствует ли введенный пароль хешированному паролю."""
        return self._hash_password(password) == self._hashed_password


class Student(Person, User):
    """Класс для представления студента."""

    def __init__(self, first_name: str, last_name: str, patronymic: str, login: str, password: str, serial_number: int = None):
        """Инициализирует студента."""
        Person.__init__(self, first_name, last_name, patronymic)
        User.__init__(self, login, password)
        self.serial_number = serial_number  # Порядковый номер

    def __repr__(self):
        return f"Student(serial_number={self.serial_number}, full_name='{self.full_name}')"

class Teacher(Person, User):
    """Класс для представления преподавателя."""

    def __init__(self, first_name: str, last_name: str, patronymic: str, login: str, password: str, salt: bytes = None, hashed_password: bytes = None):
        """Инициализирует преподавателя."""
        super().__init__(first_name, last_name, patronymic)
        User.__init__(self, login, password)
        if salt is not None:
            self._salt = salt
        if hashed_password is not None:
            self._hashed_password = hashed_password



class Subject:  # Исправлено: Теперь это класс верхнего уровня
    """Класс, представляющий учебный предмет."""
    def __init__(self, name: str):
        self.name = name
        self.pairs = []
        self.final_grades = {}  # {student_login: grade}

    def __repr__(self):
        return f"Subject(name='{self.name}')"

    def add_pair(self, pair):
        """Добавить пару к предмету"""
        self.pairs.append(pair)

    def calculate_final_grades(self):
        """Рассчитать итоговые оценки (заглушка)"""
        print(f"Расчет итоговых оценок для предмета {self.name} (пока не реализовано)")



class Pair:  # Исправлено: Теперь это класс верхнего уровня
    """Класс, представляющий пару (занятие) по предмету."""
    def __init__(self, date: datetime, topic: str, grades: dict = None, absentees: list = None):
        self.date = date
        self.topic = topic
        self.grades = grades if grades is not None else {}  # {student_login: grade}
        self.absentees = absentees if absentees is not None else []  # [student_login]

    def __repr__(self):
        return f"Pair(date={self.date.isoformat()}, topic='{self.topic}')"

    def get_absentees_list(self) -> list:
        """Получить список отсутствующих"""
        return self.absentees

    def do_roll_call(self):
        """Перекличка (заглушка)"""
        print(f"Проведение переклички на паре {self.date} по теме {self.topic} (пока не реализовано)")

    def set_grade(self, student_login: str, grade: int):
        """Поставить оценку студенту"""
        self.grades[student_login] = grade

    def display_pair_info(self):
        """Вывод информации о паре"""
        print(f"Дата: {self.date.isoformat()}, Тема: {self.topic}, Оценки: {self.grades}, Отсутствующие: {self.absentees}")

class SubjectPair:
    """Класс для представления связки "Предмет - Пара" """

    def __init__(self, teacher, academic_hours):
        self.teacher = teacher  # Преподаватель (объект класса Teacher)
        self.academic_hours = academic_hours

    def replace_teacher(self, new_teacher):
        self.teacher = new_teacher


class Journal:
    """Класс для управления журналом (список студентов, преподавателей, предметов)."""

    def __init__(self, group=None, course=None):
        """Инициализирует журнал, загружает данные."""
        self.students = []
        self.teachers = []
        self.subjects = []
        self.current_user = None
        self.group = group  # Группа
        self.course = course  # Курс

        self._load_teachers_data()  # Загрузка преподавателей из файла
        self._load_data() #Загружаем студентов


    def _load_teachers_data(self):
        """Загружает данные преподавателей из файла JSON."""
        try:
            with open('teachers_data.json', 'r') as f:
                data = json.load(f)

            self.teachers = []
            for t in data:
                teacher = Teacher(
                    first_name=EncryptionHelper.decrypt(t['data']['first_name'].encode()),
                    last_name=EncryptionHelper.decrypt(t['data']['last_name'].encode()),
                    patronymic=EncryptionHelper.decrypt(t['data']['patronymic'].encode()),
                    login=t['login'],
                    password='temp',  # Пароль не сохраняется в открытом виде
                    salt=bytes.fromhex(t['data']['salt']),
                    hashed_password=bytes.fromhex(t['data']['hashed_password'])
                )
                self.teachers.append(teacher)


        except (FileNotFoundError, json.JSONDecodeError):
            # Если файл не найден или поврежден, создаем пустой список
            self.teachers = []
            print("Файл teachers_data.json не найден или поврежден. Начинаем с пустого списка преподавателей.")
        except KeyError as e:
            print(f"Ошибка при чтении данных преподавателя: Отсутствует ключ {e}. Возможно, структура файла teachers_data.json устарела.")
        except Exception as e:
            print(f"Неожиданная ошибка при загрузке преподавателей: {e}")

    def _save_teachers_data(self):
        """Сохраняет данные преподавателей в файл JSON."""
        data = [
            {
                'login': t.login,
                'data': {
                    'first_name': t._first_name.decode(),
                    'last_name': t._last_name.decode(),
                    'patronymic': t._patronymic.decode(),
                    'salt': t._salt.hex(),
                    'hashed_password': t._hashed_password.hex()
                }
            } for t in self.teachers
        ]

        try:
            with open('teachers_data.json', 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка при сохранении данных преподавателей в файл: {e}")
        except TypeError as e:
            print(f"Ошибка при сериализации данных преподавателей в JSON: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка при сохранении преподавателей: {e}")


    def _auto_save(func):
        """Декоратор для автоматического сохранения данных после выполнения функции."""
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self._save_data()
            return result

        return wrapper

    def user_exists(self, login: str) -> bool:
        """Проверяет, существует ли пользователь с указанным логином."""
        return any(u.login == login for u in self.students + self.teachers)

    def teacher_exists(self, login: str) -> bool:
        """Проверяет, существует ли преподаватель с указанным логином."""
        return any(t.login == login for t in self.teachers)


    def register_teacher(self, user_data: dict):
      """Регистрирует нового преподавателя."""
      if self.teacher_exists(user_data['login']):
          raise ValueError("Преподаватель с таким логином уже существует!")

      new_teacher = Teacher(**user_data)
      self.teachers.append(new_teacher)
      self._save_teachers_data()

    def login(self, login: str, password: str) -> bool:
        """Выполняет вход пользователя."""
        for user in self.students + self.teachers:
            if user.login == login and user.check_password(password):
                self.current_user = user
                return True
        return False

    @_auto_save
    def add_student(self, student_data: dict):
        """Добавляет студента в журнал (только для преподавателей)."""
        if isinstance(self.current_user, Teacher):
            # Определяем порядковый номер
            serial_number = len(self.students) + 1

            new_student = Student(**student_data, serial_number=serial_number) # Передаем порядковый номер
            self.students.append(new_student)
            print(f"Студент {new_student.full_name} успешно добавлен! Порядковый номер: {serial_number}")
        else:
            print("Только преподаватели могут добавлять студентов.")

    @_auto_save
    def remove_student(self, student_login: str):
        """Удаляет студента из журнала (только для преподавателей)."""
        if isinstance(self.current_user, Teacher):
            student_to_remove = next((s for s in self.students if s.login == student_login), None)
            if student_to_remove:
                self.students.remove(student_to_remove)
                print(f"Студент {student_to_remove.full_name} успешно удален!")
            else:
                print("Студент с таким логином не найден!")
        else:
            print("Только преподаватели могут удалять студентов.")

    @_auto_save
    def add_subject(self, subject_name: str):
        """Добавляет предмет в журнал (только для преподавателей)."""
        if isinstance(self.current_user, Teacher):
            new_subject = Subject(subject_name)
            self.subjects.append(new_subject)
            print(f"Предмет {subject_name} добавлен!")
        else:
            print("Только преподаватели могут добавлять предметы.")

    @_auto_save
    def add_pair(self, subject_name: str, pair_data: dict):
        """Добавляет пару (занятие) к предмету (только для преподавателей)."""
        if isinstance(self.current_user, Teacher):
            subject = next((s for s in self.subjects if s.name == subject_name), None)
            if subject:
                try:
                    pair_data['date'] = datetime.fromisoformat(pair_data['date']) # Преобразование строки в datetime
                    new_pair = Pair(**pair_data)
                    subject.add_pair(new_pair)
                    print(f"Пара по {subject_name} добавлена!")
                except ValueError as e:
                    print(f"Ошибка при добавлении пары: Неверный формат даты.  Ожидается ISO формат (YYYY-MM-DDTHH:MM:SS).")

            else:
                print(f"Предмет {subject_name} не найден!")
        else:
            print("Только преподаватели могут добавлять пары.")

    @_auto_save
    def add_grade(self, student_login: str, subject_name: str, grade: int):
        """Добавляет оценку студенту по предмету (только для преподавателей)."""
        if isinstance(self.current_user, Teacher):
            student = next((s for s in self.students if s.login == student_login), None)
            subject = next((s for s in self.subjects if s.name == subject_name), None)

            if student and subject:
                # Найдем последнюю пару по предмету
                if subject.pairs:  # Если в предмете есть хоть какие-то пары
                   last_pair = subject.pairs[-1]
                   last_pair.set_grade(student_login, grade)
                   print(f"Оценка {grade} выставлена {student.full_name} по {subject_name}")

                else:
                    print("Сначала добавьте хотя бы одну пару по предмету!")
            else:
                print("Ошибка: студент или предмет не найдены!")
        else:
            print("Только преподаватели могут выставлять оценки.")

    def show_grades(self):
        """Показывает оценки текущего студента по всем предметам."""
        if isinstance(self.current_user, Student):
            grades = {}
            for subject in self.subjects:
                # Ищем последнюю пару по предмету и берем из нее оценку
                if subject.pairs:
                   last_pair = subject.pairs[-1]
                   grades[subject.name] = last_pair.grades.get(self.current_user.login, "Нет оценки") # оценка студента или "Нет оценки"
                else:
                    grades[subject.name] = "Нет пар" # Если нет пар по предмету
            return grades
        else:
            print("Только студенты могут просматривать свои оценки.")
            return {}

    def show_schedule(self):
        """Показывает расписание студента."""
        if isinstance(self.current_user, Student):
            schedule = {}
            for subject in self.subjects:
                schedule[subject.name] = []
                for pair in subject.pairs:
                    schedule[subject.name].append({
                        'date': pair.date.isoformat(),
                        'topic': pair.topic
                    })
            return schedule
        else:
            print("Только студенты могут просматривать расписание.")
            return {}

    def _save_data(self):
        """Сохраняет данные журнала в файл JSON."""
        data = {
            'group': self.group,
            'course': self.course,
            'students': [
                {
                    'login': s.login,
                    'data': {
                        'first_name': s._first_name.decode(),
                        'last_name': s._last_name.decode(),
                        'patronymic': s._patronymic.decode(),
                        'salt': s._salt.hex(),
                        'hashed_password': s._hashed_password.hex()
                    },
                    'serial_number': s.serial_number
                } for s in self.students
            ],
            'subjects': [
                {
                    'name': s.name,
                    'pairs': [
                        {
                            'date': p.date.isoformat(),
                            'topic': p.topic,
                            'grades': p.grades,
                            'absentees': p.absentees
                        } for p in s.pairs
                    ],
                    'final_grades': s.final_grades
                } for s in self.subjects
            ]
        }

        try:
            with open('journal_data.json', 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка при сохранении данных в файл: {e}")
        except TypeError as e:
            print(f"Ошибка при сериализации данных в JSON: {e}")


    def _load_data(self):
        """Загружает данные журнала из файла JSON."""
        try:
            with open('journal_data.json', 'r') as f:
                data = json.load(f)

            self.group = data.get('group')
            self.course = data.get('course')

            # Загрузка студентов
            self.students = []
            for s in data['students']:
                student = Student(
                    first_name=EncryptionHelper.decrypt(s['data']['first_name'].encode()),
                    last_name=EncryptionHelper.decrypt(s['data']['last_name'].encode()),
                    patronymic=EncryptionHelper.decrypt(s['data']['patronymic'].encode()),
                    login=s['login'],
                    password='temp',  # Пароль не сохраняется в открытом виде
                    serial_number=s.get('serial_number')

                )
                student._salt = bytes.fromhex(s['data']['salt'])
                student._hashed_password = bytes.fromhex(s['data']['hashed_password'])
                self.students.append(student)

            # Загрузка предметов
            self.subjects = []
            for subj in data['subjects']:
                subject = Subject(subj['name'])
                for p in subj['pairs']:
                    pair = Pair(
                        date=datetime.fromisoformat(p['date']),
                        topic=p['topic'],
                        grades=p.get('grades', {}),  # Используем .get(), чтобы избежать KeyError, если нет ключа
                        absentees=p.get('absentees', []) # Аналогично для absentees
                    )
                    subject.pairs.append(pair)
                subject.final_grades = subj['final_grades']
                self.subjects.append(subject)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка при загрузке данных из файла: {e}")
            # Если файл не найден или поврежден, создаем пустые списки
            self.students = []
            self.teachers = []
            self.subjects = []
        except KeyError as e:
            print(f"Ошибка при чтении данных: Отсутствует ключ {e}.  Возможно, структура файла journal_data.json устарела.")
        except ValueError as e:
            print(f"Ошибка при преобразовании данных: {e}")


# --- Функции пользовательского интерфейса ---
def main_menu():
    """Главное меню приложения."""
    # Добавляем ввод информации о группе и курсе при создании журнала
    group = input("Введите номер группы: ")
    course = input("Введите номер курса: ")
    journal = Journal(group=group, course=course)

    while True:
        print("\nГлавное меню:")
        print("1. Вход")
        print("2. Регистрация")
        print("3. Выход")
        choice = input("Выберите действие: ")

        if choice == '1':
            handle_login(journal)
        elif choice == '2':
            handle_registration(journal)
        elif choice == '3':
            break
        else:
            print("Некорректный выбор. Пожалуйста, выберите один из предложенных вариантов.")


def user_menu(journal):
    """Меню пользователя (студента или преподавателя)."""
    if isinstance(journal.current_user, Teacher):
        teacher_menu(journal)
    elif isinstance(journal.current_user, Student):
        student_menu(journal)
    else:
        print("Ошибка: Неизвестный тип пользователя.")


def handle_login(journal):
    """Обрабатывает процесс входа пользователя."""
    print("\nМеню входа:")
    print("1. Преподаватель")
    print("2. Студент")
    while True:
        role_choice = input("Выберите роль: ")

        if role_choice == '1' or role_choice == '2':
            break
        else:
            print("Некорректный ввод. Введите 1 или 2.")

    login = input("Логин: ")
    password = input("Пароль: ")  # Заменяем getpass.getpass() на input()

    if journal.login(login, password):
        user_type = 'teacher' if isinstance(journal.current_user, Teacher) else 'student'
        if (role_choice == '1' and user_type != 'teacher') or (role_choice == '2' and user_type != 'student'):
            print("Несоответствие выбранной роли!")
            journal.current_user = None  # Сбрасываем текущего пользователя
            return

        print(f"Добро пожаловать, {journal.current_user.full_name}!")
        user_menu(journal)
    else:
        print("Неверный логин или пароль!")


def handle_registration(journal):
    """Обрабатывает процесс регистрации пользователя."""
    print("\nМеню регистрации:")
    print("1. Преподаватель")
    print("2. Студент")

    while True:
        role_choice = input("Выберите роль (1 или 2): ")
        if role_choice in ('1', '2'):
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 1 или 2.")


    try:
        user_data = {
            'first_name': input("Имя: "),
            'last_name': input("Фамилия: "),
            'patronymic': input("Отчество: "),
            'login': input("Логин: "),
            'password': input("Пароль: ")  # Заменяем getpass.getpass() на input()
        }

        if role_choice == '1':  # Преподаватель
            try:
                journal.register_teacher(user_data)
                print("Преподаватель успешно зарегистрирован!")
            except ValueError as e:
                print(f"Ошибка регистрации преподавателя: {e}")


        elif role_choice == '2': #Студент
            try:
                journal.register_user('student', user_data)
                print("Студент успешно зарегистрирован!")
            except ValueError as e:
                print(f"Ошибка регистрации студента: {e}")

        else:
            print("Некорректный выбор!")

    except ValueError as e:
        print(f"Ошибка: {str(e)}")  # Выводим сообщение об ошибке, если логин уже существует
    except Exception as e:
        print(f"Произошла неожиданная ошибка: {e}")  # Ловим все остальные исключения

def teacher_menu(journal):
    """Меню преподавателя."""
    while True:
        print("\nМеню преподавателя:")
        print("1. Добавить студента")
        print("2. Удалить студента")
        print("3. Добавить предмет")
        print("4. Добавить пару к предмету")
        print("5. Выставить оценку студенту")
        print("6. Вывести информацию о группе")
        print("7. Переключить предмет и пару")
        print("8. Выйти")
        choice = input("Выберите действие: ")

        if choice == '1':
            student_data = {
                'first_name': input("Имя: "),
                'last_name': input("Фамилия: "),
                'patronymic': input("Отчество: "),
                'login': input("Логин: "),
                'password': input("Пароль: ")
            }
            journal.add_student(student_data)
        elif choice == '2':
            student_login = input("Введите логин студента для удаления: ")
            journal.remove_student(student_login)

        elif choice == '3':
            subject_name = input("Название предмета: ")
            journal.add_subject(subject_name)
        elif choice == '4':
            subject_name = input("Название предмета: ")
            pair_data = {
                'date': input("Дата и время (YYYY-MM-DDTHH:MM:SS): "),
                'topic': input("Тема занятия: ")
            }
            journal.add_pair(subject_name, pair_data)
        elif choice == '5':
            student_login = input("Логин студента: ")
            subject_name = input("Название предмета: ")
            try:
                grade = int(input("Оценка: "))
                journal.add_grade(student_login, subject_name, grade)
            except ValueError:
                print("Ошибка: Некорректный ввод оценки. Оценка должна быть числом.")
        elif choice == '6':
            print(f"Группа: {journal.group}, Курс: {journal.course}")

            print("\nСписок студентов в группе:")
            for student in journal.students:
                print(student)

            print("\nСписок предметов:")
            for subject in journal.subjects:
                print(subject)

        elif choice == '7':  # Добавлено для вызова "Переключить предмет и пару"

            subject_name = input("Введите название предмета: ")

            subject = next((s for s in journal.subjects if s.name == subject_name), None)

            if not subject:
                print("Предмет с таким названием не найден!")
                continue

            if not subject.pairs:
                print("В данном предмете нет ни одной пары!")
                continue

            print("Доступные пары:")

            for i, p in enumerate(subject.pairs):
                print(f"{i + 1}. {p.date} - {p.topic}")

            while True:

                try:
                    pair_number = int(input("Введите номер пары, чтобы её переключить: ")) - 1
                    if 0 <= pair_number < len(subject.pairs):
                        selected_pair = subject.pairs[pair_number]
                        break
                    else:
                        print("Некорректный номер пары. Попробуйте еще раз.")
                except ValueError:
                    print("Некорректный ввод. Введите номер пары.")
            selected_pair.display_pair_info()

        elif choice == '8':
            break
        else:
            print("Некорректный выбор.")

def student_menu(journal):
    """Меню студента."""
    while True:
        print("\nМеню студента:")
        print("1. Посмотреть оценки")
        print("2. Посмотреть расписание")
        print("3. Посмотреть информацию о группе")
        print("4. Выйти")
        choice = input("Выберите действие: ")

        if choice == '1':
            grades = journal.show_grades()
            if grades:
                for subject, grade in grades.items():
                    print(f"{subject}: {grade if grade != 'Нет оценки' else 'Нет оценки'}")
            else:
                print("У вас пока нет оценок.")
        elif choice == '2':
            schedule = journal.show_schedule()
            if schedule:
                for subject, pairs in schedule.items():
                    print(f"\n{subject}:")
                    if pairs:
                        for pair in pairs:
                            print(f"  - {pair['date']} : {pair['topic']}")
                    else:
                        print("  Нет занятий.")
            else:
                print("У вас нет расписания.")
        elif choice == '3':
            print(f"Группа: {journal.group}, Курс: {journal.course}")
        elif choice == '4':
            break
        else:
            print("Некорректный выбор.")

# --- Запуск приложения ---
if __name__ == "__main__":
    main_menu()