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
                features = df.drop(columns=["КредитОчки"]).iloc[i].values.astype(float)
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

        scale = {
            'income': 1_000_000,
            'max_income': 1_000_000,
            'balance': 10_000_000,
            'debt': 10_000_000,
            'inheritance_account': 10_000_000,
            'monthly_payment': 100_000,
            'loans_taken': 50
        }
        for col, div in scale.items():
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) / div

        df['monthly_interest_rate'] = df['monthly_interest_rate'].clip(0, 0.2) / 0.2
        df['missed_payments'] = df['missed_payments'] / 12
        binary_features = [
            'Пенсионер', 'ВАрмии', 'Судимость', 'gave_bribe',
            'cleared_credit', 'СемейноеПоложение'
        ]
        for feat in binary_features:
            df[feat] = df[feat].astype(int)
        work_mapping = [
            'Фриланс', 'pension', 'Армия', 'IT-компания', 'Завод',
            'Госслужба', 'Бизнес', 'Учитель', 'тюрьма'
        ]
        for job in work_mapping:
            df[f'work_{job}'] = (df['Работа'] == job).astype(int)
        df.drop(columns=['Работа'], inplace=True)

        df['ДнейНаРаботе'] = df['ДнейНаРаботе'] / 3650

        type_to_num = {
            'гипертим': 1,
            'дистим': 2,
            'эмотив': 3,
            'эпилептоид': 4,
            'тревожно-мнительный': 5,
            'циклоид': 6,
            'истероид': 7,
            'вохбудимый': 8
        }

        df['ТипЛичности'] = df['ТипЛичности'].str.lower()

        df['ТипЛичности'] = df['ТипЛичности'].map(type_to_num).fillna(0).astype(int)

        df['КредитОчки'] = df['КредитОчки'] / 1000

        return df.fillna(0)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
    

all_data = load_all_people_data()
dataset = CreditSimulationDataset(all_data)

print(f"Загружено {len(all_data)} файлов с данными людей")
print(f"Всего обучающих примеров: {len(dataset)}")