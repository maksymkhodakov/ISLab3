import random
from main import genetic_algorithm, print_schedule


# Функції для випадкової генерації даних
def generate_random_groups(num_groups):
    groups = {}
    for i in range(1, num_groups + 1):
        group_id = f"G{i}"
        num_students = random.randint(20, 35)
        subgroups = ['1', '2']
        groups[group_id] = {
            'NumStudents': num_students,
            'Subgroups': subgroups
        }
    return groups


def generate_random_subjects(groups, num_subjects_per_group):
    subjects = []
    subject_counter = 1
    for group_id in groups:
        for _ in range(num_subjects_per_group):
            subject_id = f"S{subject_counter}"
            subject_name = f"Предмет {subject_counter}"
            num_lectures = random.randint(10, 20)
            num_practicals = random.randint(10, 20)
            requires_subgroups = random.choice([True, False])
            week_type = random.choice(['Парний', 'Непарний', 'Both'])
            subjects.append({
                'SubjectID': subject_id,
                'SubjectName': subject_name,
                'GroupID': group_id,
                'NumLectures': num_lectures,
                'NumPracticals': num_practicals,
                'RequiresSubgroups': requires_subgroups,
                'WeekType': week_type
            })
            subject_counter += 1
    return subjects


def generate_random_lecturers(num_lecturers, subjects):
    lecturers = {}
    for i in range(1, num_lecturers + 1):
        lecturer_id = f"L{i}"
        lecturer_name = f"Викладач {i}"
        can_teach_subjects = random.sample(subjects, random.randint(1, min(5, len(subjects))))
        subjects_can_teach = [subj['SubjectID'] for subj in can_teach_subjects]
        types_can_teach = random.sample(['Лекція', 'Практика'], random.randint(1, 2))
        max_hours_per_week = random.randint(10, 20)
        lecturers[lecturer_id] = {
            'LecturerName': lecturer_name,
            'SubjectsCanTeach': subjects_can_teach,
            'TypesCanTeach': types_can_teach,
            'MaxHoursPerWeek': max_hours_per_week
        }
    return lecturers


def generate_random_auditoriums(num_auditoriums):
    auditoriums = {}
    for i in range(1, num_auditoriums + 1):
        auditorium_id = f"A{i}"
        capacity = random.randint(30, 50)
        auditoriums[auditorium_id] = capacity
    return auditoriums


def main():
    # Параметри для генерації даних
    num_groups = 5
    num_subjects_per_group = 3
    num_lecturers = 5
    num_auditoriums = 7

    # Генеруємо випадкові дані
    groups = generate_random_groups(num_groups)
    subjects = generate_random_subjects(groups, num_subjects_per_group)
    lecturers = generate_random_lecturers(num_lecturers, subjects)
    auditoriums = generate_random_auditoriums(num_auditoriums)

    # Запускаємо генетичний алгоритм
    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)
    print("\nBest schedule:\n")
    print_schedule(best_schedule, lecturers)
