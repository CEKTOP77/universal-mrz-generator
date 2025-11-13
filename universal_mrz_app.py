import streamlit as st

# === расчет контрольной цифры ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    return str(sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data)) % 10)

# === преобразование даты (ДДММГГ → ГГММДД) ===
def convert_date(date_str: str) -> str:
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

# === генерация MRZ ===
def generate_mrz(format_type, doc_type, country, nationality,
                 lastname, firstname, doc_number,
                 birth, expiry, sex, extra_info):
    # нормализация значений
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные числа
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # === паспорт TD3 ===
    if format_type == "TD3 (Паспорт, 2x44)":
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        optional_data = extra_info.ljust(14, "<")[:14]
        body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        total_cd = mrz_check_digit(body)
        line2 = (body + total_cd).ljust(44, "<")[:44]
        return [line1, line2]

    # === ID TD1 ===
    elif format_type == "TD1 (ID‑карта, 3x30)":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp2 = base2.ljust(29, "<")
        total_cd = mrz_check_digit(line1 + temp2)
        line2 = (temp2 + total_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    else:
        raise ValueError("Неизвестный формат документа")

# ====== стримлит‑интерфейс ======
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")

st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")
st.caption("Создаёт MRZ‑код для всех стран. Поддерживает форматы TD3 (паспорт) и TD1 (ID‑карта).")

format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID‑карта, 3x30)"], index=0)
doc_type = st.text_input("Тип документа (P, ID, V и т.п.)", "P")
country = st.text_input("Код страны (3 буквы)", "USA")
nationality = st.text_input("Гражданство (3 буквы)", "USA")
lastname = st.text_input("Фамилия", "HULTON")
firstname = st.text_input("Имя (можно через пробел)", "DAVID NAKAMURA")
doc_number = st.text_input("Номер документа", "A09913982")
birth = st.text_input("Дата рождения (ДДММГГ)", "190383")
expiry = st.text_input("Дата окончания (ДДММГГ)", "180133")
sex = st.selectbox("Пол", ["M", "F", "<"])
extra_info = st.text_input("Extra Info (до 14 символов)", "534397504")

if st.button("📄 Сгенерировать MRZ"):
    try:
        lines = generate_mrz(format_type, doc_type, country, nationality,
                             lastname, firstname, doc_number,
                             birth, expiry, sex, extra_info)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(lines), language="text")
        st.markdown("---")
        st.markdown("### 💳 Предпросмотр")
        st.markdown(
            f"""
            <div style='border:1px solid #888;background:#e0e0e0;padding:15px;width:680px;border-radius:6px;'>
                <div style='background:#fff;padding:10px;font-family:Courier;'>
                    <pre style='font-weight:bold;margin:0;line-height:1.2em;'>{'\n'.join(lines)}</pre>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Ошибка: {e}")
