import pandas as pd
import numpy as np
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
from sklearn.preprocessing import LabelEncoder
import os
import random

print("Загрузка оригинального файла...")
REAL_PATH = "data/CKS.csv"
df = pd.read_csv(REAL_PATH, sep=';', encoding='utf-8')

print("🧹 Подготовка данных...")

kato_df = df[['KATO_2_NAME', 'KATO_2', 'KATO_4_NAME', 'KATO_4', 'FULL_KATO_NAME']].drop_duplicates()


exclude_cols = ['KATO_2_NAME', 'KATO_2', 'KATO_4_NAME', 'KATO_4', 'FULL_KATO_NAME']
model_df = df.drop(columns=exclude_cols, errors='ignore').copy()


categoricals = model_df.select_dtypes(include='object').columns
encoders = {}
for col in categoricals:
    le = LabelEncoder()
    model_df[col] = le.fit_transform(model_df[col].astype(str))
    encoders[col] = le

print("Обучение модели GaussianCopula...")
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(model_df)

model = GaussianCopulaSynthesizer(metadata)
model.fit(model_df)

print("Генерация синтетических данных...")
synthetic = model.sample(10000)


for col, le in encoders.items():
    synthetic[col] = le.inverse_transform(synthetic[col].astype(int))

print("🔗 Добавление KATO и структуры...")
chosen_kato = kato_df.sample(n=len(synthetic), replace=True).reset_index(drop=True)
synthetic['KATO_4'] = chosen_kato['KATO_4']
synthetic['KATO_4_NAME'] = chosen_kato['KATO_4_NAME']
synthetic['KATO_2'] = chosen_kato['KATO_2']
synthetic['KATO_2_NAME'] = chosen_kato['KATO_2_NAME']
synthetic['FULL_KATO_NAME'] = chosen_kato['FULL_KATO_NAME']

#ЛОГИКА
for idx, row in synthetic.iterrows():
    
    if row['FAMILY_CAT_NEW'] == 'Многодетная':
        for i in range(1, 10):
            synthetic.at[idx, f'filtr{i}'] = '1'
        synthetic.at[idx, 'count_iin'] = random.randint(5, 10)

    
    if row['FAMILY_CAT_NEW'] == 'Малоимущая':
        for i in range(20, 28):
            synthetic.at[idx, f'filtr{i}'] = '1'
        synthetic.at[idx, 'count_iin'] = random.randint(3, 6)

    
    if row['FAMILY_CAT_NEW'] == 'Инвалид':
        synthetic.at[idx, 'filtr65'] = '1'
        for i in range(28, 31):
            synthetic.at[idx, f'filtr{i}'] = '1'

    
    num_active = sum([1 for i in list(range(1, 28)) + [65] + list(range(28, 35)) if str(row.get(f'filtr{i}', '0')) == '1'])
    synthetic.at[idx, 'Rating'] = min(5, max(1, num_active // 5))


columns_order = ['FULL_KATO_NAME', 'KATO_2_NAME', 'KATO_2', 'KATO_4_NAME', 'KATO_4'] + [
    col for col in synthetic.columns if col not in [
        'FULL_KATO_NAME', 'KATO_2_NAME', 'KATO_2', 'KATO_4_NAME', 'KATO_4']
]
synthetic = synthetic[columns_order]


OUTPUT_PATH = "data/cks_synthetic.csv"
os.makedirs("data", exist_ok=True)
synthetic.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')

print(f" Синтетические данные сохранены в: {OUTPUT_PATH}")
print(" Пример данных:")
print(synthetic.head(3))
