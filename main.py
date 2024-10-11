import sys

import file_processor
import randomizer

from genetic_algo import genetic_algorithm, TIMESLOTS


# Вивід розкладу
def print_schedule(schedule, lecturers):
    schedule_dict = {}
    for event in schedule.events:
        if event.timeslot not in schedule_dict:
            schedule_dict[event.timeslot] = []
        schedule_dict[event.timeslot].append(event)

    for timeslot in TIMESLOTS:
        print(f"{timeslot}:")
        if timeslot in schedule_dict:
            for event in schedule_dict[timeslot]:
                group_info = ', '.join([f"Group: {gid}" + (
                    f" (Subgroup {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else '')
                                        for gid in event.group_ids])
                print(f"  {group_info}, {event.subject_name} ({event.event_type}), "
                      f"Teacher: {lecturers[event.lecturer_id]['LecturerName']}, auditorium: {event.auditorium_id}")
        else:
            print("  EMPTY")
        print()


# Клас для дублювання stdout
class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)

    def flush(self):
        for f in self.files:
            f.flush()


def main():
    # Завантажуємо дані
    groups = file_processor.load_groups('datasource/groups.csv')
    subjects = file_processor.load_subjects('datasource/subjects.csv')
    lecturers = file_processor.load_lecturers('datasource/lectures.csv')
    auditoriums = file_processor.load_auditoriums('datasource/auditoriums.csv')

    # Запускаємо генетичний алгоритм
    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)

    # Виводимо розклад і записуємо його у файл
    with open('schedule_output.txt', 'w', encoding='utf-8') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        try:
            print("\nBest schedule:\n")
            print_schedule(best_schedule, lecturers)
        finally:
            sys.stdout = original_stdout


# Основна функція
if __name__ == "__main__":
    method = sys.argv[1]

    if method == 'FILE':
        main()
    elif method == 'RANDOM':
        randomizer.main()
    else:
        print("Invalid parameter!!!")
