import os
import pandas as pd
import glob
import torch
from torch.utils.data import Dataset

def load_all_people_data(directory="people_statistic"):
    """Загружает все CSV-файлы людей из указанной директории"""
    all_files = glob.glob(os.path.join(directory, "person_*.csv"))
    people_data = []
    
    for file in all_files:
        try:
            df = pd.read_csv(file, delimiter=";")
            people_data.append(df)
        except Exception as e:
            print(f"Ошибка при чтении файла {file}: {str(e)}")
    
    return people_data

class CreditSimulationDataset(Dataset):
    def __init__(self, people_dataframes):
        self.samples = []
        
        for df in people_dataframes:
            df = self.preprocess(df)
            for i in range(len(df)):
                features = df.iloc[i].drop("КредитОчки", errors='ignore').values.astype(float)
                target = df.iloc[i]["КредитОчки"]
                self.samples.append((features, target))
    
    def preprocess(self, df):

        df['Пол'] = df['Пол'].map({'female': 0, 'male': 1}).fillna(-1)
        
        df['Возраст'] = df['Возраст'] / 100
        
        education_mapping = {
            'NONE': 0,
            'School': 0.25,
            'HIGH SCHOOL': 0.5,
            'College': 0.75,
            'University': 1.0
        }
        df['Образование'] = df['Образование'].map(education_mapping).fillna(0)
        
        financial_features = {
            'income': 1_000_000,
            'max_income': 1_000_000,
            'balance': 10_000_000,
            'debt': 10_000_000,
            'inheritance_account': 10_000_000,
            'monthly_payment': 100_000,
            'loans_taken': 50 
        }
        
        for feat, divisor in financial_features.items():
            df[feat] = df[feat].abs() / divisor 
    
        df['monthly_interest_rate'] = df['monthly_interest_rate'].clip(0, 0.2) / 0.2
        
        df['missed_payments'] = df['missed_payments'] / 12 
        
        binary_features = [
            'Пенсионер', 'ВАрмии', 'Судимость', 'gave_bribe',
            'cleared_credit', 'СемейноеПоложение'
        ]
        for feat in binary_features:
            df[feat] = df[feat].astype(int)
        
        work_mapping = {
            'Фриланс': 0,
            'pension': 1,
            'Армия': 2,
            'IT-компания': 3,
            'Завод': 4,
            'Госслужба': 5,
            'Бизнес': 6,
            'Учитель': 7,
            'тюрьма': 8,
            None: 9
        }
        df['Работа'] = df['Работа'].map(work_mapping).fillna(9)
        
        df['ДнейНаРаботе'] = df['ДнейНаРаботе'] / 3650
        df['КредитОчки'] = df['КредитОчки'] / 1000
        
        features = [
            'Пол', 'Возраст', 'Образование',
            'income', 'max_income', 'balance', 'debt',
            'inheritance_account', 'monthly_payment', 'loans_taken',
            'monthly_interest_rate', 'missed_payments', 'cleared_credit',
            'Работа', 'ДнейНаРаботе', 'Пенсионер', 'ВАрмии',
            'Судимость', 'gave_bribe', 'СемейноеПоложение',
            'КредитОчки'
        ]
        
        return df[features].fillna(0)
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        x, y = self.samples[idx]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

all_data = load_all_people_data()
dataset = CreditSimulationDataset(all_data)

print(f"Загружено {len(all_data)} файлов с данными людей")
print(f"Всего обучающих примеров: {len(dataset)}")