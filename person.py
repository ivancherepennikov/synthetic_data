import datetime
import state
from dateutil.relativedelta import relativedelta
from random import random, randint, shuffle, choice
from names import male_names, female_names, last_names

class Person:
    def __init__(self, id, sex, first_name, last_name, patroyomic, father_id, mother_id, INN, SNILS, 
                 birth_year, birth_month, birth_day, passport_number, drive_card_number, eduсation, income, work_place, cocity_state, criminal_record, credit_score,
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
        self.drive_card_number = drive_card_number
        self.eduсation = eduсation
        self.income = income
        self.balance = 0
        self.work_place = work_place
        self.cocity_state = cocity_state
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


    def get_age(self):
        return relativedelta(state.current_date, self.birthday).years

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
        self.balance -= randint(20000, 150000)

        if self.inheritance_account > 0 and self.get_age() >= 18:
            print(f"{self.first_name} {self.last_name} получил наследство: {self.inheritance_account}")
            self.balance += self.inheritance_account
            self.inheritance_account = 0


        self.try_get_education()
        self.try_change_job()
        self.try_to_marry()
        self.try_have_children()
        self.try_go_to_prison()
        self.update_credit_score()
        self.go_to_pension()
        self.check_prison_status()

    def check_death(self, age):
        if age < 50:
            return random() < 0.0007
        elif age < 70:
            return random() < 0.007
        else:
            return random() < (0.05 + (age - 70) * 0.003)

    def die(self):
        self.dead = True
        self.death_date = state.current_date
        print(f"{self.first_name} {self.last_name} умер в возрасте {self.get_age()}")

        children = [p for p in state.people if (p.father_id == self.id or p.mother_id == self.id) and not p.dead]
        if not children:
            return
        
        inheritance = self.balance
        share = inheritance // len(children)
        
        for child in children:
            if child.get_age() < 18:
                child.inheritance_account += share
            else:
                child.balance += share

        self.balance = 0



    def try_get_education(self):
        if self.get_age() == 15:
            self.eduсation = 'School'
        if self.get_age() == 17 and random() > 0.6:
            self.eduсation = 'HIGH SCHOOL'
        elif self.eduсation == 'HIGH SCHOOL' and self.get_age() >= 18:
            r = random()
            if r < 0.4:
                self.eduсation = 'College'
            elif r < 0.6:
                self.eduсation = 'University'

            elif r >= 0.4 and self.sex == 'male':
                self.in_army = True
                self.army_release_date = state.current_date + relativedelta(years=1)
                self.work_place = 'Армия'
                self.income = 10000

        elif self.eduсation == 'College' and random() < 0.2:
            self.eduсation = 'University'

            

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
            elif self.work_place == 'Бисзнес':
                delta = randint(-100000, +200000)
                self.income += delta
            elif self.work_place == 'Учитель':
                delta = randint(2000, 3000)
                self.income += delta
        

        else:
            chance = randint(1,6)
            if chance == 1 and self.eduсation in ['College', 'University']:
                if self.work_place == None:
                    self.income == 60000
                else:
                    delta = randint(30000, 50000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'IT-компания'
            elif chance == 2:
                if self.work_place == None:
                    self.income == 40000
                else:
                    delta = randint(2000, 4000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Завод'
            if chance == 3 and self.eduсation in ['HIGH SCHOOL', 'College', 'University']:
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
            if chance == 6 and self.eduсation in ['College, University']:
                if self.work_place == None:
                    self.income == 30000
                else:
                    delta = randint(1000, 35000)
                    self.income += delta * k
                    self.last_job_change_date = state.current_date
                self.work_place = 'Учиетель'

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

    def try_have_children(self):
        if self.partner_id is None or self.get_age() < 20 or self.get_age() > 40 or self.criminal_record:
            return

        existing_children = self.count_children_with_partner()
        if existing_children >= 3:
            return

        if random() < 0.01:
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
                drive_card_number=None,
                eduсation='NONE',
                income=0,
                work_place=None,
                cocity_state=self.cocity_state,
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
        if self.get_age() <= 14:
            self.credit_score = 0
            return
        score = 300
        if self.partner_id: score += 20
        if self.eduсation == 'College': score += 30
        elif self.eduсation == 'University': score += 50
        score += int(self.income / 1000)
        score += int(self.balance / 1000000)
        if self.criminal_record: score -= 300
        if self.dead: score = 0
        self.credit_score = max(score, 0)
        self.credit_score = min(score, 999)

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
            self.income = 15000 + self.income*0.3

def random_name(sex):
    return choice(male_names) if sex == 'male' else choice(female_names)

def generate_patronymic(parent_name: str, child_sex: str):
    return parent_name + 'ovich' if child_sex == 'male' else parent_name + 'ovna'