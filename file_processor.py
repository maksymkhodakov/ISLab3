import csv


# Завантаження груп
def load_groups(filename):
    groups = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            group_id = row['groupNumber']
            groups[group_id] = {
                'NumStudents': int(row['studentAmount']),
                'Subgroups': row['subgroups'].split(';') if row['subgroups'] else []
            }
    return groups


# Завантаження самих дисциплін
def load_subjects(filename):
    subjects = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subjects.append({
                'SubjectID': row['id'],
                'SubjectName': row['name'],
                'GroupID': row['groupID'],
                'NumLectures': int(row['numLectures']),
                'NumPracticals': int(row['numPracticals']),
                'RequiresSubgroups': row['requiresSubgroups'] == 'Yes',
                'WeekType': row['weekType'] if 'WeekType' in row else 'Both'  # 'Парний', 'Непарний' або Обидва
            })
    return subjects


# Завантаження лекторів
def load_lecturers(filename):
    lecturers = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lecturer_id = row['lecturerID']
            lecturers[lecturer_id] = {
                'LecturerName': row['lecturerName'],
                'SubjectsCanTeach': row['subjectsCanTeach'].split(';'),
                'TypesCanTeach': row['typesCanTeach'].split(';'),
                'MaxHoursPerWeek': int(row['maxHoursPerWeek'])
            }
    return lecturers


# Завантаження аудиторій
def load_auditoriums(filename):
    auditoriums = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            auditorium_id = row['auditoriumID']
            auditoriums[auditorium_id] = int(row['capacity'])
    return auditoriums
