import state
from global_function import (
    end_month, generate_random_person, display_people_table
)
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
import numpy as np
import shutil
import os
import csv

def setup_individual_logs():
    log_dir = "people_statistic"
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)
    return log_dir

def log_person_data(person):
    filename = f"people_statistic/person_{person.id}.csv"
    write_headers = not os.path.exists(filename)

    if person.dead and os.path.exists(filename):
        return

    age = person.get_age()
    days_on_job = (state.current_date - person.last_job_change_date).days if person.last_job_change_date else 0
    marital_status = 1 if person.partner_id is not None else 0
    
    row = [
        person.id,
        person.sex,
        age,
        person.education,
        
        int(person.income),
        int(person.max_income),
        int(person.balance),
        int(person.debt),
        int(person.inheritance_account),
        int(person.monthly_payment),
        person.loans_taken,
        person.monthly_interest_rate,
        
        person.missed_payments,
        int(person.cleared_credit),
        
        person.work_place,
        days_on_job,
        int(person.pension),
        int(person.in_army),
        
        int(person.criminal_record),
        int(person.gave_bribe),
        
        marital_status,
        person.temperament,
        
        int(person.credit_score) if person.credit_score is not None else 0
    ]

    headers = [
        "ID", "Пол", "Возраст", "Образование",
        "income", "max_income", "balance", "debt",
        "inheritance_account", "monthly_payment", "loans_taken",
        "monthly_interest_rate",
        "missed_payments", "cleared_credit",
        "Работа", "ДнейНаРаботе", "Пенсионер", "ВАрмии",
        "Судимость", "gave_bribe",
        "СемейноеПоложение", "ТипЛичности",
        "КредитОчки"
    ]

    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        if write_headers:
            writer.writerow(headers)
        writer.writerow(row)


sys.stdout = open("output.txt", "w", encoding="utf-8")
setup_individual_logs()

for i in range(1, state.max_population+1):
    person = generate_random_person(i)
    state.people.append(person)

# 4. Основной цикл симуляции
age_list = []
income_by_age = []
credit_by_age = []
alive_count = []
dead_count = []
net_worth_stats = []
net_worth_by_age = [] 

for month in range(12 * 350):
    print(state.current_date)
    
    for person in list(state.people):  
        if not person.dead:
            person.tick()
    
    for person in state.people:
        log_person_data(person)
    
    if state.current_date.month == 1:
        current_alive = 0
        total_net_worth = 0
        for p in state.people:
            if not p.dead:
                current_alive += 1
                age = p.get_age()
                age_list.append(age)
                income_by_age.append(p.income)
                credit_by_age.append(p.credit_score)
                net_worth = p.balance - p.debt
                net_worth_by_age.append((age, net_worth))
                total_net_worth += net_worth
        alive_count.append(current_alive)
        avg_net_worth = total_net_worth / current_alive if current_alive > 0 else 0
        net_worth_stats.append(avg_net_worth)
    
    display_people_table()
    end_month()

sys.stdout.close()

plt.figure(figsize=(16, 7))
def calculate_averages(x_list, y_list):
    grouped = defaultdict(list)
    for x, y in zip(x_list, y_list):
        if y is not None:
            grouped[x].append(y)
    avg_x = sorted(grouped.keys())
    avg_y = [np.mean([v for v in grouped[x] if v is not None]) for x in avg_x]
    return avg_x, avg_y

# График 1 — Возраст и доход
plt.subplot(2, 2, 1)
plt.scatter(age_list, income_by_age, alpha=0.1, color='green', label='Данные')
avg_age, avg_income = calculate_averages(age_list, income_by_age)
plt.plot(avg_age, avg_income, color='darkgreen', linewidth=2, label='Средний доход')
plt.xlabel("Возраст")
plt.ylabel("Доход")
plt.title("Доход по возрасту")
plt.legend()

# График 2 — Возраст и кредитный рейтинг
plt.subplot(2, 2, 2)
plt.scatter(age_list, credit_by_age, alpha=0.1, color='blue', label='Данные')
avg_age, avg_credit = calculate_averages(age_list, credit_by_age)
plt.plot(avg_age, avg_credit, color='navy', linewidth=2, label='Средний кредит')
plt.xlabel("Возраст")
plt.ylabel("Кредитный рейтинг")
plt.title("Кредитный рейтинг по возрасту")
plt.legend()

# График 3 — Живые по годам
plt.subplot(2, 2, 3)
years = list(range(len(alive_count)))
plt.plot(years, alive_count, label="Живые", color='green')
plt.xlabel("Годы симуляции")
plt.ylabel("Количество живых людей")
plt.title("Статистика количества живых")
plt.legend()

# График 4 — Чистая стоимость по возрасту
plt.subplot(2, 2, 4)
ages_net = [x[0] for x in net_worth_by_age]
net_worths = [x[1] for x in net_worth_by_age]
plt.scatter(ages_net, net_worths, alpha=0.1, color='purple', label="По возрастам")
avg_age, avg_net = calculate_averages(ages_net, net_worths)
plt.plot(avg_age, avg_net, color='indigo', linewidth=2, label="Средняя дельта")
plt.xlabel("Возраст")
plt.ylabel("Капитал (баланс - долг)")
plt.title("Капитал")
plt.legend()

plt.tight_layout()
plt.savefig("stats.png", dpi=200)
plt.show()