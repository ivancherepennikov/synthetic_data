import datetime
import state
from dateutil.relativedelta import relativedelta


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
        self.work_place = work_place
        self.cocity_state = cocity_state
        self.criminal_record = criminal_record
        self.credit_score = credit_score
        self.partner_id = partner_id

    def get_sex(self):
        return self.sex
    
    def get_first_name(self):
        return self.first_name
    
    def get_last_name(self):
        return self.last_name
    
    def get_patronymic(self):
        return self.patroyomic
    

    def get_age(self):
        return relativedelta(state.current_date, self.birthday).years
    
    def chance_to_die(self):
        

    


    