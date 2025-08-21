from datetime import datetime

current_date = datetime(year = 2025, month = 7, day = 23)

people = []

years = 300
max_population = 100
logistic_r = 3.2
key_court = 0.1

salary_up_r = 0.06/12
salary_up_A = 0.05
salary_up_T = 12
salary_up_year = -1
salary_up_index = 1.0



#инфляция
inflation_r = 0.07/12
inflation_A = 0.05
inflation_T = 12
inflation_year = -1
inflation_index = 1.0

MAX_INCOME = 1e7


#мысль с природными ресурсами
oil_amount_per_person = 2_700_000_000 / 8_142_000_000
oil_in_simulation = oil_amount_per_person * max_population * years * 12

car_amaunt = 0
