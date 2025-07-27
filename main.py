from person import Person
import state
from global_function import(
    end_month, generate_random_person, display_people_table
)
import matplotlib.pyplot as plt
import time
import sys

sys.stdout = open("output.txt", "w", encoding="utf-8")

# --- Создаем начальное население ---
p1 = Person(
    id=1,
    sex='male',
    first_name='Ivan',
    last_name='Cherepennikov',
    patroyomic='Valerevic',
    father_id=None,
    mother_id=None,
    INN=98398,
    SNILS=83978130,
    birth_year=2006,
    birth_month=2,
    birth_day=12,
    passport_number=52,
    drive_card_number=None,
    eduсation='HIGH SCHOOL',
    income=150000,
    work_place='police',
    cocity_state=1,
    criminal_record=False,
    credit_score=500,
    partner_id=2
)

p2 = Person(
    id=2,
    sex='female',
    first_name='Anna',
    last_name='Ivanova',
    patroyomic='Petrovna',
    father_id=None,
    mother_id=None,
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
    credit_score=500,
    partner_id=1
)

state.people.append(p1)
state.people.append(p2)

for i in range(3, 101):
    person = generate_random_person(i)
    state.people.append(person)

# --- Для графиков ---
age_list = []
income_by_age = []
credit_by_age = []
alive_count = []
dead_count = []

# --- Главный цикл ---
for month in range(12 * 30):
    print(state.current_date)
    for person in list(state.people):  
        if not person.dead:
            person.tick()
    
    # Сбор статистики раз в год (оптимизация)
    if state.current_date.month == 1:
        current_alive = 0

        for p in state.people:
            if not p.dead:
                current_alive += 1
                age = p.get_age()
                age_list.append(age)
                income_by_age.append(p.income)
                credit_by_age.append(p.credit_score)

        alive_count.append(current_alive)

    
    display_people_table()
    end_month()

sys.stdout.close()

# --- Построение графиков ---
plt.figure(figsize=(12, 7))

# Возраст и доход
plt.subplot(2, 2, 1)
plt.scatter(age_list, income_by_age, alpha=0.3, color='green')
plt.xlabel("Age")
plt.ylabel("Income")
plt.title("Доход по возрасту")

# Возраст и кредит
plt.subplot(2, 2, 2)
plt.scatter(age_list, credit_by_age, alpha=0.3, color='blue')
plt.xlabel("Age")
plt.ylabel("Credit Score")
plt.title("Кредитный рейтинг по возрасту")

# Живые по годам
plt.subplot(2, 1, 2)
years = list(range(len(alive_count)))
plt.plot(years, alive_count, label="Живые", color='green')
plt.xlabel("Годы симуляции")
plt.ylabel("Количество живых людей")
plt.title("Статистика количества живых")
plt.legend()


plt.tight_layout()
plt.savefig("stats.png", dpi=200)
plt.show()
