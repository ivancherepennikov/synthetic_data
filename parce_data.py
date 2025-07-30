import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import torch
from torch.utils.data import Dataset, DataLoader
from datetime import datetime

# === Шаг 1: Загрузка данных ===
# Используем строку вместо файла для примера (в вашем случае оставьте путь к файлу)
data = """ID;Пол;Имя;Фамилия;Отчество;Отец_ID;Мать_ID;ИНН;СНИЛС;ДатаРождения;Паспорт;Образование;Доход;МаксДоход;Баланс;Работа;Судимость;КредитОчки;Партнёр_ID;Умер;ДатаСмерти;ДатаСменыРаботы;ОсвобождёнИзТюрьмы;Пенсионер;ВАрмии;ДатаОсвобожденияИзАрмии;Наследство;Долг
1;male;Ivan;Cherepennikov;Valerevic;;;98398;83978130;2006-02-12;52;College;50000;0;47705;Бизнес;False;382;2;False;;2025-07-23;;False;False;;-48588;0
1;male;Ivan;Cherepennikov;Valerevic;;;98398;83978130;2006-02-12;52;College;50000;0;105748;Бизнес;False;382;2;False;;2025-07-23;;False;False;;-96236;0"""
df = pd.read_csv("/Users/ivancerepennikov/live_simulator/people_statistic/person_1.csv", sep=";")

# === Шаг 2: Очистка ===
drop_cols = ['ID', 'Имя', 'Фамилия', 'Отчество', 'Паспорт', 'ИНН', 'СНИЛС']
df = df.drop(columns=[col for col in drop_cols if col in df.columns])

# === Шаг 3: Обработка дат ===
today = pd.to_datetime("2025-07-30")
date_cols = ['ДатаРождения', 'ДатаСмерти', 'ДатаСменыРаботы', 'ДатаОсвобожденияИзАрмии']
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = (today - df[col]).dt.days
        df[col] = df[col].fillna(-1)

# === Шаг 4: Категориальные → числовые ===
cat_cols = [col for col in df.select_dtypes(include='object').columns if col != 'КредитОчки']
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))

# === Шаг 5: Обработка КредитОчки ===
# Заменяем пустые строки и преобразуем в float
df['КредитОчки'] = df['КредитОчки'].replace('', np.nan).astype(float)

# Удаляем строки с пропусками в целевой переменной
df = df.dropna(subset=['КредитОчки'])

print("Уникальные значения КредитОчки после обработки:", df['КредитОчки'].unique())

# Целевые переменные
y_regression = df['КредитОчки'].values.astype(np.float32)
y_classification = (df['КредитОчки'] >= 400).astype(np.float32)  # 1 = можно дать кредит

# === Шаг 6: Признаки ===
X = df.drop(columns=['КредитОчки'])

# === Шаг 7: Заполнение NaN и масштабирование ===
X = X.fillna(-1)  # можно заменить на средние/медианы по необходимости
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X.values.astype(np.float32))

# === Шаг 8: Кастомный PyTorch Dataset ===
class CreditDataset(Dataset):
    def __init__(self, X, y_reg, y_class):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y_reg = torch.tensor(y_reg, dtype=torch.float32).unsqueeze(1)
        self.y_class = torch.tensor(y_class, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y_reg[idx], self.y_class[idx]

# === Шаг 9: DataLoader ===
dataset = CreditDataset(X_scaled, y_regression, y_classification)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# === Шаг 10: Проверка ===
for x, y_reg, y_cls in loader:
    print("\nПример загруженных данных:")
    print("Размерность признаков (X shape):", x.shape)
    print("Первые 5 значений КредитОчки (регрессия):", y_reg[:5].squeeze().tolist())
    print("Первые 5 значений Можно давать кредит (классификация):", y_cls[:5].squeeze().tolist())
    print("\nПервые 5 строк масштабированных признаков:")
    print(x[:5])
    break

# Дополнительная проверка
print("\nДополнительная информация:")
print("Количество записей:", len(dataset))
print("Количество признаков:", X.shape[1])
print("Распределение классов (0/1):", np.bincount(y_classification.astype(int)))