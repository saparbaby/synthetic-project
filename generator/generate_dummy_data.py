import pandas as pd
import numpy as np
from faker import Faker
from datetime import timedelta
import random

fake = Faker("ru_RU")
np.random.seed(42)
Faker.seed(42)

n = 10000
output_dir = "data"  

regions = [
    "Абайская", "Актюбинская", "Алматинская", "Атырауская", "ВКО", "Жамбылская",
    "Жетысуская", "ЗКО", "Карагандинская", "Костанайская", "Кызылординская",
    "Мангистауская", "Павлодарская", "СКО", "Туркестанская", "Улытауская", "Шымкент",
    "Астана", "Алматы"
]


statuses = ["В работе", "Завершено", "Отказано", "На рассмотрении"]
citizenships = ["КАЗАХСТАН", "РОССИЯ", "УЗБЕКИСТАН"]
genders = ["Мужской", "Женский"]
issues = ["Жилищный вопрос", "Социальное обеспечение", "Здравоохранение", "Земельные отношения", "Предпринимательство"]
appeal_types = ["Заявление", "Жалоба", "Предложение", "Запрос"]
decisions = ["Предоставить ответ", "Принять благоприятный акт", "Отказ", "Рассмотрено"]
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

data_eobr = []
for _ in range(n):
    start_dt = fake.date_time_between(start_date='-2y', end_date='now')
    deadline = start_dt + timedelta(days=random.randint(7, 30))
    finish_dt = start_dt + timedelta(days=random.randint(3, 40))
    data_eobr.append({
        "fake_iin_bin": fake.random_number(12, fix_len=True),
        "appeal_id": fake.random_number(14, fix_len=True),
        "reg_number": fake.bothify(text='ЖТ-####-#######'),
        "current_working_state": random.choice(statuses),
        "status_overdue": random.choice(statuses),
        "applicant_type": random.choice(["Физическое лицо", "Юридическое лицо"]),
        "person_age": random.randint(18, 85),
        "citizenship": random.choice(citizenships),
        "gender": random.choice(genders),
        "issue": random.choice(issues),
        "appeal_type": random.choice(appeal_types),
        "region": random.choice(regions),
        "start_dt": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "finish_dt": finish_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "appeal_decision": random.choice(decisions),
        "month_name": random.choice(months),
        "mark": random.choice(["", "Хорошо", "Удовлетворительно", "Плохо"])
    })

df_eobr = pd.DataFrame(data_eobr)
df_eobr.to_csv(f"{output_dir}/e_obr_dummy.csv", index=False, sep=";")


categories = [
    "Социально-уязвимые", "Госслужащие", "Пенсионеры", "Неполные семьи", "Многодетные семьи"
]
subcategories = [
    "Лица с инвалидностью", "Неполная семья", "Семьи с детьми-инвалидами",
    "Малообеспеченные", "Пенсионеры по возрасту"
]
real_estate_status = ["Есть недвижимость", "Нет недвижимости"]
dead_status = ["Живой", "Умер"]
criteria_result = ["Соответствует", "Не соответствует", "Частично соответствует"]
family_categories = ["A", "B", "C", "D"]
address_status = ["Есть прописка", "Нет прописки"]

data_kz = []
for _ in range(n):
    req_date = fake.date_time_between(start_date='-2y', end_date='now')
    queue_date = req_date - timedelta(days=random.randint(30, 1500))
    data_kz.append({
        "FAKE_IIN": fake.random_number(12, fix_len=True),
        "FLREQUESTDATE": req_date.strftime("%Y-%m-%d %H:%M:%S"),
        "FLQUEUEDATE": queue_date.strftime("%Y-%m-%d %H:%M:%S"),
        "FLCATEGORY": random.choice(categories),
        "FLSUBCATEGORY": random.choice(subcategories),
        "FLQUEUENUMBER": random.randint(1, 9999),
        "N_APPLICATIONS": random.randint(1, 5),
        "IN_FL": "ИИН есть в реестре ФЛ",
        "ADDRESS_REGISTRATION_STATUS": random.choice(address_status),
        "REGION_APPLICANT": random.choice(regions),
        "REAL_ESTATE_STATUS": random.choice(real_estate_status),
        "DEAD_STATUS": random.choice(dead_status),
        "N_CRITERIA_FAILED": random.randint(0, 3),
        "STATUS_FAILED": random.choice(criteria_result),
        "SK_FAMILY_ID": fake.random_number(8, fix_len=True),
        "FAMILY_CAT_NEW": random.choice(family_categories),
        "CNT_MEM": random.randint(1, 10),
        "SDU_LOAD_IN_DT": fake.date_time_between(start_date='-30d', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
    })

df_kz = pd.DataFrame(data_kz)
df_kz.to_csv(f"{output_dir}/kezekte_dummy.csv", index=False, sep=";")

print(" Файлы успешно созданы в папке data/")
