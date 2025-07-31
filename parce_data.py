import os
import pandas as pd
import glob
import torch
from torch.utils.data import Dataset

def load_all_people_data(directory="people_statistic_2"): #_2
    all_files = glob.glob(os.path.join(directory, "person_*.csv"))
    people_data = []

    for file in all_files:
        df = pd.read_csv(file, delimiter=";")

        date_cols = [
            "ДатаРождения", "ДатаСмерти", "ДатаСменыРаботы",
            "ОсвобождёнИзТюрьмы", "ДатаОсвобожденияИзАрмии"
        ]

        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")

        df.sort_values("ДатаСменыРаботы", inplace=True)
        people_data.append(df)

    return people_data



class CreditSimulationDataset(Dataset):
    def __init__(self, people_dataframes):
        self.samples = []

        for df in people_dataframes:
            df = self.preprocess(df)
            for i in range(len(df)):
                x = df.iloc[i].drop("КредитОчки").values.astype(float)
                y = df.iloc[i]["КредитОчки"]
                self.samples.append((x, y))

    def preprocess(self, df):
        df['Пол'] = df['Пол'].map({'male': 0, 'female': 1}).fillna(-1)
        df['Образование'] = df['Образование'].astype('category').cat.codes
        df['Работа'] = df['Работа'].astype('category').cat.codes
        df['Судимость'] = df['Судимость'].astype(int)
        df['Пенсионер'] = df['Пенсионер'].astype(int)
        df['ВАрмии'] = df['ВАрмии'].astype(int)
        df['Умер'] = df['Умер'].astype(int)

        df["Доход"] = df["Доход"] / 100_000
        df["МаксДоход"] = df["МаксДоход"] / 100_000
        df["Баланс"] = df["Баланс"] / 1_000_000_000
        df["Наследство"] = df["Наследство"] / 1_000_000_000
        df["Долг"] = df["Долг"] / 1_000_000_000
        df["КредитОчки"] = df["КредитОчки"] / 1000

        used_features = [
            "Доход", "МаксДоход", "Баланс", "Судимость",
            "Пенсионер", "ВАрмии", "Пол", "Образование", "Работа",
            "Наследство", "Долг", "КредитОчки"
        ]

        df = df[used_features].fillna(0)
        return df

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]
        x = torch.tensor(x, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.float32)
        return x, y





all_data = load_all_people_data()
dataset = CreditSimulationDataset(all_data)

print(f"Загружено {len(all_data)} человек")
print(f"Всего обучающих примеров: {len(dataset)}")


