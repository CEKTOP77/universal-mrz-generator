import streamlit as st

# === функция расчета контрольной цифры (по ICAO DOC 9303) ===
def mrz_check_digit(data: str) -> str:
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === преобразование даты (ДДММГГ -> ГГММДД) ===
def convert_date(date_str: str) -> str:
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

# === универсальная генерация MRZ с Extra Info ===
def generate_mrz(doc_type, country, lastname, firstname, doc_number, nationality, birth, expiry, sex, extra_info, format_type):
    # Приведение данных и очистка
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")

    # Даты
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # Контрольные цифры
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # Формат TD3 (паспорт 2×44)
    if format_type == "TD3 (Паспорт, 2x44)":
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        optional_data = extra_info.ljust(14, "<")[:14]
        line2_base = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        total_cd = mrz_check_digit(line2_base)
        line2 = (line2_base + total_cd).ljust(44, "<")[:44]
        return [line1, line2], total_cd

    # Формат TD1 (ID-карта 3×30)
    elif format_type == "TD1 (ID-карта, 3x30)":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base_line2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        line2_temp = base_line2.ljust(29, "<")[:29]
        total_cd = mrz_check_digit(line1 + line2_temp)
        line2 = (line2_temp + total_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3], total_cd

    else:
        raise ValueError("Неизвестный тип формата")


# === Веб-интерфейс Streamlit ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")

st.title("🌍 Универсальный MRZ Генератор (по стандарту ICAO DOC 9303)")
st.markdown("Создает MRZ для паспортов (TD3) и ID-карт (TD1), поддерживает поле **Extra Info** для дополнительных данных.")

# выбор формата документа
format_type = st.selectbox("Выберите формат документа:", ["TD3 (Паспорт, 2x44)", "TD1 (ID-карта, 3x30)"])

# поля ввода
doc_type = st.text_input("Тип документа (P, ID, V и т.п.)", value="P")
country = st.text_input("Код страны (3 буквы)", value="DEU")
lastname = st.text_input("Фамилия", value="MUSTER")
firstname = st.text_input("Имя", value="MAX")
doc_number = st.text_input("Номер документа", value="C01X00T47")
nationality = st.text_input("Национальность", value="DEU")
birth = st.text_input("Дата рождения (ДДММГГ)", value="261293")
expiry = st.text_input("Срок действия (ДДММГГ)", value="120832")
sex = st.selectbox("Пол", ["M", "F", "<"])
extra_info = st.text_input("Extra Info (дополнительные данные, до 14 символов)", value="CUSTOMDATA")

# кнопка генерации MRZ
if st.button("Сгенерировать MRZ"):
    try:
        lines, checksum = generate_mrz(doc_type, country, lastname, firstname, doc_number, nationality, birth, expiry, sex, extra_info, format_type)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(lines), language="text")
        st.text(f"Финальная контрольная цифра MRZ: {checksum}")
        st.markdown("---")
        st.markdown("### 💳 Предпросмотр MRZ блока")
        st.markdown(
            f"""
            <div style="border:1px solid #888;background:#e0e0e0;padding:15px;width:670px;border-radius:6px;">
                <div style="background:#fff;padding:10px;font-family:Courier;">
                    <pre style="font-weight:bold;margin:0;line-height:1.2em;">
{'\n'.join(lines)}
                    </pre>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Ошибка: {e}")
