import random
from copy import deepcopy
from dataclasses import dataclass


# -------------- define dataclasses ----------------------

@dataclass
class Teacher:
    name: str
    max_hours: int
    classes: list


@dataclass
class Group:
    id: str
    hours: list
    teachers: list


# -------------- create groups, students, and teachers --------------

# hours and teachers go in order: [english, history, math, science, literature, arts]
groups_hours = {
    "1A": [2, 5, 2, 0, 6, 3],
    "1B": [4, 2, 0, 0, 3, 3],
    "1C": [2, 0, 2, 3, 2, 2],
    "1D": [0, 0, 2, 5, 0, 1],
}

groups_students = {
    "1A": 28,
    "1B": 22,
    "1C": 30,
    "1D": 18,
}

teachers = [
    Teacher("bob", 7, ["english", "history"]),
    Teacher("alice", 7, ["english", "history", "arts"]),
    Teacher("victor", 5, ["math", "science"]),
    Teacher("jane", 11, ["arts", "literature"]),
    Teacher("james", 7, ["literature"]),
    Teacher("john", 8, ["english"]),
    Teacher("sarah", 4, ["math", "science"]),
    Teacher("mike", 14, ["math"]),
    Teacher("sam", 4, ["science"]),
]

auditoriums = {
    "A1": 30,
    "A2": 25,
    "A3": 35,
    "A4": 20,
}

# ----------- create helpful data structures -------------

subjects_raw = ["english", "history", "math", "science", "literature", "arts"]
subjects2teachers = {}

for subject in subjects_raw:
    subjects2teachers[subject] = []
    for teacher in teachers:
        if subject in teacher.classes:
            subjects2teachers[subject].append(teacher.name)


# ----------- helper functions for constraints -------------

def is_teacher_available(teacher, subject_index, schedule):
    """
    Перевіряє, чи викладач доступний на цей період часу для цієї групи.
    """
    for group_schedule in schedule:
        if group_schedule[subject_index] == teacher:
            return False
    return True


def is_classroom_suitable(group_id, auditorium):
    """
    Перевіряє, чи вистачає місць в аудиторії для групи.
    """
    if groups_students[group_id] > auditoriums[auditorium]:
        return False
    return True


def evaluate_windows(schedule):
    """
    Оцінює кількість "вікон" у розкладі викладачів і груп.
    """
    windows_penalty = 0
    # Тут можна додати логіку для підрахунку "вікон"
    return windows_penalty


# -------------- scheduling functions --------------------

def create_schedule(max_attempts=100):
    schedule = []
    for group_id in groups_hours:
        teachers_for_group = []
        for subject_index, subject in enumerate(subjects_raw):
            subject_teachers = subjects2teachers[subject]
            available_teachers = [
                teacher for teacher in subject_teachers
                if is_teacher_available(teacher, subject_index, schedule)
            ]
            if not available_teachers:
                # Не знайдено доступного викладача, додаємо випадкового викладача (можна змінити логіку)
                print(
                    f"Warning: No available teachers for subject '{subject}' in group '{group_id}' at time slot {subject_index}. Assigning randomly.")
                teacher = random.choice(subject_teachers)
            else:
                teacher = random.choice(available_teachers)
            teachers_for_group.append(teacher)
        schedule.append(teachers_for_group)
    return schedule


def evaluate(schedule):
    teacher_hours = {teacher.name: teacher.max_hours for teacher in teachers}
    score = 0
    for i, group_id in enumerate(groups_hours):
        group = Group(group_id, groups_hours[group_id], schedule[i])
        for group_teacher, hours in zip(group.teachers, group.hours):
            if hours > teacher_hours[group_teacher]:
                score += teacher_hours[group_teacher]
                teacher_hours[group_teacher] = 0
            else:
                score += hours
                teacher_hours[group_teacher] -= hours

    # Враховуємо штраф за "вікна"
    score -= evaluate_windows(schedule)

    return score


def create_population(population_size=16):
    population = []
    for _ in range(population_size):
        schedule = create_schedule()
        population.append(schedule)
    return population


def competition(population):
    new_population = []
    # Парування сусідніх індивідів
    for i in range(0, len(population) - 1, 2):
        schedule1 = population[i]
        schedule2 = population[i + 1]
        score1 = evaluate(schedule1)
        score2 = evaluate(schedule2)
        if score1 > score2:
            new_population.append(schedule1)
        else:
            new_population.append(schedule2)
    return new_population


def crossover(population):
    schedule_half = len(population[0]) // 2
    offspring = []
    for i in range(0, len(population) - 1, 2):
        schedule1 = population[i]
        schedule2 = population[i + 1]
        child1 = schedule1[:schedule_half] + schedule2[schedule_half:]
        child2 = schedule2[:schedule_half] + schedule1[schedule_half:]
        offspring.append(child1)
        offspring.append(child2)
    population.extend(offspring)
    return population


def mutation(population, mutation_rate=0.3):  # Збільшено ймовірність мутацій
    local_population = deepcopy(population)
    for schedule in local_population:
        for group_id, group in zip(groups_hours.keys(), schedule):
            for i in range(len(group)):
                if random.random() < mutation_rate:
                    subject = subjects_raw[i]
                    subject_teachers = subjects2teachers[subject]
                    available_teachers = [
                        teacher for teacher in subject_teachers
                        if is_teacher_available(teacher, i, schedule)
                    ]
                    if available_teachers:
                        new_teacher = random.choice(available_teachers)
                    else:
                        # Якщо немає доступних викладачів, залишаємо поточного
                        new_teacher = group[i]
                    group[i] = new_teacher  # Змінюємо викладача в групі
    return local_population


def generic_step(population):
    local_best_score, local_average, local_best_schedule = evaluate_population(population)
    print(f"Generation step - Best score: {local_best_score}, Average score: {local_average}")
    population = competition(population)
    population = crossover(population)
    population = mutation(population, 0.3)  # Збільшена ймовірність мутації
    # Додаємо найкращий розклад назад до популяції
    if local_best_schedule not in population:
        population.append(local_best_schedule)
    return population


def genetic_algorithm(population_size, generations):
    population = create_population(population_size)
    for generation in range(generations):
        print(f"Generation: {generation + 1}")
        population = generic_step(population)
    return population


def get_max_score():
    max_score = 0
    for hours in groups_hours.values():
        for hour in hours:
            max_score += hour
    return max_score


def evaluate_population(population):
    scores = []
    for schedule in population:
        scores.append(evaluate(schedule))
    max_score = max(scores)
    average_score = sum(scores) / len(scores)
    best_schedule = population[scores.index(max_score)]
    return max_score, average_score, best_schedule


def print_schedule(schedule):
    for i, group_id in enumerate(groups_hours):
        group = Group(group_id, groups_hours[group_id], schedule[i])
        print(f"group {group.id}:")
        for subj, teacher in zip(subjects_raw, group.teachers):
            print(f"\t{subj}: {teacher}")


# -------------- main code ----------------------

if __name__ == '__main__':
    print(f"best possible score: {get_max_score()}")

    # Генетичний алгоритм
    population_test = genetic_algorithm(128, 100)

    # Створення початкової популяції
    population_simple = create_population(128)

    # Оцінка популяції після генетичного алгоритму
    best_score, average_score, best_schedule = evaluate_population(population_test)

    # Оцінка початкової популяції
    best_score_simple, average_score_simple, best_schedule_simple = evaluate_population(population_simple)

    # Виведення результату
    print("-----best schedule from genetic algorithm-----")
    print_schedule(best_schedule)

    print("-----genetic algorithm-----")
    print(f"@@@@ average score: {average_score}")
    print(f"@@@@ best score: {best_score}")

    print("-----simple population-----")
    print(f"@@@@ average score: {average_score_simple}")
    print(f"@@@@ best score: {best_score_simple}")
