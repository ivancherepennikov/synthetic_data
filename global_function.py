import state
from random import randint, choice, random
from dateutil.relativedelta import relativedelta
from person import(
    Person
)
from names import male_names, female_names
import datetime
from tabulate import tabulate


def end_month():
    state.current_date += relativedelta(months = 1) 



def random_name(sex):
    return choice(male_names) if sex == 'male' else choice(female_names)

def generate_patronymic(parent_name, sex):
    return parent_name + ('ovich' if sex == 'male' else 'ovna')

def generate_random_person(id):
    sex = choice(['male', 'female'])
    first_name = random_name(sex)
    last_name = f"Lastname{id}"
    patroyomic = generate_patronymic('Vasiliy', sex)

    age = randint(18, 70)
    birth_date = state.current_date - datetime.timedelta(days=365 * age)
    
    education = choice(['School', 'HIGH SCHOOL', 'College', 'University'])
    income = randint(10000, 100000)
    work_place = choice(['Завод', 'IT-компания', 'Госслужба', 'Фриланс', None])
    criminal = random() < 0.05

    person = Person(
        id=id,
        sex=sex,
        first_name=first_name,
        last_name=last_name,
        patroyomic=patroyomic,
        father_id=None,
        mother_id=None,
        INN=randint(100000, 999999),
        SNILS=randint(100000000, 999999999),
        birth_year=birth_date.year,
        birth_month=birth_date.month,
        birth_day=birth_date.day,
        passport_number=randint(1000, 9999),
        drive_card_number=None,
        eduсation=education,
        income=income,
        work_place=work_place,
        cocity_state=randint(1, 10),
        criminal_record=criminal,
        credit_score=500,
        partner_id=None
    )
    return person


def display_people_table():
    table_data = []
    for p in state.people:
        credit_display = "-" if p.dead else p.credit_score
        table_data.append([
            p.id,
            p.first_name,
            p.last_name,
            p.get_age(),
            p.father_id,
            p.mother_id,
            p.eduсation,
            p.income,
            p.work_place,
            "Да" if p.criminal_record else "Нет",
            "Да" if p.dead else "Нет",
            credit_display,
        ])
    
    headers = ["ID", "Имя", "Фамилия", "Возраст", "Отец", "Мать", "Образование", "Доход", "Работа", "Судимость", "Мертв", "Кредит"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

