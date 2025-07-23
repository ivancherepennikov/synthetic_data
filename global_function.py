import state
from random import randint
from dateutil.relativedelta import relativedelta
from person import(
    Person
)

def end_day():
    state.current_date += relativedelta(days = 1) 

    chance_to_new_person = randint(1,5)
    if chance_to_new_person == 3:
      create_new_person()

def create_new_person(father_id, mother_id):
    chance_to_male = randint(1,2152)
    if chance_to_male <= 1000:
        new_people_sex = 'male'
    else:
        new_people_sex = 'female'

    new_person = Person(
        id=3,
        sex=new_people_sex,
        first_name='Anna',
        last_name='Ivanova',
        patroyomic='Petrvna',
        father_id=father_id,
        mother_id=mother_id,
        INN=92221,
        SNILS=844478130,
        birth_year=state.current_date.year,
        birth_month=state.current_date.month,
        birth_day=state.current_date.day,
        passport_number=32,
        drive_card_number=None,
        eduсation=None,
        income=0,
        work_place=None,
        cocity_state=0,
        criminal_record=False,
        credit_score=0,
        partner_id=None
    )

    state.people.append(new_person)