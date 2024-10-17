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
                gt_key = (group_id, event.timeslot)

                # Перевірка: група не може одночасно мати лекцію і практику
                if gt_key in group_times:
                    previous_event = group_times[gt_key]
                    if previous_event.event_type != event.event_type:
                        hard_constraints_violations += 1  # Група не може мати лекцію та практику одночасно
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
                    # Дозволено проводити лекції декільком групам одночасно в одній аудиторії
                    pass
                else:
                    hard_constraints_violations += 1  # Аудиторія зайнята для іншого типу заняття
            else:
                auditorium_times[at_key] = event

            # Перевірка максимального навантаження викладача на тиждень
            week = event.timeslot.split(', ')[0]
            lecturer_hours_key = (event.lecturer_id, week)
            lecturer_hours[lecturer_hours_key] = lecturer_hours.get(lecturer_hours_key, 0) + 1.5  # Додаємо 1.5 години
            if lecturer_hours[lecturer_hours_key] > lecturers[event.lecturer_id]['MaxHoursPerWeek']:
                # Порушення: Перевищено максимальне навантаження
                exceeded_hours = lecturer_hours[lecturer_hours_key] - lecturers[event.lecturer_id]['MaxHoursPerWeek']
                hard_constraints_violations += exceeded_hours * 10  # Множник можна налаштувати для більш суворого штрафу

            # М'які обмеження

            # Перевірка місткості аудиторії
            total_group_size = sum(
                groups[g]['NumStudents'] // 2 if event.subgroup_ids and event.subgroup_ids.get(g) else groups[g][
                    'NumStudents']
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


# Функція для генерації початкової популяції розкладів
def generate_initial_population(pop_size, groups, subjects, lecturers, auditoriums):
    population = []

    for _ in range(pop_size):
        lecturer_times = {}  # Словник для зберігання зайнятих часових слотів викладачами
        group_times = {}  # Словник для зберігання зайнятих часових слотів групами
        schedule = Schedule()

        for subj in subjects:
            # Визначаємо, на які тижні проводиться предмет
            weeks = [subj['WeekType']] if subj['WeekType'] in WEEK_TYPE else WEEK_TYPE
            for week in weeks:
                # Додаємо лекції
                for _ in range(subj['NumLectures']):
                    event = create_random_event(subj, groups, lecturers, auditoriums, 'Лекція', week, lecturer_times,
                                                group_times)
                    if event:
                        schedule.add_event(event)

                # Додаємо практичні/лабораторні заняття
                for _ in range(subj['NumPracticals']):
                    if subj['RequiresSubgroups']:
                        # Для кожної підгрупи створюємо окрему подію
                        for subgroup_id in groups[subj['GroupID']]['Subgroups']:
                            event = create_random_event(subj, groups, lecturers, auditoriums, 'Практика', week,
                                                        lecturer_times, group_times,
                                                        {subj['GroupID']: subgroup_id})
                            if event:
                                schedule.add_event(event)
                    else:
                        event = create_random_event(subj, groups, lecturers, auditoriums, 'Практика', week,
                                                    lecturer_times, group_times)
                        if event:
                            schedule.add_event(event)

        population.append(schedule)  # Додаємо розклад до популяції

    return population


def create_random_event(subj, groups, lecturers, auditoriums, event_type, week_type, lecturer_times, group_times, subgroup_ids=None):
    # Вибираємо випадковий часовий слот для заданого типу тижня
    global lecturer_key
    timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])

    # Знаходимо викладачів, які можуть викладати цей предмет і тип заняття
    suitable_lecturers = [lid for lid, l in lecturers.items()
                          if subj['SubjectID'] in l['SubjectsCanTeach'] and event_type in l['TypesCanTeach']]
    if not suitable_lecturers:
        return None  # Якщо немає підходящих викладачів, повертаємо None

    # Вибираємо випадкового викладача, перевіряючи, чи він вільний у цей часовий слот
    random.shuffle(suitable_lecturers)
    lecturer_id = None
    for lid in suitable_lecturers:
        lecturer_key = (lid, timeslot)
        if lecturer_key not in lecturer_times:  # Перевірка на зайнятість викладача
            lecturer_id = lid
            break

    if not lecturer_id:
        return None  # Якщо всі викладачі зайняті у цей часовий слот, повертаємо None

    # Якщо це лекція, можемо об'єднати кілька груп
    if event_type == 'Лекція':
        group_ids = random.sample(groups.keys(), random.randint(1, 3))  # Вибираємо випадково до 3 груп
    else:
        group_ids = [subj['GroupID']]  # Для практики або лабораторних це одна група або її підгрупа

    # Перевірка зайнятості групи у цей часовий слот
    for group_id in group_ids:
        group_key = (group_id, timeslot)
        if group_key in group_times:  # Якщо група вже зайнята у цей час
            return None  # Повертаємо None, бо група не може бути на декількох заняттях одночасно

    # Якщо це практика, перевіряємо підгрупу
    if event_type == 'Практика':
        # Якщо вже є підгрупи, перевіряємо, чи зайнята підгрупа
        if subgroup_ids is None:
            subgroup_ids = {group_id: random.choice(groups[group_id]['Subgroups']) for group_id in group_ids}

        # Перевірка зайнятості підгруп
        for group_id, subgroup_id in subgroup_ids.items():
            subgroup_key = (group_id, subgroup_id, timeslot)
            if subgroup_key in group_times:  # Якщо підгрупа вже зайнята у цей час
                return None  # Повертаємо None, бо підгрупа не може бути на декількох заняттях одночасно

    # Вибираємо аудиторію, яка має достатню місткість для всіх груп
    total_group_size = sum(groups[g]['NumStudents'] for g in group_ids)
    suitable_auditoriums = [aid for aid, cap in auditoriums.items()
                            if cap >= total_group_size]
    if not suitable_auditoriums:
        return None  # Немає аудиторій з достатньою місткістю
    auditorium_id = random.choice(suitable_auditoriums)  # Вибираємо випадкову аудиторію з достатньою місткістю

    event = Event(timeslot, group_ids, subj['SubjectID'], subj['SubjectName'],
                  lecturer_id, auditorium_id, event_type, subgroup_ids, week_type)

    # Заносимо викладача і групу в зайнятість на цей часовий слот
    lecturer_times[lecturer_key] = event
    for group_id in group_ids:
        group_key = (group_id, timeslot)
        group_times[group_key] = event

        # Заносимо зайнятість підгруп
        if event_type == 'Практика':
            subgroup_key = (group_id, subgroup_ids[group_id], timeslot)
            group_times[subgroup_key] = event  # Реєструємо підгрупу як зайняту

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
        print(f"Покоління: {generation + 1}, Найкраща пристосованість: {best_fitness}")

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
