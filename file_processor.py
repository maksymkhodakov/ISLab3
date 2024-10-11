import csv  # Імпортуємо модуль csv для роботи з CSV-файлами


# Функція для завантаження даних про аудиторії з файлу
def load_auditoriums(filename):
    auditoriums = {}  # Створюємо порожній словник для збереження інформації про аудиторії
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Створюємо об'єкт читання CSV-файлу як словників
        for row in reader:
            auditorium_id = row['auditoriumID']  # Зчитуємо ідентифікатор аудиторії
            auditoriums[auditorium_id] = int(row['capacity'])  # Зберігаємо місткість аудиторії
    return auditoriums  # Повертаємо словник з аудиторіями та їх місткістю


# Функція для завантаження даних про групи з файлу
def load_groups(filename):
    groups = {}  # Створюємо порожній словник для збереження інформації про групи
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Створюємо об'єкт читання CSV-файлу як словників
        for row in reader:
            group_id = row['groupNumber']  # Зчитуємо номер групи
            groups[group_id] = {
                'NumStudents': int(row['studentAmount']),  # Кількість студентів у групі
                'Subgroups': row['subgroups'].split(';') if row['subgroups'] else []  # Список підгруп, якщо вони є
            }
    return groups  # Повертаємо словник з інформацією про групи


# Функція для завантаження даних про дисципліни з файлу
def load_subjects(filename):
    subjects = []  # Створюємо порожній список для збереження дисциплін
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Створюємо об'єкт читання CSV-файлу як словників
        for row in reader:
            subjects.append({
                'SubjectID': row['id'],  # Ідентифікатор дисципліни
                'SubjectName': row['name'],  # Назва дисципліни
                'GroupID': row['groupID'],  # Номер групи, для якої призначена дисципліна
                'NumLectures': int(row['numLectures']),  # Кількість лекцій з дисципліни
                'NumPracticals': int(row['numPracticals']),  # Кількість практичних занять
                'RequiresSubgroups': row['requiresSubgroups'] == 'Yes',  # Чи потрібен поділ на підгрупи
                'WeekType': row['weekType'] if 'weekType' in row else 'Both'
                # Тип тижня ('Парний', 'Непарний' або 'Both')
            })
    return subjects  # Повертаємо список з інформацією про дисципліни


# Функція для завантаження даних про викладачів з файлу
def load_lecturers(filename):
    lecturers = {}  # Створюємо порожній словник для збереження інформації про викладачів
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Створюємо об'єкт читання CSV-файлу як словників
        for row in reader:
            lecturer_id = row['lecturerID']  # Зчитуємо ідентифікатор викладача
            lecturers[lecturer_id] = {
                'LecturerName': row['lecturerName'],  # Ім'я викладача
                'SubjectsCanTeach': row['subjectsCanTeach'].split(';'),  # Список дисциплін, які може викладати викладач
                'TypesCanTeach': row['typesCanTeach'].split(';'),
                # Типи занять (лекції, практики тощо), які може проводити
                'MaxHoursPerWeek': int(row['maxHoursPerWeek'])  # Максимальна кількість годин на тиждень для викладача
            }
    return lecturers  # Повертаємо словник з інформацією про викладачів
