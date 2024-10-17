import sys  # Імпортуємо модуль sys для роботи з параметрами командного рядка та стандартним виводом

import file_processor  # Імпортуємо модуль для обробки файлів з даними
import randomizer  # Імпортуємо модуль для генерації випадкових даних (ймовірно, для тестування)

from genetic_algo import genetic_algorithm, TIMESLOTS  # Імпортуємо генетичний алгоритм та часові слоти з модуля genetic_algo


# Функція для виведення розкладу з додатковою інформацією
def print_schedule(schedule, lecturers, groups, auditoriums):
    schedule_dict = {}  # Створюємо словник для зберігання подій за часовими слотами
    for event in schedule.events:
        if event.timeslot not in schedule_dict:
            schedule_dict[event.timeslot] = []  # Ініціалізуємо список подій для нового часовго слота
        schedule_dict[event.timeslot].append(event)  # Додаємо подію до відповідного часовго слота

    # Словник для підрахунку годин викладачів
    lecturer_hours = {lecturer_id: 0 for lecturer_id in lecturers}

    for timeslot in TIMESLOTS:
        print(f"{timeslot}:")  # Виводимо часовий слот
        if timeslot in schedule_dict:
            for event in schedule_dict[timeslot]:
                # Формуємо інформацію про групи, включаючи підгрупи, якщо вони є
                group_info = ', '.join([
                    f"Group: {gid}" + (
                        f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else ''
                    )
                    for gid in event.group_ids
                ])
                # Обчислюємо кількість студентів у події
                total_students = sum(
                    groups[gid]['NumStudents'] // 2 if event.subgroup_ids and gid in event.subgroup_ids else
                    groups[gid]['NumStudents']
                    for gid in event.group_ids
                )
                # Отримуємо місткість аудиторії
                auditorium_capacity = auditoriums[event.auditorium_id]

                # Виводимо інформацію про подію: групи, предмет, тип заняття, викладача, аудиторію, кількість
                # студентів та місткість аудиторії
                print(f"  {group_info}, {event.subject_name} ({event.event_type}), "
                      f"Teacher: {lecturers[event.lecturer_id]['LecturerName']}, "
                      f"auditorium: {event.auditorium_id} "
                      f"(Students: {total_students}, Capacity: {auditorium_capacity})")

                # Додаємо 1.5 години до загальної кількості годин викладача
                lecturer_hours[event.lecturer_id] += 1.5
        else:
            print("  EMPTY")  # Якщо у цьому часовому слоті немає подій
        print()  # Додаємо порожній рядок для відділення часових слотів

    # Виводимо кількість годин викладачів на тиждень
    print("Кількість годин лекторів на тиждень:")
    for lecturer_id, hours in lecturer_hours.items():
        lecturer_name = lecturers[lecturer_id]['LecturerName']
        print(f"{lecturer_name} ({lecturer_id}): {hours} годин")


# Клас для дублювання стандартного виводу (stdout) у консоль та файл
class Tee(object):
    def __init__(self, *files):
        self.files = files  # Зберігаємо файли, куди будемо записувати вивід

    def write(self, obj):
        for f in self.files:
            f.write(obj)  # Записуємо об'єкт (текст) у всі файли

    def flush(self):
        for f in self.files:
            f.flush()  # Очищуємо буфери всіх файлів


def main():
    # Завантажуємо дані з CSV-файлів
    groups = file_processor.load_groups('datasource/groups.csv')  # Завантажуємо інформацію про групи
    subjects = file_processor.load_subjects('datasource/subjects.csv')  # Завантажуємо інформацію про предмети
    lecturers = file_processor.load_lecturers('datasource/lectures.csv')  # Завантажуємо інформацію про викладачів
    auditoriums = file_processor.load_auditoriums('datasource/auditoriums.csv')  # Завантажуємо інформацію про аудиторії

    # Запускаємо генетичний алгоритм для отримання найкращого розкладу
    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)

    # Виводимо розклад у консоль та записуємо його у файл
    with open('schedule_output.txt', 'w', encoding='utf-8') as f:
        original_stdout = sys.stdout  # Зберігаємо оригінальний stdout
        sys.stdout = Tee(sys.stdout, f)  # Перенаправляємо stdout на наш клас Tee, щоб дублювати вивід
        try:
            print("\nBest schedule:\n")
            print_schedule(best_schedule, lecturers, groups, auditoriums)  # Виводимо розклад
        finally:
            sys.stdout = original_stdout  # Відновлюємо оригінальний stdout


# Виконуємо основну функцію при запуску скрипта
if __name__ == "__main__":
    method = sys.argv[1]  # Зчитуємо параметр з командного рядка

    if method == 'FILE':
        main()  # Якщо параметр 'FILE', виконуємо основну функцію
    elif method == 'RANDOM':
        randomizer.main()  # Якщо параметр 'RANDOM', запускаємо функцію з модуля randomizer
    else:
        print("Invalid parameter!!!")  # Якщо параметр невідомий, виводимо повідомлення про помилку
