import random
import copy

# Константи для розкладу

# Кількість днів у тижні (без врахування субот)
DAYS_PER_WEEK = 5

# Кількість академічних годин на день
LESSONS_PER_DAY = 4

# Типи тижнів: парний та непарний
WEEK_TYPE = ['EVEN', 'ODD']

# Загальна кількість академічних годин
TOTAL_LESSONS = DAYS_PER_WEEK * LESSONS_PER_DAY * len(WEEK_TYPE)

# Часові слоти з урахуванням парних/непарних тижнів
TIMESLOTS = [f"{week} - day {day + 1}, lesson {slot + 1}"
             for week in WEEK_TYPE
             for day in range(DAYS_PER_WEEK)
             for slot in range(LESSONS_PER_DAY)]


# Клас для представлення події розкладу
class Event:
    def __init__(self, timeslot, group_ids, subject_id, subject_name, lecturer_id, auditorium_id, event_type,
                 subgroup_ids=None, week_type='Both'):
        self.timeslot = timeslot
        self.group_ids = group_ids  # Список груп, які беруть участь у події
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.lecturer_id = lecturer_id
        self.auditorium_id = auditorium_id
        self.event_type = event_type  # Тип заняття (наприклад, лекція або практика)
        self.subgroup_ids = subgroup_ids  # Словник з підгрупами для груп
        self.week_type = week_type  # Тип тижня ('EVEN', 'ODD' або 'Both')


# Клас для представлення розкладу
class Schedule:
    def __init__(self):
        self.events = []  # Список подій у розкладі

    def add_event(self, event):
        if event:
            self.events.append(event)  # Додаємо подію до розкладу

    # Функція оцінки розкладу (функція оцінки №1)
    def fitness(self, groups, lecturers, auditoriums):
        hard_constraints_violations = 0  # Кількість порушень жорстких обмежень
        soft_constraints_score = 0  # Сума порушень м'яких обмежень

        lecturer_times = {}  # Словник зайнятих часових слотів викладачами
        group_times = {}  # Словник зайнятих часових слотів групами
        auditorium_times = {}  # Словник зайнятих аудиторій
        lecturer_hours = {}  # Словник кількості годин викладачів на тиждень

        for event in self.events:
            # Жорсткі обмеження

            # Перевірка зайнятості викладача у цей часовий слот
            lt_key = (event.lecturer_id, event.timeslot)
            if lt_key in lecturer_times:
                hard_constraints_violations += 1  # Викладач зайнятий у цей час
            else:
                lecturer_times[lt_key] = event

            # Перевірка зайнятості групи у цей часовий слот
            for group_id in event.group_ids:
                subgroup_id = event.subgroup_ids.get(group_id) if event.subgroup_ids else 'all'
                gt_key = (group_id, subgroup_id, event.timeslot)
                if gt_key in group_times:
                    hard_constraints_violations += 1  # Група або підгрупа зайнята у цей час
                else:
                    group_times[gt_key] = event

            # Перевірка зайнятості аудиторії у цей часовий слот
            at_key = (event.auditorium_id, event.timeslot)
            if at_key in auditorium_times:
                # Якщо це лекція і той самий викладач, дозволяємо об'єднати події
                existing_event = auditorium_times[at_key]
                if (event.event_type == 'Лекція' and
                        existing_event.event_type == 'Лекція' and
                        event.lecturer_id == existing_event.lecturer_id):
                    # Дозволено
                    pass
                else:
                    hard_constraints_violations += 1  # Аудиторія зайнята
            else:
                auditorium_times[at_key] = event

            # Перевірка максимального навантаження викладача на тиждень
            week = event.timeslot.split(', ')[0]
            lecturer_hours_key = (event.lecturer_id, week)
            lecturer_hours[lecturer_hours_key] = lecturer_hours.get(lecturer_hours_key, 0) + 1.5  # Додаємо 1.5 години
            if lecturer_hours[lecturer_hours_key] > lecturers[event.lecturer_id]['MaxHoursPerWeek']:
                hard_constraints_violations += 1  # Перевищено максимальне навантаження

            # М'які обмеження

            # Перевірка місткості аудиторії
            total_group_size = sum(
                groups[g]['NumStudents'] // 2 if event.subgroup_ids and event.subgroup_ids.get(g) else groups[g]['NumStudents']
                for g in event.group_ids)
            if auditoriums[event.auditorium_id] < total_group_size:
                soft_constraints_score += 1  # Аудиторія замала

            # Перевірка, чи викладач може викладати цей предмет
            if event.subject_id not in lecturers[event.lecturer_id]['SubjectsCanTeach']:
                soft_constraints_score += 1  # Викладач не може викладати цей предмет

            # Перевірка, чи викладач може проводити цей тип заняття
            if event.event_type not in lecturers[event.lecturer_id]['TypesCanTeach']:
                soft_constraints_score += 1  # Викладач не може проводити цей тип заняття

        # Функціонал якості №1: Мінімізуємо кількість порушень
        total_score = hard_constraints_violations * 1000 + soft_constraints_score  # Жорсткі обмеження важать більше
        return total_score

    # Альтернативна функція оцінки (функція оцінки №2)
    def fitness_alternative(self, groups, lecturers, auditoriums):
        # Враховуємо баланс навантаження викладачів та кількість "вікон" у розкладі
        total_penalty = self.fitness(groups, lecturers, auditoriums)  # Використовуємо першу функцію як основу

        # Додаємо м'яке обмеження на кількість "вікон" (перерв) у розкладі
        lecturer_windows = {}  # Словник для відстеження перерв у викладачів
        group_windows = {}  # Словник для відстеження перерв у груп

        for event in self.events:
            day_slot = event.timeslot.split(', ')
            day = day_slot[1]  # День
            slot = int(day_slot[2].split(' ')[1])  # Номер заняття
            week = day_slot[0]  # Тип тижня

            # Для викладачів
            lecturer_key = (event.lecturer_id, week)
            if lecturer_key not in lecturer_windows:
                lecturer_windows[lecturer_key] = {}
            if day not in lecturer_windows[lecturer_key]:
                lecturer_windows[lecturer_key][day] = []
            lecturer_windows[lecturer_key][day].append(slot)

            # Для груп
            for group_id in event.group_ids:
                subgroup_id = event.subgroup_ids.get(group_id) if event.subgroup_ids else 'all'
                group_key = (group_id, subgroup_id, week)
                if group_key not in group_windows:
                    group_windows[group_key] = {}
                if day not in group_windows[group_key]:
                    group_windows[group_key][day] = []
                group_windows[group_key][day].append(slot)

        # Підраховуємо кількість "вікон" для викладачів
        for lecturer, days in lecturer_windows.items():
            for slots in days.values():
                slots.sort()
                windows = sum(1 for i in range(len(slots) - 1) if slots[i + 1] - slots[i] > 1)
                total_penalty += windows

        # Підраховуємо кількість "вікон" для груп
        for group, days in group_windows.items():
            for slots in days.values():
                slots.sort()
                windows = sum(1 for i in range(len(slots) - 1) if slots[i + 1] - slots[i] > 1)
                total_penalty += windows

        return total_penalty


# Функція для генерації початкової популяції розкладів
def generate_initial_population(pop_size, groups, subjects, lecturers, auditoriums):
    population = []
    for _ in range(pop_size):
        schedule = Schedule()
        for subj in subjects:
            # Визначаємо, на які тижні проводиться предмет
            weeks = [subj['WeekType']] if subj['WeekType'] in WEEK_TYPE else WEEK_TYPE
            for week in weeks:
                # Додаємо лекції
                for _ in range(subj['NumLectures']):
                    event = create_random_event(subj, groups, lecturers, auditoriums, 'Лекція', week)
                    schedule.add_event(event)
                # Додаємо практичні/лабораторні заняття
                for _ in range(subj['NumPracticals']):
                    if subj['RequiresSubgroups']:
                        # Для кожної підгрупи створюємо окрему подію
                        for subgroup_id in groups[subj['GroupID']]['Subgroups']:
                            event = create_random_event(
                                subj, groups, lecturers, auditoriums, 'Практика', week,
                                {subj['GroupID']: subgroup_id})
                            schedule.add_event(event)
                    else:
                        event = create_random_event(subj, groups, lecturers, auditoriums, 'Практика', week)
                        schedule.add_event(event)
        population.append(schedule)  # Додаємо розклад до популяції
    return population


# Функція для створення випадкової події
def create_random_event(subj, groups, lecturers, auditoriums, event_type, week_type, subgroup_ids=None):
    # Вибираємо випадковий часовий слот для заданого типу тижня
    timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])
    # Знаходимо викладачів, які можуть викладати цей предмет і тип заняття
    suitable_lecturers = [lid for lid, l in lecturers.items()
                          if subj['SubjectID'] in l['SubjectsCanTeach'] and event_type in l['TypesCanTeach']]
    if not suitable_lecturers:
        return None  # Якщо немає підходящих викладачів, повертаємо None
    lecturer_id = random.choice(suitable_lecturers)  # Вибираємо випадкового викладача
    auditorium_id = random.choice(list(auditoriums.keys()))  # Вибираємо випадкову аудиторію
    group_ids = [subj['GroupID']]  # Отримуємо ідентифікатор групи
    return Event(timeslot, group_ids, subj['SubjectID'], subj['SubjectName'],
                 lecturer_id, auditorium_id, event_type, subgroup_ids, week_type)


# Функція для відбору найкращих розкладів у популяції
def select_population(population, groups, lecturers, auditoriums, fitness_function):
    population.sort(key=lambda x: fitness_function(x, groups, lecturers, auditoriums))  # Сортуємо за значенням функції оцінки
    return population[:len(population) // 2] if len(population) > 1 else population  # Повертаємо половину найкращих


# Реалізація "травоїдного" згладжування
def herbivore_smoothing(population, best_schedule, lecturers, auditoriums):
    # Додаємо невеликі випадкові варіації до найкращого розкладу
    new_population = []
    for _ in range(len(population)):
        new_schedule = copy.deepcopy(best_schedule)  # Копіюємо найкращий розклад
        mutate(new_schedule, lecturers, auditoriums, intensity=0.1)  # Виконуємо мутацію з низькою інтенсивністю
        new_population.append(new_schedule)
    return new_population


# Реалізація "хижака"
def predator_approach(population, groups, lecturers, auditoriums, fitness_function):
    # Видаляємо найгірші розклади, залишаючи лише найкращих
    population = select_population(population, groups, lecturers, auditoriums, fitness_function)
    return population


# Реалізація "дощу"
def rain(population_size, groups, subjects, lecturers, auditoriums):
    # Генеруємо нові випадкові розклади та додаємо їх до популяції
    new_population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    return new_population


# Нова нетривіальна мутація з використанням обміну подій
def mutate(schedule, lecturers, auditoriums, intensity=0.3):
    num_events_to_mutate = int(len(schedule.events) * intensity)
    # Забезпечуємо, що кількість подій для мутації є парною та не менше 2
    if num_events_to_mutate < 2:
        num_events_to_mutate = 2
    if num_events_to_mutate % 2 != 0:
        num_events_to_mutate += 1
    if num_events_to_mutate > len(schedule.events):
        num_events_to_mutate = len(schedule.events) - (len(schedule.events) % 2)

    events_to_mutate = random.sample(schedule.events, num_events_to_mutate)
    # Обмінюємо часові слоти між парами подій
    for i in range(0, len(events_to_mutate), 2):
        event1 = events_to_mutate[i]
        event2 = events_to_mutate[i + 1]

        # Зберігаємо початкові значення для перевірки обмежень
        original_timeslot1 = event1.timeslot
        original_timeslot2 = event2.timeslot
        original_auditorium1 = event1.auditorium_id
        original_auditorium2 = event2.auditorium_id
        original_lecturer1 = event1.lecturer_id
        original_lecturer2 = event2.lecturer_id

        # Виконуємо обмін часовими слотами
        event1.timeslot = original_timeslot2
        event2.timeslot = original_timeslot1

        # З випадковою ймовірністю обмінюємо аудиторії
        if random.random() < 0.5:
            event1.auditorium_id = original_auditorium2
            event2.auditorium_id = original_auditorium1

        # З випадковою ймовірністю обмінюємо викладачів
        if random.random() < 0.5:
            event1.lecturer_id = original_lecturer2
            event2.lecturer_id = original_lecturer1


# Генетичний алгоритм для оптимізації розкладу
def genetic_algorithm(groups, subjects, lecturers, auditoriums, generations=100):
    global best_schedule
    population_size = 50  # Фіксований розмір популяції
    population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    fitness_function = Schedule.fitness  # Використовуємо основну функцію оцінки

    for generation in range(generations):
        # Оцінка популяції та відбір найкращих
        population = select_population(population, groups, lecturers, auditoriums, fitness_function)
        if not population:
            print("Population is empty after the selection. Finishing the algorithm.")
            break
        best_schedule = population[0]
        best_fitness = fitness_function(best_schedule, groups, lecturers, auditoriums)
        print(f"Generation: {generation + 1}, Best fitness: {best_fitness}")

        # Якщо досягли оптимального розкладу
        if best_fitness == 0:
            break

        new_population = []

        # Реалізація "хижака"
        population = predator_approach(population, groups, lecturers, auditoriums, fitness_function)

        # Реалізація "травоїдного" згладжування
        smoothed_population = herbivore_smoothing(population, best_schedule, lecturers, auditoriums)

        # Реалізація "дощу"
        rain_population = rain(len(population), groups, subjects, lecturers, auditoriums)

        # Об'єднуємо всі популяції
        new_population.extend(population)
        new_population.extend(smoothed_population)
        new_population.extend(rain_population)

        # Мутація розкладів у новій популяції
        for schedule in new_population:
            if random.random() < 0.3:
                mutate(schedule, lecturers, auditoriums)

        # Зберігаємо стабільний розмір популяції
        population = new_population[:population_size]

    return best_schedule
