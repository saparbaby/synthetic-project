import pandas as pd
import numpy as np
import random
from datetime import datetime
from sdv.single_table import CTGANSynthesizer
from sdv.metadata import SingleTableMetadata
from faker import Faker

fake = Faker('ru_RU')

REAL_CKS_PATH = 'data/CKS.csv'
SYNTHETIC_PATH = 'data/cks_synthetic.csv'


real_kato = pd.read_csv(REAL_CKS_PATH, sep=';', encoding='utf-8')
region_city_df = (
    real_kato[['KATO_2_NAME', 'KATO_4_NAME']]
    .dropna()
    .drop_duplicates()
    .rename(columns={'KATO_2_NAME': 'region', 'KATO_4_NAME': 'city'})
)


columns = [
    'family_id', 'region', 'city', 'address', 'family_members_count',
    'children_count', 'average_income', 'has_social_support', 'housing_type',
    'family_category', 'registration_date', 'last_update_date', 'contact_phone',
    'email', 'has_disabled_member', 'has_elderly_member', 'children_under_7',
    'children_7_18', 'working_members', 'education_level', 'health_status'
]

def generate_initial_data(num_samples=500):
    housing_types = ['квартира', 'частный дом', 'арендуемое жильё', 'общежитие']
    family_categories = ['многодетная', 'малоимущая', 'обычная', 'пенсионеры', 'инвалиды']
    education_levels = ['начальное', 'среднее', 'среднее специальное', 'высшее']
    health_statuses = ['отличное', 'хорошее', 'удовлетворительное', 'плохое']

    data = []
    for _ in range(num_samples):
        reg_date = fake.date_between(start_date='-5y', end_date='today')
        members = random.randint(1, 6)
        children = random.randint(0, min(5, members - 1)) if members > 1 else 0
        children_under_7 = random.randint(0, min(2, children))
        children_7_18 = max(0, children - children_under_7)
        working_members = random.randint(0, max(1, members - children - 1))

        data.append([
            f"FAM-{random.randint(10000, 99999)}",
            None,  
            None,  
            fake.street_address(),
            members,
            children,
            round(random.uniform(50000, 500000), 2),
            random.choice([True, False]),
            random.choice(housing_types),
            random.choice(family_categories),
            reg_date.strftime('%Y-%m-%d'),
            fake.date_between(start_date=reg_date, end_date='today').strftime('%Y-%m-%d'),
            fake.phone_number(),
            fake.email(),
            random.choice([True, False]),
            random.random() > 0.7,
            children_under_7,
            children_7_18,
            working_members,
            random.choice(education_levels),
            random.choice(health_statuses)
        ])
    return pd.DataFrame(data, columns=columns)


print("Генерация начальных данных...")
initial_data = generate_initial_data()

print(" Обучение модели CTGAN...")
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(initial_data)
model = CTGANSynthesizer(metadata=metadata, epochs=200)
model.fit(initial_data)

print("Генерация синтетических данных...")
synthetic_data = model.sample(10000)


print(" Подстановка логически корректных регионов и городов...")
random_choices = region_city_df.sample(n=len(synthetic_data), replace=True).reset_index(drop=True)
synthetic_data['region'] = random_choices['region']
synthetic_data['city'] = random_choices['city']

#Постобработка логики
for idx, row in synthetic_data.iterrows():
    members = row['family_members_count']
    children = row['children_count']
    adults = members - children

    if children > members:
        synthetic_data.at[idx, 'children_count'] = random.randint(0, max(0, members-1)) if members > 1 else 0

    if row['family_category'] == 'многодетная':
        synthetic_data.at[idx, 'children_count'] = random.randint(3, min(5, members-1)) if members > 3 else members

    if row['family_category'] == 'малоимущая' and random.random() > 0.2:
        synthetic_data.at[idx, 'has_social_support'] = True

    if row['family_category'] == 'инвалиды':
        synthetic_data.at[idx, 'has_disabled_member'] = True

    if row['family_category'] == 'пенсионеры':
        synthetic_data.at[idx, 'has_elderly_member'] = True

    total_children = row['children_under_7'] + row['children_7_18']
    if total_children > children:
        children_under_7 = random.randint(0, children)
        synthetic_data.at[idx, 'children_under_7'] = children_under_7
        synthetic_data.at[idx, 'children_7_18'] = children - children_under_7

    if adults > 0 and row['working_members'] > adults:
        synthetic_data.at[idx, 'working_members'] = random.randint(0, adults)
    elif adults <= 0:
        synthetic_data.at[idx, 'working_members'] = 0

    if row['average_income'] > 300000 and random.random() > 0.1:
        synthetic_data.at[idx, 'has_social_support'] = False

    if row['housing_type'] == 'арендуемое жильё' and random.random() > 0.3:
        synthetic_data.at[idx, 'family_category'] = 'малоимущая'

    if row['average_income'] > 400000:
        synthetic_data.at[idx, 'health_status'] = random.choice(['отличное', 'хорошее'])

    if row['has_disabled_member']:
        synthetic_data.at[idx, 'health_status'] = random.choice(['удовлетворительное', 'плохое'])

    if row['average_income'] > 300000:
        synthetic_data.at[idx, 'education_level'] = random.choice(['среднее специальное', 'высшее'])

    if row['family_category'] == 'многодетная' and random.random() > 0.4:
        synthetic_data.at[idx, 'housing_type'] = 'частный дом'

    reg_date = pd.to_datetime(row['registration_date'])
    last_update = pd.to_datetime(row['last_update_date'])
    if last_update < reg_date:
        new_date = fake.date_between_dates(date_start=reg_date, date_end=datetime.now())
        synthetic_data.at[idx, 'last_update_date'] = new_date.strftime('%Y-%m-%d')

    if adults > 0 and row['children_under_7'] > 0 and row['working_members'] == adults:
        synthetic_data.at[idx, 'working_members'] = max(0, adults - 1)


print(f"\n Сохраняем в файл: {SYNTHETIC_PATH}")
synthetic_data.to_csv(SYNTHETIC_PATH, index=False, encoding='utf-8-sig')


print("\n Статистика:")
print(synthetic_data.describe())

print("\n Распределение по регионам:")
print(synthetic_data['region'].value_counts())

print("\n Категории семей:")
print(synthetic_data['family_category'].value_counts())

print("\n Уровень образования:")
print(synthetic_data['education_level'].value_counts())
