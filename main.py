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
    income=50000,
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
net_worth_stats = []  # Список для хранения дельты (баланс - долг)
net_worth_by_age = []  # Список для хранения дельты по возрастам

# --- Главный цикл ---
for month in range(12 * 100):
    print(state.current_date)
    for person in list(state.people):  
        if not person.dead:
            person.tick()
    
    # Сбор статистики раз в год (оптимизация)
    if state.current_date.month == 1:
        current_alive = 0
        total_net_worth = 0  # Общая чистая стоимость всех живых

        for p in state.people:
            if not p.dead:
                current_alive += 1
                age = p.get_age()
                age_list.append(age)
                income_by_age.append(p.income)
                credit_by_age.append(p.credit_score)
                
                # Рассчитываем чистую стоимость (баланс - долг)
                net_worth = p.balance - p.debt
                net_worth_by_age.append((age, net_worth))
                total_net_worth += net_worth

        alive_count.append(current_alive)
        # Средняя чистая стоимость на человека
        avg_net_worth = total_net_worth / current_alive if current_alive > 0 else 0
        net_worth_stats.append(avg_net_worth)
    
    display_people_table()
    end_month()

sys.stdout.close()

# --- Построение графиков ---
plt.figure(figsize=(16, 7))

# График 1 — Возраст и доход
plt.subplot(2, 2, 1)
plt.scatter(age_list, income_by_age, alpha=0.3, color='green')
plt.xlabel("Возраст")
plt.ylabel("Доход")
plt.title("Доход по возрасту")

# График 2 — Возраст и кредит
plt.subplot(2, 2, 2)
plt.scatter(age_list, credit_by_age, alpha=0.3, color='blue')
plt.xlabel("Возраст")
plt.ylabel("Кредитный рейтинг")
plt.title("Кредитный рейтинг по возрасту")

# График 3 — Живые по годам
plt.subplot(2, 2, 3)
years = list(range(len(alive_count)))
plt.plot(years, alive_count, label="Живые", color='green')
plt.xlabel("Годы симуляции")
plt.ylabel("Количество живых людей")
plt.title("Статистика количества живых")
plt.legend()

# График 4 — Чистая стоимость по возрастам и средняя по годам
plt.subplot(2, 2, 4)
# Разделяем данные по возрастам для scatter plot
ages_net = [x[0] for x in net_worth_by_age]
net_worths = [x[1] for x in net_worth_by_age]
plt.scatter(ages_net, net_worths, alpha=0.3, color='purple', label="По возрастам")
plt.xlabel("Возраст")
plt.ylabel("Чистая стоимость (баланс - долг)")
plt.title("дельта по возрастам")


plt.tight_layout()
plt.savefig("stats.png", dpi=200)
plt.show()