import datetime
import state
from dateutil.relativedelta import relativedelta
from random import random, randint, shuffle, choice, uniform
from names import male_names, female_names, last_names
import os
import numpy as np

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
        self.balance = 0
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



    def get_age(self):
        return relativedelta(state.current_date, self.birthday).years
    
    def get_age_at_death(self):
        if not self.dead:
            return self.get_age()
        return relativedelta(self.death_date, self.birthday).years

    def tick(self):
        if self.dead:
            return
        
        if self.in_army:
            if state.current_date >= self.army_release_date:
                self.in_army = False
                self.army_release_date = None
                self.work_place = None
                self.income = 0
            else:
                self.work_place = 'Армия'
                self.income = 10000
                return

        self.check_prison_release()

        age = self.get_age()
        if self.check_death(age):
            self.die()
            return

        self.balance += self.income
        if self.in_army:
            pass
        
        else:
            if self.get_age() > 20 and not self.in_army:
                self.balance -= randint(30000, 120000)
            else:
                self.inheritance_account = getattr(self, 'inheritance_account', 0)
                self.inheritance_account -= randint(30000, 50000)


            if self.inheritance_account > 0 and self.get_age() >= 18:
                print(f"{self.first_name} {self.last_name} получил наследство: {self.inheritance_account}")
                self.balance += self.inheritance_account
                self.inheritance_account = 0


        self.try_get_education()
        self.try_change_job()
        self.try_to_marry()
        self.try_to_divorce()
        self.try_have_children()
        self.try_go_to_prison()
        self.update_credit_score()
        self.go_to_pension()
        self.check_prison_status()
        self.check_and_take_loan()
        self.check_payment_due()
        self.apply_loan_interest()
        self.repay_loan()
        self.add_procent()
        self.try_bribe()
        self.fire()
        self.try_clear_credit_history()


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
        if age < 50:
            base_death_chance = 0.0007
        elif age < 70:
            base_death_chance = 0.007
        else:
            base_death_chance = 0.05 + (age - 70) * 0.003

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
        return random() < death_chance


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

        self.balance = 0
        self.debt = 0



    def try_get_education(self):
        if self.get_age() == 15:
            self.education = 'School'
        if self.get_age() == 17 and random() > 0.6:
            self.education = 'HIGH SCHOOL'
        elif self.education == 'HIGH SCHOOL' and self.get_age() >= 18:
            r = random()
            if r < 0.4:
                self.education = 'College'
            elif r < 0.6:
                self.education = 'University'

            elif r >= 0.4 and self.sex == 'male':
                self.in_army = True
                self.army_release_date = state.current_date + relativedelta(years=1)
                self.work_place = 'Армия'
                self.income = 10000

        elif self.education == 'College' and random() < 0.2:
            self.education = 'University'

            

    def try_change_job(self):
        if self.pension:
            return
        if random() <= 0.9:
            return
        if self.get_age() < 14 or self.criminal_record:
            return
        days_since_last_change = (state.current_date - self.last_job_change_date).days
        if days_since_last_change < 365:
            return
        if 14 <= self.get_age() < 16 and randint(1,5) != 2:
            return


        if self.get_age() >= 50:
            k = - 1
        else:
            k = 1

        #cпекуляция
        if self.work_place in ['Госслужба', 'Бизнес'] and random() < 0.01:
            self.income += randint(50000, 200000)
            if random() < 0.2:
                self.criminal_record = True
                self.prison_release_date = state.current_date + relativedelta(years=3)


        #new offer
        if random() >= 0.1:
            if self.work_place == 'IT-компания':
                delta = randint(20000, 40000)
                self.income += delta
            elif self.work_place == 'Завод':
                delta = randint(2000, 10000)
                self.income += delta
            elif self.work_place == 'Госслужба':
                delta = randint(15000, 30000)
                self.income += delta
            elif self.work_place == 'Фриланс':
                delta = randint(1000, 40000)
                self.income += delta
            elif self.work_place == 'Бизнес':
                delta = randint(-100000, +200000)
                self.income += delta
            elif self.work_place == 'Учитель':
                delta = randint(2000, 3000)
                self.income += delta
        

        else:
            chance = randint(1,6)
            if chance == 1 and self.education in ['College', 'University']:
                if self.work_place == None:
                    self.income = 60000
                else:
                    delta = randint(30000, 50000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'IT-компания'
            elif chance == 2:
                if self.work_place == None:
                    self.income = 40000
                else:
                    delta = randint(2000, 4000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Завод'
            if chance == 3 and self.education in ['HIGH SCHOOL', 'College', 'University']:
                if self.work_place == None:
                    self.income = 60000
                else:
                    if self.income <= 400000:
                        delta = randint(5000, 15000)
                    else:
                        delta = randint(1000,2000)
                        self.income += delta * k
                        self.last_job_change_date = state.current_date
                self.work_place = 'Госслужба'
            if chance == 4:
                if self.work_place == None:
                    self.income = 35000
                else:
                    delta = randint(1000, 35000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Фриланс'
            if chance == 5:
                if self.work_place == None:
                    self.income = 10000
                    self.work_place = 'Бизнес'
            if chance == 6 and self.education in ['College', 'University']:
                if self.work_place == None:
                    self.income = 30000
                else:
                    delta = randint(1000, 35000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Учиетель'

        self.max_income = max(self.income, self.max_income)
        self.income = max(0, self.income)


    def try_to_marry(self):
        if self.partner_id is not None or self.criminal_record and self.get_age() >= 16:
            return
        candidates = [p for p in state.people if p.id != self.id and p.partner_id is None and not p.dead and not p.criminal_record and p.get_age() > 18]
        shuffle(candidates)
        for candidate in candidates:
            if candidate.sex != self.sex and random() < 0.2:
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

        if random() < divorce_chance:
            print(f"{self.first_name} {self.last_name} развёлся с {partner.first_name} {partner.last_name}")
            self.partner_id = None
            partner.partner_id = None


    def try_have_children(self):
        if self.partner_id is None or self.get_age() < 16 or self.get_age() > 50 or self.criminal_record:
            return

        existing_children = self.count_children_with_partner()
        if existing_children >= 3:
            return

        if random() < 0.005:
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
                partner_id=None
            )
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
        if not self.criminal_record and random() < 0.0005 and self.get_age() > 14:
            self.criminal_record = True
            sentence_years = randint(2, 5)
            self.prison_release_date = state.current_date + relativedelta(years=sentence_years)

    def check_prison_release(self):
        if self.criminal_record and self.prison_release_date and state.current_date >= self.prison_release_date:
            self.criminal_record = False
            self.prison_release_date = None

    def check_prison_status(self):
        if self.criminal_record and self.prison_release_date:
            self.work_place = 'тюрьма'
            self.income = 15000
            self.criminal_record = True

    def update_credit_score(self):
        if self.dead or self.get_age() < 18:
            self.credit_score = 0
            return

        income_factor = np.tanh(np.log1p(self.income) / 14 - 1.5)    
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

        final_score = np.clip((raw_score + 1) / 2, 0, 1)
        self.credit_score = int(final_score * 999)


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
        
        if self.get_age() >= 65 and self.sex == 'male' and random() >= 0.85:
            self.pension = True
        elif self.get_age() >= 70 and self.sex == 'male' and random() >= 0.55:
            self.pension = True
        elif self.get_age() >= 75 and self.sex == 'male' and random() >= 0.25:
            self.pension = True
        elif self.get_age() >= 80 and self.sex == 'male' and random() >= 0.01:
            self.pension = True

        elif self.get_age() >= 60 and self.sex == 'female' and random() >= 0.85:
            self.pension = True
        elif self.get_age() >= 65 and self.sex == 'female' and random() >= 0.55:
            self.pension = True
        elif self.get_age() >= 70 and self.sex == 'female' and random() >= 0.25:
            self.pension = True
        elif self.get_age() >= 75 and self.sex == 'female' and random() >= 0.01:
            self.pension = True

        if self.pension:
            self.work_place = 'pension'
            self.income = 15000 + self.max_income*0.4


    #debt
    def check_and_take_loan(self):
        if self.balance < 0 and not self.gave_bribe:
            loan_amount = -self.balance
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

                    # Последствия просрочек
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
            payment = self.balance * 0.75
            payment = min(payment, self.debt)
            self.balance -= payment
            self.debt -= payment
            print(f"{self.first_name} {self.last_name} выплатил по кредиту: {payment:.2f}")

    def add_procent(self):
        self.balance = self.balance + (self.balance * state.key_court * 0.825)
        self.balance *= uniform(0.9, 1.1)

    def index_salary(self):
        self.income *= (1 + state.salary_up)

    def fire(self):
        if self.income < 200000 and self.debt > 100000 and self.get_age() > 30:
            if random() < 0.01:
                self.income = 0
                self.work_place = None
                print(f"{self.first_name} {self.last_name} выгорел и потерял работу.")



def random_name(sex):
    return choice(male_names) if sex == 'male' else choice(female_names)

def generate_patronymic(parent_name: str, child_sex: str):
    return parent_name + 'ovich' if child_sex == 'male' else parent_name + 'ovna'
