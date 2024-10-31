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


class Schedule:
    def __init__(self):
        self.events = []  # Список подій у розкладі
        self.hard_constraints_violations = 0  # Ініціалізація для жорстких обмежень
        self.soft_constraints_score = 0       # Ініціалізація для м'яких обмежень

    def add_event(self, event):
        if event:
            self.events.append(event)  # Додаємо подію до розкладу

    # Функція оцінки розкладу
    def fitness(self, groups, lecturers, auditoriums):
        self.hard_constraints_violations = 0  # Скидаємо лічильник порушень
        self.soft_constraints_score = 0       # Скидаємо лічильник м'яких обмежень

        lecturer_times = {}
        group_times = {}
        subgroup_times = {}
        auditorium_times = {}
        lecturer_hours = {}

        for event in self.events:
            # Жорсткі обмеження
            lt_key = (event.lecturer_id, event.timeslot)
            if lt_key in lecturer_times:
                self.hard_constraints_violations += 1  # Викладач зайнятий на іншому занятті
            else:
                lecturer_times[lt_key] = event

            for group_id in event.group_ids:
                gt_key = (group_id, event.timeslot)
                if gt_key in group_times:
                    self.hard_constraints_violations += 1  # Група зайнята на іншому занятті
                else:
                    group_times[gt_key] = event

                if event.subgroup_ids and group_id in event.subgroup_ids:
                    subgroup_id = event.subgroup_ids[group_id]
                    sgt_key = (group_id, subgroup_id, event.timeslot)
                    if sgt_key in subgroup_times:
                        self.hard_constraints_violations += 1  # Підгрупа зайнята на іншому занятті
                    else:
                        subgroup_times[sgt_key] = event

            at_key = (event.auditorium_id, event.timeslot)
            if at_key in auditorium_times:
                existing_event = auditorium_times[at_key]
                if (event.event_type == 'Лекція' and
                        existing_event.event_type == 'Лекція' and
                        event.lecturer_id == existing_event.lecturer_id):
                    pass
                else:
                    self.hard_constraints_violations += 1  # Аудиторія зайнята
            else:
                auditorium_times[at_key] = event

            week = event.timeslot.split(' - ')[0]
            lecturer_hours_key = (event.lecturer_id, week)
            lecturer_hours[lecturer_hours_key] = lecturer_hours.get(lecturer_hours_key, 0) + 1.5
            if lecturer_hours[lecturer_hours_key] > lecturers[event.lecturer_id]['MaxHoursPerWeek']:
                self.hard_constraints_violations += 1  # Перевищено навантаження

            # М'які обмеження
            total_group_size = sum(
                groups[g]['NumStudents'] // 2 if event.subgroup_ids and event.subgroup_ids.get(g) else groups[g][
                    'NumStudents']
                for g in event.group_ids)
            if auditoriums[event.auditorium_id] < total_group_size:
                self.soft_constraints_score += 1  # Аудиторія замала

            if event.subject_id not in lecturers[event.lecturer_id]['SubjectsCanTeach']:
                self.soft_constraints_score += 1  # Викладач не може викладати цей предмет

            if event.event_type not in lecturers[event.lecturer_id]['TypesCanTeach']:
                self.soft_constraints_score += 1  # Викладач не може проводити цей тип заняття

        total_score = self.hard_constraints_violations * 1000 + self.soft_constraints_score
        return total_score  # Повертаємо загальне значення обмежень


# Функція для генерації початкової популяції розкладів
def generate_initial_population(pop_size, groups, subjects, lecturers, auditoriums):
    population = []
    for _ in range(pop_size):
        lecturer_times = {}  # Словник для зберігання зайнятих часових слотів викладачами
        group_times = {}  # Словник для зберігання зайнятих часових слотів групами
        subgroup_times = {}  # Словник для зберігання зайнятості підгруп
        auditorium_times = {}  # Словник для зберігання зайнятих аудиторій
        schedule = Schedule()

        for subj in subjects:
            weeks = [subj['WeekType']] if subj['WeekType'] in WEEK_TYPE else WEEK_TYPE
            for week in weeks:
                # Додаємо лекції
                for _ in range(subj['NumLectures']):
                    event = create_random_event(
                        subj, groups, lecturers, auditoriums, 'Лекція', week,
                        lecturer_times, group_times, subgroup_times, auditorium_times
                    )
                    if event:
                        schedule.add_event(event)

                # Додаємо практичні/лабораторні заняття
                for _ in range(subj['NumPracticals']):
                    if subj['RequiresSubgroups']:
                        # Для кожної підгрупи створюємо окрему подію
                        for subgroup_id in groups[subj['GroupID']]['Subgroups']:
                            subgroup_ids = {subj['GroupID']: subgroup_id}
                            event = create_random_event(
                                subj, groups, lecturers, auditoriums, 'Практика', week,
                                lecturer_times, group_times, subgroup_times, auditorium_times, subgroup_ids
                            )
                            if event:
                                schedule.add_event(event)
                    else:
                        event = create_random_event(
                            subj, groups, lecturers, auditoriums, 'Практика', week,
                            lecturer_times, group_times, subgroup_times, auditorium_times
                        )
                        if event:
                            schedule.add_event(event)

        population.append(schedule)  # Додаємо розклад до популяції

    return population


def create_random_event(
        subj, groups, lecturers, auditoriums, event_type, week_type,
        lecturer_times, group_times, subgroup_times, auditorium_times, subgroup_ids=None
):
    # Вибираємо випадковий часовий слот для заданого типу тижня
    global lecturer_key
    timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])

    # Знаходимо викладачів, які можуть викладати цей предмет і тип заняття
    suitable_lecturers = [
        lid for lid, l in lecturers.items()
        if subj['SubjectID'] in l['SubjectsCanTeach'] and event_type in l['TypesCanTeach']
    ]
    if not suitable_lecturers:
        return None  # Немає підходящих викладачів

    # Вибираємо випадкового викладача, який не зайнятий у цей часовий слот
    random.shuffle(suitable_lecturers)
    lecturer_id = None
    for lid in suitable_lecturers:
        lecturer_key = (lid, timeslot)
        if lecturer_key not in lecturer_times:
            lecturer_id = lid
            break
    if not lecturer_id:
        return None  # Всі викладачі зайняті

    # Вибір груп
    if event_type == 'Лекція':
        # Вибираємо від 1 до 3 груп, які не зайняті в цей часовий слот
        available_groups = [gid for gid in groups if (gid, timeslot) not in group_times]
        if not available_groups:
            return None  # Немає доступних груп
        num_groups = random.randint(1, min(3, len(available_groups)))
        group_ids = random.sample(available_groups, num_groups)
    else:
        group_ids = [subj['GroupID']]
        # Перевірка зайнятості групи
        if (group_ids[0], timeslot) in group_times:
            return None  # Група зайнята

    # Перевірка зайнятості груп
    for group_id in group_ids:
        group_key = (group_id, timeslot)
        if group_key in group_times:
            return None  # Група зайнята у цей часовий слот

    # Перевірка зайнятості підгруп
    if event_type == 'Практика' and subj['RequiresSubgroups']:
        if subgroup_ids is None:
            subgroup_ids = {}
            for group_id in group_ids:
                subgroup_ids[group_id] = random.choice(groups[group_id]['Subgroups'])
        for group_id, subgroup_id in subgroup_ids.items():
            subgroup_key = (group_id, subgroup_id, timeslot)
            if subgroup_key in subgroup_times:
                return None  # Підгрупа зайнята у цей часовий слот
    else:
        subgroup_ids = None  # Якщо підгрупи не потрібні, встановлюємо None

    # Вибір аудиторії з підходящою місткістю
    total_group_size = sum(
        groups[g]['NumStudents'] // 2 if subgroup_ids and g in subgroup_ids else groups[g]['NumStudents']
        for g in group_ids
    )
    suitable_auditoriums = [
        (aid, cap) for aid, cap in auditoriums.items() if cap >= total_group_size
    ]
    if not suitable_auditoriums:
        return None  # Немає аудиторій з достатньою місткістю

    # Випадковим чином обираємо аудиторію з доступних
    random.shuffle(suitable_auditoriums)
    auditorium_id = None
    for aid, cap in suitable_auditoriums:
        auditorium_key = (aid, timeslot)
        if auditorium_key not in auditorium_times:
            auditorium_id = aid
            break
    if not auditorium_id:
        return None  # Всі аудиторії зайняті

    event = Event(
        timeslot, group_ids, subj['SubjectID'], subj['SubjectName'],
        lecturer_id, auditorium_id, event_type, subgroup_ids, week_type
    )

    # Реєструємо зайнятість викладача, груп, підгруп та аудиторії
    lecturer_times[lecturer_key] = event
    for group_id in group_ids:
        group_key = (group_id, timeslot)
        group_times[group_key] = event
        if event_type == 'Практика' and subgroup_ids and group_id in subgroup_ids:
            subgroup_id = subgroup_ids[group_id]
            subgroup_key = (group_id, subgroup_id, timeslot)
            subgroup_times[subgroup_key] = event
    auditorium_times[(auditorium_id, timeslot)] = event

    return event


# Функція для відбору найкращих розкладів у популяції
def select_population(population, groups, lecturers, auditoriums, fitness_function):
    population.sort(
        key=lambda x: fitness_function(x, groups, lecturers, auditoriums))  # Сортуємо за значенням функції оцінки
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

        # Перевіряємо, чи можна обміняти події без порушення жорстких обмежень
        if can_swap_events(event1, event2):
            # Виконуємо обмін часовими слотами
            event1.timeslot, event2.timeslot = event2.timeslot, event1.timeslot

            # З випадковою ймовірністю обмінюємо аудиторії, тільки якщо це дозволено
            if random.random() < 0.5 and can_swap_auditoriums(event1, event2):
                event1.auditorium_id, event2.auditorium_id = event2.auditorium_id, event1.auditorium_id

            # З випадковою ймовірністю обмінюємо викладачів, тільки якщо це дозволено
            if random.random() < 0.5 and can_swap_lecturers(event1, event2):
                event1.lecturer_id, event2.lecturer_id = event2.lecturer_id, event1.lecturer_id


# Функція для перевірки можливості обміну подіями
def can_swap_events(event1, event2):
    # Обмін можливий, якщо не порушуються жорсткі обмеження
    # Забороняємо обмін, якщо це призведе до того, що одна група матиме лекцію і практику одночасно
    group_conflict = any(
        g in event2.group_ids for g in event1.group_ids) and event1.event_type != event2.event_type
    return not group_conflict


# Функція для перевірки можливості обміну аудиторіями
def can_swap_auditoriums(event1, event2):
    return event1.auditorium_id != event2.auditorium_id


# Функція для перевірки можливості обміну викладачами
def can_swap_lecturers(event1, event2):
    return event1.lecturer_id != event2.lecturer_id


# Функція для оцінки м'яких обмежень
def soft_constraints_fitness(schedule):
    return schedule.soft_constraints_score


# Функція для оцінки жорстких обмежень
def hard_constraints_fitness(schedule):
    return schedule.hard_constraints_violations


# Функція для відбору популяції
def select_from_population(population, fitness_function):
    population.sort(key=fitness_function)  # Сортуємо за значенням функції оцінки
    return population[:len(population) // 2] if len(population) > 1 else population  # Повертаємо половину найкращих


# Функція для вибору N найкращих розкладів у популяції
def select_top_n(population, fitness_function, n):
    population.sort(key=fitness_function)
    return population[:n]


# Функція для схрещування двох розкладів
def crossover(parent1, parent2):
    # Створюємо копію батьківських розкладів
    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
    crossover_point = len(parent1.events) // 2

    # Обмінюємо події на основі точки схрещування
    child1.events[crossover_point:], child2.events[crossover_point:] = parent2.events[crossover_point:], parent1.events[
                                                                                                         crossover_point:]
    return child1, child2


# Генетичний алгоритм з схрещуванням та вибором кількох елементів
def genetic_algorithm(groups, subjects, lecturers, auditoriums, generations=100):
    global best_schedule
    population_size = 50
    n_best_to_select = 10  # Кількість найкращих розкладів, що обираються для наступного покоління
    population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)

    # Етап 1: Жорсткі обмеження
    for generation in range(generations):
        population = select_top_n(population, lambda sched: sched.hard_constraints_violations, n_best_to_select)

        # Перевірка, чи знайдено розклад без порушень жорстких обмежень
        if population[0].hard_constraints_violations == 0:
            best_schedule = population[0]
            print(f"Покоління: {generation + 1}, Найкращий розклад для жорстких обмежень знайдено.")
            break
        else:
            best_schedule = population[0]

        # Схрещування між вибраними найкращими розкладами
        new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        # Мутація нової популяції
        for schedule in new_population:
            if random.random() < 0.3:
                mutate(schedule, lecturers, auditoriums)

        population = new_population

    # Етап 2: Оптимізація м'яких обмежень, зберігаючи жорсткі
    for generation in range(generations):
        population = select_top_n(population, lambda sched: sched.soft_constraints_score, n_best_to_select)
        best_schedule = population[0]
        best_fitness = best_schedule.soft_constraints_score

        print(f"Покоління: {generation + 1}, Оптимізація м'яких обмежень, поточна найкраща оцінка: {best_fitness}")

        if best_fitness == 0:
            break

        # Схрещування для оптимізації м'яких обмежень
        new_population = []
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([child1, child2])

        # Мутація нової популяції
        for schedule in new_population:
            if random.random() < 0.3:
                mutate(schedule, lecturers, auditoriums)

        population = new_population

    return best_schedule
