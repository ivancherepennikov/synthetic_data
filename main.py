from person import Person
import state
from global_function import(
    end_month,generate_random_person, display_people_table
)
import time
import sys

sys.stdout = open("output.txt", "w", encoding="utf-8")


p1 = Person(
    id=1,
    sex='male',
    first_name='Ivan',
    last_name='Cherepennikov',
    patroyomic='Valerevic',
    father_id=2331,
    mother_id=242,
    INN=98398,
    SNILS=83978130,

    birth_year=2006,
    birth_month=2,
    birth_day=12,
    passport_number=52,
    drive_card_number=None,
    eduсation='HIGH SCHOOL',
    income=15000,
    work_place='police',
    cocity_state=1,
    criminal_record=False,
    credit_score=999,
    partner_id=2
)

p2 = Person(
    id=2,
    sex='female',
    first_name='Anna',
    last_name='Ivanova',
    patroyomic='Petrovna',
    father_id=23555,
    mother_id=212,
    INN=92221,
    SNILS=844478130,
    birth_year=2004,
    birth_month=6,
    birth_day=23,

    passport_number=32,
    drive_card_number='C921MA',
    eduсation='College',
    income=35000,
    work_place='post',
    cocity_state=2,
    criminal_record=True,
    credit_score=950,
    partner_id=1
)

state.people.append(p1)
state.people.append(p2)

for i in range(3, 101):
    person = generate_random_person(i)
    state.people.append(person)


for month in range(12 * 20):
    print(state.current_date)
    for person in list(state.people):  
        if not person.dead:
            person.tick()
    
    display_people_table()
    end_month()

sys.stdout.close()

