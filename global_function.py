import state
from random import randint
from dateutil.relativedelta import relativedelta
from person import(
    Person
)

def end_day():
    state.current_date += relativedelta(days = 1) 

    