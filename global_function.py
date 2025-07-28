import state
from random import randint, choice, random
from dateutil.relativedelta import relativedelta
from person import(
    Person
)
from names import male_names, female_names, patronymics_male, patronymics_female, last_names
import datetime
from tabulate import tabulate


def end_month():
    state.current_date += relativedelta(months = 1) 


def random_name(sex):
    return choice(male_names) if sex == 'male' else choice(female_names)

def generate_patronymic(father_name, sex):
    if sex == 'male' and father_name in patronymics_male:
        return patronymics_male[father_name]
    elif sex == 'female' and father_name in patronymics_female:
        return patronymics_female[father_name]
    

def generate_random_patronymic(sex):
    if sex == 'male':
        return choice(list(patronymics_male.values()))
    else:
        return choice(list(patronymics_female.values()))


def generate_random_person(id):
    sex = choice(['male', 'female'])
    first_name = random_name(sex)
    last_name = choice(last_names)
    if sex == "female":
        last_name += 'a'
    patroyomic = generate_random_patronymic(sex)

    age = randint(1, 70)
    birth_date = state.current_date - datetime.timedelta(days=365 * age)
    
    if age >= 18:
        education = choice(['School', 'HIGH SCHOOL', 'College', 'University'])
        income = randint(10000, 100000)
        work_place = choice(['Завод', 'IT-компания', 'Госслужба', 'Фриланс', None])
        criminal = random() < 0.05
    else:
        education = None
        income = 0
        work_place = None
        criminal = False

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
        credit_score=300,
        partner_id=None
    )
    return person

def display_people_table():
    table_data = []
    for p in state.people:
        if p.dead:
            income_display = f"died ({p.death_date.strftime('%Y-%m-%d')})"
            work_display = '-'
            credit_display = "-"
            balance_display = "-"
        else:
            income_display = f"{int(p.income):,}".replace(',', ' ')
            work_display = p.work_place
            balance_display = f"{int(p.balance):,}".replace(',', ' ')
            
            if p.credit_score is not None:
                credit_display = f"{int(p.credit_score):,}".replace(',', ' ')
            else:
                credit_display = "-"

        table_data.append([
            p.id,
            p.last_name,
            p.first_name,
            p.patroyomic,
            p.get_age(),
            p.father_id,
            p.mother_id,
            p.eduсation,
            income_display,
            balance_display,
            work_display,
            "yes" if p.pension else "no",
            "yes" if p.criminal_record else "no",
            credit_display,
        ])

    headers = ["ID", "Фамилия", "Имя", "Отчество", "Возраст", "Отец", "Мать", "Образование", "Доход", "Баланс", "Работа", "Пенсия", "Судимость", "Кредит"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
