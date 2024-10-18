import random  # Імпортуємо модуль random для генерації випадкових чисел
from main import genetic_algorithm, print_schedule  # Імпортуємо генетичний алгоритм та функцію для виведення розкладу


# Функції для випадкової генерації даних
def generate_random_groups(num_groups):
    groups = {}  # Створюємо порожній словник для груп
    for i in range(1, num_groups + 1):
        group_id = f"G{i}"  # Створюємо ідентифікатор групи (наприклад, 'G1')
        num_students = random.randint(20, 35)  # Випадкова кількість студентів у групі від 20 до 35
        # Генеруємо підгрупи: мінімум 2 підгрупи для кожної групи
        num_subgroups = 2  # Створюємо 2 підгрупи (можна змінити на рандомну кількість)
        subgroups = [f"{j}" for j in range(1, num_subgroups + 1)]  # Наприклад, ['1', '2']
        groups[group_id] = {
            'NumStudents': num_students,  # Кількість студентів
            'Subgroups': subgroups  # Список підгруп
        }
    return groups  # Повертаємо словник з групами


# Функція для генерації випадкових предметів для кожної групи
def generate_random_subjects(groups, num_subjects_per_group):
    subjects = []  # Створюємо порожній список для предметів
    subject_counter = 1  # Лічильник для унікальних ідентифікаторів предметів
    for group_id in groups:
        for _ in range(num_subjects_per_group):
            subject_id = f"S{subject_counter}"  # Створюємо ідентифікатор предмета (наприклад, 'S1')
            subject_name = f"Предмет {subject_counter}"  # Назва предмета
            num_lectures = random.randint(10, 20)  # Випадкова кількість лекцій від 10 до 20
            num_practicals = random.randint(10, 20)  # Випадкова кількість практичних занять від 10 до 20
            requires_subgroups = random.choice([True, False])  # Випадково визначаємо, чи потрібні підгрупи
            week_type = random.choice(['EVEN', 'ODD', 'Both'])  # Випадково вибираємо тип тижня
            subjects.append({
                'SubjectID': subject_id,  # Ідентифікатор предмета
                'SubjectName': subject_name,  # Назва предмета
                'GroupID': group_id,  # Група, для якої призначений предмет
                'NumLectures': num_lectures,  # Кількість лекцій
                'NumPracticals': num_practicals,  # Кількість практичних занять
                'RequiresSubgroups': requires_subgroups,  # Чи потрібен поділ на підгрупи
                'WeekType': week_type  # Тип тижня: 'EVEN', 'ODD' або 'Both'
            })
            subject_counter += 1  # Збільшуємо лічильник предметів
    return subjects  # Повертаємо список предметів


# Функція для генерації випадкових викладачів
def generate_random_lecturers(num_lecturers, subjects):
    lecturers = {}  # Створюємо порожній словник для викладачів
    for i in range(1, num_lecturers + 1):
        lecturer_id = f"L{i}"  # Створюємо ідентифікатор викладача (наприклад, 'L1')
        lecturer_name = f"Викладач {i}"  # Ім'я викладача
        # Випадково вибираємо предмети, які викладач може викладати (від 1 до 5 предметів)
        can_teach_subjects = random.sample(subjects, random.randint(1, min(5, len(subjects))))
        subjects_can_teach = [subj['SubjectID'] for subj in can_teach_subjects]  # Отримуємо ідентифікатори цих предметів
        # Випадково вибираємо типи занять, які викладач може проводити ('Лекція', 'Практика' або обидва)
        types_can_teach = random.sample(['Лекція', 'Практика'], random.randint(1, 2))
        max_hours_per_week = random.randint(10, 20)  # Випадкова максимальна кількість годин на тиждень
        lecturers[lecturer_id] = {
            'LecturerName': lecturer_name,  # Ім'я викладача
            'SubjectsCanTeach': subjects_can_teach,  # Список предметів, які може викладати
            'TypesCanTeach': types_can_teach,  # Типи занять, які може проводити
            'MaxHoursPerWeek': max_hours_per_week  # Максимальна кількість годин на тиждень
        }
    return lecturers  # Повертаємо словник викладачів


# Функція для генерації випадкових аудиторій
def generate_random_auditoriums(num_auditoriums):
    auditoriums = {}  # Створюємо порожній словник для аудиторій
    for i in range(1, num_auditoriums + 1):
        auditorium_id = f"A{i}"  # Створюємо ідентифікатор аудиторії (наприклад, 'A1')
        capacity = random.randint(30, 50)  # Випадкова місткість аудиторії від 30 до 50
        auditoriums[auditorium_id] = capacity  # Зберігаємо місткість аудиторії
    return auditoriums  # Повертаємо словник аудиторій


# Головна функція для запуску генерації даних та алгоритму
def main():
    # Параметри для генерації даних
    num_groups = 5  # Кількість груп
    num_subjects_per_group = 3  # Кількість предметів на групу
    num_lecturers = 5  # Кількість викладачів
    num_auditoriums = 7  # Кількість аудиторій

    # Генеруємо випадкові дані
    groups = generate_random_groups(num_groups)  # Генеруємо групи
    subjects = generate_random_subjects(groups, num_subjects_per_group)  # Генеруємо предмети
    lecturers = generate_random_lecturers(num_lecturers, subjects)  # Генеруємо викладачів
    auditoriums = generate_random_auditoriums(num_auditoriums)  # Генеруємо аудиторії

    # Запускаємо генетичний алгоритм для створення розкладу
    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)
    print("\nBest schedule:\n")
    print_schedule(best_schedule, lecturers, groups, auditoriums)  # Виводимо найкращий знайдений розклад
