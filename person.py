import datetime
import state
from dateutil.relativedelta import relativedelta
from random import random, randint, shuffle, choice, uniform
from names import male_names, female_names, last_names
import os
import numpy as np
from personal_type import get_temperament_divorce_adjust, personal_traits, pension_personality_mod
from decimal import Decimal, getcontext

base = np.random.normal(loc=500, scale=150)
score = int(min(max(base, 200), 800))

def age_coefficient(age):
    if age < 20:
        return 0.7
    elif age < 30:
        return 1.0
    elif age < 50:
        return 1.1
    elif age < 65:
        return 1.0
    else:
        return 0.9
    

def get_birth_boost_factor():
    current_alive = len([p for p in state.people if not p.dead])
    x_n = current_alive / state.max_population
    x_next = state.logistic_r * x_n * (1 - x_n)
    target_population = x_next * state.max_population

    shortfall = target_population - current_alive
    if shortfall <= 0:
        return 1.0
    boost = min(3.0, 1.0 + shortfall / 100) 
    return boost


def get_death_boost_factor():
    current_alive = len([p for p in state.people if not p.dead])
    x_n = current_alive / state.max_population

    if x_n < 0.5:
        return 0.9
    elif x_n > 1.0:
        return min(2.0, 1.0 + (x_n - 1.0) * 4)
    else:
        return 1.0
    

def update_inflation_index():
    """Обновляет индекс инфляции на основе циклической модели."""
    y = state.inflation_year
    P_now = (1 + state.inflation_r) ** y * (1 + state.inflation_A * np.sin(2 * np.pi * y / state.inflation_T))
    P_prev = (1 + state.inflation_r) ** (y - 1/12) * (1 + state.inflation_A * np.sin(2 * np.pi * (y - 1/12) / state.inflation_T))
    month_factor = P_now / P_prev
    state.inflation_index *= month_factor
    state.inflation_year += 1/12

def update_salary_up_index():
    """Обновляет индекс инфляции на основе циклической модели."""
    y = state.salary_up_year
    P_now = (1 + state.salary_up_r) ** y * (1 + state.salary_up_A * np.sin(2 * np.pi * y / state.salary_up_T))
    P_prev = (1 + state.salary_up_r) ** (y - 1/12) * (1 + state.salary_up_A * np.sin(2 * np.pi * (y - 1/12) / state.salary_up_T))
    month_factor = P_now / P_prev
    state.salary_up_index *= month_factor 
    state.salary_up_year += 1/12

def setup_logging():
    log_dir = "people_statistic"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

log_dir = setup_logging()

class Person:
    def __init__(self, id, sex, first_name, last_name, patroyomic, father_id, mother_id, INN, SNILS, 
                 birth_year, birth_month, birth_day, passport_number, education, income, work_place, criminal_record, credit_score,
                 partner_id):
        self.id = id
        self.sex = sex
        self.first_name = first_name
        self.last_name = last_name
        self.patroyomic = patroyomic
        self.father_id = father_id
        self.mother_id = mother_id
        self.INN = INN
        self.SNILS = SNILS
        self.birthday = datetime.datetime(birth_year, birth_month, birth_day)

        self.passport_number = passport_number
        self.education = education
        self.income = income
        self.max_income = 0
        self.balance = 10_000
        self.loans_taken = 0
        self.last_payment_date = None
        self.monthly_payment = 0
        self.missed_payments = 0
        self.gave_bribe = False


        self.work_place = work_place
        self.criminal_record = criminal_record
        self.credit_score = credit_score

        self.partner_id = partner_id
        self.dead = False
        self.death_date = None
        self.last_job_change_date = state.current_date
        self.prison_release_date = None
        self.pension = False

        self.in_army = False
        self.army_release_date = None

        self.inheritance_account = 0
        self.debt = 0
        self.monthly_interest_rate = state.key_court
        self.cleared_credit = False

        self.temperament = None
        self.boost = 1.0

        self.have_car = False

        if self.in_army:
            self.join_army()



    def get_age(self):
        return relativedelta(state.current_date, self.birthday).years
    
    def get_age_at_death(self):
        if not self.dead:
            return self.get_age()
        return relativedelta(self.death_date, self.birthday).years
    
    def spend_money_by_type(self):
        t = self.temperament.lower()
        age = self.get_age()
        
        if age < 20:
            return 0
        
        if t == 'гипертим':
            return randint(40000, 150000)
        elif t == 'дистим':
            return randint(30000, 50000)
        elif t == 'эмотив':
            return randint(25000, 90000)
        elif t == 'эпилептоид':
            return randint(25000, 70000)
        elif t == 'тревожно-мнительный':
            return randint(30000, 50000)
        elif t == 'циклоид':
            if randint(1, 100) <= 30:
                return randint(70000, 150000)
            else:
                return randint(30000, 50000)
        elif t == 'истероид':
            return randint(30000, 120000)
        elif t == 'возбудимый':
            return randint(35000, 200000)
        else:
            return randint(30000, 100000)
        
    def apply_inflation_to_expenses(self):
        if not hasattr(self, "_expense_multiplier"):
            self._expense_multiplier = 1.0

        monthly_inflation = state.key_court  
        self._expense_multiplier *= (1 + monthly_inflation)

    def tick(self):
        if self.dead:
            return
        
        if self.in_army:
            self.military_service()
            return

        self.check_prison_release()

        age = self.get_age()
        if self.check_death(age):
            self.die()
            return
        
        if self.income < state.MAX_INCOME:
            self.income *= state.salary_up_index
        else:
            self.income = state.MAX_INCOME

        self.balance += self.income
        
        if self.get_age() > 20:
            self.apply_inflation_to_expenses() 
            expenses = self.spend_money_by_type() * state.inflation_index
            self.balance -= expenses


            if self.inheritance_account > 0:
                print(f"{self.first_name} {self.last_name} получил наследство: {self.inheritance_account}")
                self.balance += self.inheritance_account
                self.inheritance_account = 0

        if self.get_age() <= 18:
            self.balance = 0
            self.debt = 0
            self.loans_taken = 0

        if self.balance <= 0 and self.get_age() <= 23:
            self.balance += 5e4

        if self.balance > 1e5:
            tax = self.balance * 0.15
            self.balance -= tax
            state.inflation_index *= 1.000000001

        if self.balance > 1e6:
            tax = self.balance * 0.25
            self.balance -= tax
            state.inflation_index *= 1.00000001

        if self.balance >= 1e7:
            tax = self.balance * 0.35
            self.balance -= tax
            state.inflation_index *= 1.0000001

        if self.balance < -1e6:
            self.balance += 1e5


        if self.balance <= - 9e7:
            chance = random()
            if chance < 00.5:
                self.dead = True
            elif chance >= 0.9:
                self.balance = 0
            else:
                self.balance += 1e4

        state.oil_in_simulation = state.oil_amount_per_person/2

        if self.get_age() >= 18 and self.balance >= 1e7:
            self.have_car = True
            state.car_amaunt += 1
            self.balance -= 7e6
            print("машин сейчас: ", state.car_amaunt)

        if self.have_car == True:
            state.oil_in_simulation -= 0.0001

        state.inflation_index = (state.inflation_index * 0.0000001 * state.oil_in_simulation / 198968) + state.inflation_index

        self.try_get_education()
        self.try_change_job()
        self.try_to_marry()
        self.try_to_divorce()
        self.try_have_children()
        self.try_go_to_prison()
        self.update_credit_score()
        self.go_to_pension()
        self.invest_savings()
        self.check_prison_status()
        self.check_and_take_loan()
        self.check_payment_due()
        self.apply_loan_interest()
        self.repay_loan()
        self.add_procent()
        self.try_bribe()
        self.fire()
        self.try_clear_credit_history()

        self.balance = np.clip(self.balance, -1e8, 1e8)


        '''log_path = os.path.join("people_statistic", f"person_{self.id}.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            log_entry = (
                f"{state.current_date.date()}: "
                f"Возраст: {self.get_age()}, "
                f"Доход: {int(round(self.income))}, "
                f"Баланс: {int(round(self.balance))}, "
                f"Долг: {int(round(self.debt))}, "
                f"Кредитный рейтинг: {self.credit_score}, "
                f"Работа: {self.work_place}, "
                f"Образование: {self.eduсation}, "
                f"{'Мертв' if self.dead else 'Жив'}\n"
            )
            f.write(log_entry)'''



    def check_death(self, age):
        base_death_chance = 0.001
        if self.have_car:
            base_death_chance *= 2
        
        if self.in_army:
            base_death_chance = 0.003
            
            if self.temperament == 'эпилептоид':
                base_death_chance *= 0.7  
            elif self.temperament == 'возбудимый':
                base_death_chance *= 1.5 
            elif self.temperament == 'тревожно-мнительный':
                base_death_chance *= 0.5 

            if random() < 0.05:
                base_death_chance *= 2.5

        if age < 55:
            base_death_chance *= 1.0
        elif age < 75:
            base_death_chance *= 10
        else:
            base_death_chance = 0.025 + (age - 70) * 0.002

        wealth_modifier = 1.0
        if self.income > 100000:
            wealth_modifier -= 0.1
        elif self.income < 20000:
            wealth_modifier += 0.05

        if self.balance > 500000:
            wealth_modifier -= 0.1
        elif self.balance < 10000:
            wealth_modifier += 0.05

        if self.debt > 200000:
            wealth_modifier += 0.1

        wealth_modifier = max(0.7, min(1.3, wealth_modifier))
        death_chance = base_death_chance * wealth_modifier
        death_boost = get_death_boost_factor()
        return random() < death_chance * death_boost


    def die(self):
        self.dead = True
        self.death_date = state.current_date
        print(f"{self.first_name} {self.last_name} умер в возрасте {self.get_age()}")

        children = [p for p in state.people if (p.father_id == self.id or p.mother_id == self.id) and not p.dead]
        if not children:
            return
        
        inheritance = self.balance
        share = inheritance // len(children)
        
        debt_share = self.debt // len(children) if self.debt > 0 else 0
        
        for child in children:
            if child.get_age() < 18:
                child.inheritance_account += share
                child.inheritance_account -= debt_share
            else:
                child.balance += share
                child.debt += debt_share
                print(f"{child.first_name} {child.last_name} получил долг {debt_share} от умершего {self.first_name} {self.last_name}")



    def try_get_education(self):
        personality_factor = {
            'гипертим': 1.2,
            'дистим': 0.7,
            'эмотив': 1.1,
            'эпилептоид': 0.9,
            'тревожно-мнительный': 0.8,
            'циклоид': 1.0,
            'истероид': 1.0,
            'возбудимый': 1.1,
            None: 1.0
        }

        factor = personality_factor.get(self.temperament, 1.0)

        if self.get_age() == 15:
            self.education = 'School'
        
        if self.get_age() == 18 and self.sex == 'male' and not self.in_army:
            if random() < 0.05:
                self.join_army()
                return
                
        if self.get_age() == 17 and random() > 0.6 / factor:  
            self.education = 'HIGH SCHOOL'
        elif self.education == 'HIGH SCHOOL' and self.get_age() >= 18:
            r = random()
            college_chance = 0.4 * factor
            university_chance = 0.2 * factor

            if r < college_chance:
                self.education = 'College'
                self.boost = 1.3
            elif r < college_chance + university_chance:
                self.education = 'University'
                self.boost = 2
            elif self.sex == 'male' and not self.in_army and random() < 0.5:
                self.join_army()

        elif self.education == 'College' and random() < 0.2 * factor:
            self.education = 'University'



            

    def try_change_job(self):
        if self.in_army:
            return
        if self.pension:
            return
        if random() <= 0.8:
            return
        if self.get_age() < 14 or self.criminal_record:
            return
        days_since_last_change = (state.current_date - self.last_job_change_date).days
        if days_since_last_change < 365:
            return
        if 14 <= self.get_age() < 16 and randint(1, 5) != 2:
            return

        traits = personal_traits.get(self.temperament, {
            'лидерство': 0.5,
            'общительность': 0.5,
            'стрессоустойчивость': 0.5,
            'амбициозность': 0.5,
            'добросовестность': 0.5 
        })

        base_salary_factor = {
            'гипертим': 1.3,
            'дистим': 0.65,
            'эмотив': 1.1,
            'эпилептоид': 0.85,
            'тревожно-мнительный': 0.7,
            'истероид': 1.1,
            None: 1.0
        }
        factor = base_salary_factor.get(self.temperament, 1.0)
        factor *= 1 + traits['амбициозность'] * 0.2
        if random() > (0.1 + traits['лидерство'] * 0.2 + traits['общительность'] * 0.1):
            return

        k = -1 if self.get_age() >= 45 else 1

        # Спекуляция/коррупция
        if self.work_place in ['Госслужба', 'Бизнес'] and random() < (0.01 * (1 - traits['добросовестность'])):
            self.income += int(randint(50000, 200000) * factor)
            if random() < 0.2:
                self.criminal_record = True
                self.prison_release_date = state.current_date + relativedelta(years=3)

        # Новое предложение
        if random() >= 0.1:
            if self.work_place == 'IT-компания':
                delta = int(randint(20000, 40000) * factor) * (state.salary_up_index + 1)
                self.income += delta
            elif self.work_place == 'Завод':
                delta = int(randint(2000, 10000) * factor) * (state.salary_up_index + 1)
                self.income += delta
            elif self.work_place == 'Госслужба':
                delta = int(randint(15000, 30000) * factor) * (state.salary_up_index + 1)
                self.income += delta
            elif self.work_place == 'Фриланс':
                delta = int(randint(1000, 40000) * factor) * (state.salary_up_index + 1)
                self.income += delta
            elif self.work_place == 'Бизнес':
                delta = int(randint(-150000, +300000) * factor) * (state.salary_up_index + 1)
                self.income += delta
            elif self.work_place == 'Учитель':
                delta = int(randint(2000, 3000) * factor) * (state.salary_up_index + 1)
                self.income += delta 
        else:
            chance = randint(1, 6)
            if chance == 1 and self.education in ['College', 'University']:
                if self.work_place is None:
                    self.income = 60000 * factor
                else:
                    delta = randint(30000, 50000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'IT-компания'
            elif chance == 2:
                if self.work_place is None:
                    self.income = 40000 * factor
                else:
                    delta = randint(2000, 4000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Завод'
            elif chance == 3 and self.education in ['HIGH SCHOOL', 'College', 'University']:
                if self.work_place is None:
                    self.income = 60000 * factor
                else:
                    if self.income <= 400000:
                        delta = randint(5000, 15000)
                    else:
                        delta = randint(1000, 2000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Госслужба'
            elif chance == 4:
                if self.work_place is None:
                    self.income = 35000 * factor
                else:
                    delta = randint(1000, 35000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Фриланс'
            elif chance == 5:
                if self.work_place is None:
                    self.income = 10000 * factor
                    self.work_place = 'Бизнес'
            elif chance == 6 and self.education in ['College', 'University']:
                if self.work_place is None:
                    self.income = 30000 * factor
                else:
                    delta = randint(1000, 35000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Учитель'

        self.max_income = max(self.income, self.max_income)


    def try_to_marry(self):
        if self.in_army:
            return
        if self.partner_id is not None or self.criminal_record and self.get_age() >= 16:
            return
        candidates = [p for p in state.people if p.id != self.id and p.partner_id is None and not p.dead and not p.criminal_record and p.get_age() > 18]
        shuffle(candidates)
        for candidate in candidates:
            if candidate.sex != self.sex and random() < 0.4:
                self.partner_id = candidate.id
                candidate.partner_id = self.id
                print(state.current_date)
                break

    def try_to_divorce(self):
        if self.partner_id is None or self.dead:
            return

        partner = next((p for p in state.people if p.id == self.partner_id), None)
        if not partner or partner.dead:
            return

        divorce_chance = 0.01

        if self.criminal_record or partner.criminal_record:
            divorce_chance += 0.005

        if abs(self.income - partner.income) > 100000:
            divorce_chance += 0.002

        temperament_scale = 0.9
        divorce_chance += get_temperament_divorce_adjust(self.temperament, partner.temperament, scale=temperament_scale)

        if hasattr(self, 'married_since') and self.married_since:
            years_together = (state.current_date - self.married_since).days / 365.0
            divorce_chance = max(0.0, divorce_chance - min(0.005, years_together * 0.0008))

        if random() < divorce_chance:
            print(f"{self.first_name} {self.last_name} развёлся с {partner.first_name} {partner.last_name}")
            self.partner_id = None
            partner.partner_id = None



    def try_have_children(self):
        if self.in_army:
            birth_boost = get_birth_boost_factor() * 0.7
    
        if self.partner_id is None or self.get_age() < 16 or self.get_age() > 50 or self.criminal_record:
            return

        existing_children = self.count_children_with_partner()
        if existing_children >= 3:
            return
        
        birth_boost = get_birth_boost_factor()
        if random() < 0.015 * birth_boost:
            partner = next((p for p in state.people if p.id == self.partner_id), None)
            if not partner:
                return

            new_id = max(p.id for p in state.people) + 1
            sex = 'male' if random() < 0.5 else 'female'
            first_name = random_name(sex)
            patroyomic = generate_patronymic(self.first_name, sex)

            child = Person(
                id=new_id,
                sex=sex,
                first_name=first_name,
                last_name=self.last_name,
                patroyomic=patroyomic,
                father_id=self.id if self.sex == 'male' else self.partner_id,
                mother_id=self.id if self.sex == 'female' else self.partner_id,
                INN=randint(100000, 999999),
                SNILS=randint(100000000, 999999999),
                birth_year=state.current_date.year,
                birth_month=state.current_date.month,
                birth_day=state.current_date.day,
                passport_number=None,
                education='NONE',
                income=0,
                work_place=None,
                criminal_record=False,
                credit_score=None,
                partner_id=None,
            )
            child.temperament = self.temperament if random() < 0.5 else partner.temperament
            child.balance = 100_000
            state.people.append(child)

    def count_children_with_partner(self):
        count = 0
        for person in state.people:
            is_child = (
                (person.father_id == self.id and person.mother_id == self.partner_id) or
                (person.mother_id == self.id and person.father_id == self.partner_id)
            )
            if is_child:
                father = None
                if person.father_id is not None:
                    father = next((p for p in state.people if p.id == person.father_id), None)
                
                if father:
                    person.patroyomic = generate_patronymic(father.first_name, person.sex)
                    if person.sex == 'male':
                        person.last_name = father.last_name
                    else:
                        person.last_name = father.last_name + 'a'
                count += 1
        return count


    def try_go_to_prison(self):
        """Попытка отправить персонажа в тюрьму"""
        if not self.criminal_record and random() < 0.0001 and self.get_age() > 14:
            self.criminal_record = True
            sentence_years = randint(1, 8)
            
            # Сначала пробуем уйти в армию
            if (sentence_years <= 2 
                and self.sex == 'male' 
                and 18 <= self.get_age() <= 40
                and not hasattr(self, 'repeat_offender')):
                
                if self.join_army(avoid_prison=True):
                    return
                    
            # Если не получилось - устанавливаем срок
            self.prison_release_date = state.current_date + relativedelta(years=sentence_years)
            print(f"{self.first_name} {self.last_name} приговорен к {sentence_years} годам тюрьмы")

    def can_avoid_prison(self, sentence_years):
        return (self.sex == 'male' 
                and 18 <= self.get_age() <= 40
                and sentence_years <= 2
                and not hasattr(self, 'repeat_offender')
                and not self.in_army)
    
    def join_army(self, avoid_prison=False):
        """Вступление в армию с возможностью избежать тюрьмы"""
        if self.in_army:
            return False
            
        if avoid_prison:
            if not (self.sex == 'male' 
                    and 18 <= self.get_age() <= 40
                    and not hasattr(self, 'repeat_offender')):
                return False
                
            base_chance = 0.7
            if self.temperament == 'эпилептоид':
                base_chance += 0.2
            elif self.temperament == 'возбудимый':
                base_chance -= 0.1
                
            if random() > max(0.1, min(0.9, base_chance)):
                return False
        
        self.in_army = True
        self.init_military()
        
        # Если уходим от тюрьмы - очищаем судимость
        if avoid_prison:
            self.criminal_record = False
            if hasattr(self, 'prison_release_date'):
                del self.prison_release_date
            print(f"{self.first_name} {self.last_name} избежал тюрьмы, отправившись в армию!")
        else:
            print(f"{self.first_name} {self.last_name} призван в армию!")
        
        return True


    def check_prison_release(self):
        if self.criminal_record and self.prison_release_date and state.current_date >= self.prison_release_date:
            self.criminal_record = False
            self.prison_release_date = None

    def check_prison_status(self):
        """Проверка тюремного статуса"""
        if self.criminal_record:
            if hasattr(self, 'prison_release_date') and self.prison_release_date is not None:
                # Попытка уйти в армию вместо тюрьмы
                remaining_time = (self.prison_release_date - state.current_date).days / 365
                if (remaining_time <= 2 
                    and self.sex == 'male' 
                    and 18 <= self.get_age() <= 40
                    and not hasattr(self, 'repeat_offender')):
                    
                    if self.join_army(avoid_prison=True): 
                        return
                    
                self.work_place = 'тюрьма'
                self.income = 15000
                print(f"{self.first_name} {self.last_name} в тюрьме, осталось {remaining_time:.1f} лет")
            else:
                self.work_place = 'тюрьма'
                self.income = 15000
                print(f"{self.first_name} {self.last_name} в тюрьме (срок не определен)")

    def update_credit_score(self):
        if self.dead or self.get_age() < 18:
            self.credit_score = 0
            return
        
        safe_income = max(self.income, -0.99)
        income_factor = np.tanh(np.log1p(float(safe_income)) / 14 - 1.5) 
        safe_balance = max(self.balance, -0.99)
        safe_debt = max(self.debt, 0)

        balance_factor = np.tanh(np.log1p(safe_balance) / 15 - 1.5)
        debt_factor = -np.tanh(np.log1p(safe_debt + 1) / 12)
        age_factor = np.cos(self.get_age() / 80 * np.pi)     
        missed_factor = -min(self.missed_payments * 0.1, 1.0)    
        loan_factor = -min(self.loans_taken * 0.05, 0.5)             
        education_factor = {
            "None": -0.4,
            "College": 0.1,
            "University": 0.3
        }.get(self.education, 0)

        raw_score = (
            income_factor * 0.2 +
            balance_factor * 0.2 +
            debt_factor * 0.2 +
            age_factor * 0.05 +
            missed_factor * 0.15 +
            loan_factor * 0.1 +
            education_factor * 0.05
        )

        risk = min(1.0, (self.debt + 1) / 1e6 + self.missed_payments * 0.05)
        raw_score += np.random.normal(0, 0.15 + 0.3 * risk)
        if np.random.rand() < 0.01:
            raw_score -= np.random.uniform(0.5, 1.0)  
        elif np.random.rand() < 0.01:
            raw_score += np.random.uniform(0.5, 1.0)

 
        raw_score += np.random.normal(0, 0.1)   
        if self.have_car:
            raw_score += 50 

        final_score = np.clip((raw_score + 1) / 2, 0, 1)
        self.credit_score = int(np.nan_to_num(final_score) * 999)


    def try_bribe(self):
        if self.dead or self.criminal_record or self.get_age() < 18 or self.pension:
            return

        if random() < 0.02:
            print(f"{self.first_name} {self.last_name} попытался дать взятку.")
            self.gave_bribe = True 

            if random() < 0.7:
                self.income += 100000
                print(f"{self.first_name} {self.last_name} успешно дал взятку. Доход увеличен до {self.income}.")
            else:
                self.criminal_record = True
                self.prison_release_date = state.current_date + relativedelta(years=5)
                self.work_place = 'тюрьма'
                self.income = 15000
                print(f"{self.first_name} {self.last_name} попался на взятке и получил 5 лет тюрьмы.")

    def try_clear_credit_history(self):
        if self.dead or self.debt <= 0 or self.criminal_record or self.cleared_credit:
            return

        if random() < 0.003:
            print(f"{self.first_name} {self.last_name} замял кредитную историю и обнулил долг!")

            self.debt = 0
            self.missed_payments = 0
            self.monthly_payment = 0
            self.credit_score = max(self.credit_score, 600)
            self.cleared_credit = True






    def go_to_pension(self):
        if self.pension:
            return

        ptype = self.temperament.lower() if hasattr(self, 'temperament') else None
        mod = pension_personality_mod.get(ptype, 1.0) 

        age = self.get_age()
        sex = self.sex

        if sex == 'male':
            if age >= 80 and random() >= 0.01 * mod:
                self.pension = True
            elif age >= 75 and random() >= 0.25 * mod:
                self.pension = True
            elif age >= 70 and random() >= 0.55 * mod:
                self.pension = True
            elif age >= 65 and random() >= 0.85 * mod:
                self.pension = True

        elif sex == 'female':
            if age >= 75 and random() >= 0.01 * mod:
                self.pension = True
            elif age >= 70 and random() >= 0.25 * mod:
                self.pension = True
            elif age >= 65 and random() >= 0.55 * mod:
                self.pension = True
            elif age >= 60 and random() >= 0.85 * mod:
                self.pension = True

        if self.pension:
            self.work_place = 'pension'
            self.income = 15000 + self.max_income * 0.4



    #debt
    def check_and_take_loan(self):
        max_loan = self.income * 12
        if self.debt >= max_loan:
            return

        self.balance = int(self.balance)
        self.income = int(self.income)
        if self.balance < -self.income * 3 and not self.gave_bribe: 
            loan_amount = -self.balance * 0.8 
            self.debt += loan_amount
            self.debt += loan_amount
            self.balance += loan_amount
            self.loans_taken += 1

            self.monthly_payment = loan_amount / 12
            self.last_payment_date = state.current_date
            self.missed_payments = 0

            print(f"{self.first_name} {self.last_name} взял кредит на сумму {loan_amount:.2f}, платёж {self.monthly_payment:.2f}")
        elif self.balance < 0 and self.gave_bribe:
            print(f"{self.first_name} {self.last_name} не может взять кредит из-за истории с взяткой.")


    def check_payment_due(self):
        if self.debt <= 0 or not self.last_payment_date:
            return

        months_due = (state.current_date.year - self.last_payment_date.year) * 12 + (state.current_date.month - self.last_payment_date.month)

        if months_due >= 1:
            for _ in range(months_due):
                if self.balance >= self.monthly_payment:
                    self.balance -= self.monthly_payment
                    self.debt -= self.monthly_payment
                    self.last_payment_date += relativedelta(months=1)
                    print(f"{self.first_name} {self.last_name} оплатил ежемесячный платёж: {self.monthly_payment:.2f}")
                else:
                    self.missed_payments += 1
                    self.last_payment_date += relativedelta(months=1)
                    penalty = self.monthly_payment * 0.05 * self.missed_payments
                    self.debt += penalty
                    print(f"{self.first_name} {self.last_name} пропустил платёж! Штраф: {penalty:.2f}. Пропущено: {self.missed_payments}")

                    if self.missed_payments >= 3:
                        self.credit_score = max(0, self.credit_score - 50)
                    if self.missed_payments >= 6 and random() < 0.2:
                        self.try_go_to_prison()


    def apply_loan_interest(self):
        if self.debt > 0:
            interest = self.debt * self.monthly_interest_rate
            self.debt += interest
            print(f"{self.first_name} {self.last_name} начислены проценты по кредиту: {interest:.2f}")

    def repay_loan(self):
        if self.balance > 0 and self.debt > 0:
            payment = self.balance * 0.6
            payment = min(payment, self.debt)
            self.balance -= payment
            self.debt -= payment
            print(f"{self.first_name} {self.last_name} выплатил по кредиту: {payment:.2f}")

    def add_procent(self):
        self.balance = self.balance + (self.balance * state.key_court * 0.7)
        

    def index_salary(self):
        self.income *= (1 + state.salary_up)

    def fire(self):
        if self.income < 200000 and self.debt > 100000 and self.get_age() > 30:
            if random() < 0.01:
                self.income = 0
                self.work_place = None
                print(f"{self.first_name} {self.last_name} выгорел и потерял работу.")


    
    def update_income(self):

        salary = max(self.salary, 0)
        investments = max(self.investments_income, 0)
        rent_income = max(self.rent_income, 0)

        debt_interest = max(self.debt, 0) * 0.02
        penalties = max(self.penalties, 0)
        taxes = max(salary * 0.13, 0)

        total_income = (salary + investments + rent_income) - (debt_interest + penalties + taxes)
        self.income += total_income

        if not np.isfinite(self.income):
            self.income = 0

        self.income = np.clip(self.income, -1e6, 1e6)


    def init_military(self):
        self.work_place = "Армия (контракт)"
        self.income = 250000
        self.army_release_date = None
        self.army_rank = 1 
        self.army_serve_years = 0


    def military_service(self):
        if state.current_date.month == 1 and state.current_date.day == 1:
            self.army_serve_years += 1
            self.income *= 1.1
            if self.army_serve_years % 3 == 0 and self.army_rank < 10:
                self.army_rank += 1
                self.income += 50000 * self.army_rank
                print(f"{self.first_name} {self.last_name} повышен до звания уровня {self.army_rank}!")
        
        self.balance += self.income
        self.balance -= randint(20000, 50000)

        if self.check_death(self.get_age()):
            self.die()
            return
        
    def invest_savings(self):
        """Инвестирование части сбережений"""
        if self.income < 20000:  
            return
        
        if self.balance >= 1e5:
            self.balance *= random() + 0.3
            
        investment_ratio = {
            'гипертим': 0.4,
            'эпилептоид': 0.3,
            'дистим': 0.1,
            None: 0.2
        }.get(self.temperament, 0.2)
        
        if random() < 0.8: 
            amount = self.balance * 0.5
            risk = random()
            
            if risk > 0.2: 
                returns = amount * uniform(1.2, 2.5)
                self.balance += returns 
            elif risk < 0.9: 
                self.balance += amount * uniform(0.95, 1.05)
            else:  
                loss = amount * uniform(0.1, 0.3)
                self.balance -= loss
        


def random_name(sex):
    return choice(male_names) if sex == 'male' else choice(female_names)

def generate_patronymic(parent_name: str, child_sex: str):
    return parent_name + 'ovich' if child_sex == 'male' else parent_name + 'ovna'