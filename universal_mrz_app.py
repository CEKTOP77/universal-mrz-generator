import streamlit as st

# === функция расчета контрольной цифры (ICAO DOC 9303) ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === конвертация даты ДДММГГ → ГГММДД ===
def convert_date(date_str: str) -> str:
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

# === генерация MRZ ===
def generate_mrz(
        format_type, doc_type, country, nationality,
        lastname, firstname, doc_number,
        birth, expiry, sex, extra_info):

    # Нормализация вводимых значений
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    country = country.upper()
    nationality = nationality.upper()
    doc_number = doc_number.upper()
    birth = convert_date(birth)
    expiry = convert_date(expiry)
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")

    # Контрольные цифры для отдельных полей
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # === ПАСПОРТ TD3 (2 строки × 44 символа) ===
    if format_type == "TD3 (Паспорт, 2x44)":
        # Первая строка: тип документа, страна выдачи, фамилия и имя
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]

        # Вторая строка: поля и контрольные цифры
        optional_data = extra_info.ljust(14, "<")[:14]
        line2_body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        final_cd = mrz_check_digit(line2_body)
        line2 = (line2_body + final_cd)
        if len(line2) < 44:
            line2 = line2.ljust(44, "<")
        elif len(line2) > 44:
            line2 = line2[:44]
        return [line1, line2], final_cd

    # === ID TD1 (3 строки × 30 символов) ===
    elif format_type == "TD1 (ID-карта, 3x30)":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base_line2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp_line2 = base_line2.ljust(29, "<")
        final_cd = mrz_check_digit(line1 + temp_line2)
        line2 = (temp_line2 + final_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3], final_cd

    else:
        raise ValueError("Неверный формат документа. Выберите TD3 или TD1.")


# === Веб-интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")

st.title("🌍 Универсальный MRZ Генератор (ICAO DOC 9303)")
st.markdown("""
Создаёт MRZ для **любой страны** (не зависит от Германии или другого государства)  
по международному стандарту **ICAO DOC 9303**.  
Поддерживает форматы **TD3 (паспорта)** и **TD1 (ID‑карты)**,  
а также дополнительное поле **Extra Info**.
""")

# Ввод данных
format_type = st.selectbox("Выберите формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID-карта, 3x30)"])
doc_type = st.text_input("Тип документа (P, ID, V и т.п.)", value="P")
country = st.text_input("Код страны выдачи (3 буквы)", value="USA")
nationality = st.text_input("Гражданство (3 буквы)", value="USA")
lastname = st.text_input("Фамилия", value="HULTON")
firstname = st.text_input("Имя (можно через пробел)", value="DAVID NAKAMURA")
doc_number = st.text_input("Номер документа", value="A09913982")
birth = st.text_input("Дата рождения (ДДММГГ)", value="190383")
expiry = st.text_input("Дата окончания (ДДММГГ)", value="180133")
sex = st.selectbox("Пол", ["M", "F", "<"], index=0)
extra_info = st.text_input("Extra Info (до 14 символов)", value="534397504")

if st.button("Сгенерировать MRZ"):
    try:
        lines, checksum = generate_mrz(format_type, doc_type, country, nationality,
                                       lastname, firstname, doc_number,
                                       birth, expiry, sex, extra_info)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(lines), language="text")
        st.text(f"Контрольная цифра MRZ (всего блока): {checksum}")
        st.markdown("---")
        st.markdown("### 💳 Предпросмотр MRZ блока")
        st.markdown(
            f"""
            <div style="border:1px solid #888;background:#e0e0e0;padding:15px;width:680px;border-radius:6px;">
                <div style="background:#fff;padding:10px;font-family:Courier;">
                    <pre style="font-weight:bold;margin:0;line-height:1.2em;">
{'\n'.join(lines)}
                    </pre>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
