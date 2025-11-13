import streamlit as st

# === функция расчёта контрольной цифры ===
def mrz_check_digit(data: str) -> str:
    """Контрольная цифра (7‑3‑1 ICAO DOC 9303)"""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

# === преобразование формата даты ===
def convert_date(date_str: str) -> str:
    """ДДММГГ → ГГММДД"""
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

# === генерация MRZ ===
def generate_mrz(format_type, doc_type, country, nationality,
                 lastname, firstname, doc_number,
                 birth, expiry, sex, extra_info):

    lastname  = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные цифры
    doc_cd    = mrz_check_digit(doc_number)
    birth_cd  = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # === TD3 – паспорт ===
    if format_type == "TD3 (Паспорт, 2x44)":
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        optional_data = extra_info.ljust(14, "<")[:14]
        line2_body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        final_cd = mrz_check_digit(line2_body)
        line2 = (line2_body + final_cd).ljust(44, "<")[:44]
        return [line1, line2]

    # === TD1 – ID‑карта ===
    elif format_type == "TD1 (ID‑карта, 3x30)":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp2 = base2.ljust(29, "<")
        final_cd = mrz_check_digit(line1 + temp2)
        line2 = (temp2 + final_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    else:
        raise ValueError("Неверный формат документа")


# === Streamlit‑интерфейс ===
st.set_page_config(page_title="Универсальный MRZ Генератор", layout="centered")
st.title("🌍 Универсальный MRZ‑генератор (ICAO DOC 9303)")

# инициализация session_state (для очистки)
if "reset" not in st.session_state:
    st.session_state.reset = False

# кнопка очистки (расположим рядом с кнопкой "Сгенерировать")
def clear_fields():
    st.session_state.doc_type = ""
    st.session_state.country = ""
    st.session_state.nationality = ""
    st.session_state.lastname = ""
    st.session_state.firstname = ""
    st.session_state.doc_number = ""
    st.session_state.birth = ""
    st.session_state.expiry = ""
    st.session_state.sex = "M"
    st.session_state.extra_info = ""
    st.session_state.reset = not st.session_state.reset

# поля данных
format_type = st.selectbox("Формат документа", ["TD3 (Паспорт, 2x44)", "TD1 (ID‑карта, 3x30)"], index=0)
doc_type = st.text_input("Тип документа (P, ID, V и т.п.)", value=st.session_state.get("doc_type", "P"), key="doc_type")
country = st.text_input("Код страны выдачи (3 буквы)", value=st.session_state.get("country", "USA"), key="country")
nationality = st.text_input("Гражданство (3 буквы)", value=st.session_state.get("nationality", "USA"), key="nationality")
lastname = st.text_input("Фамилия", value=st.session_state.get("lastname", "HULTON"), key="lastname")
firstname = st.text_input("Имя (можно через пробел)", value=st.session_state.get("firstname", "DAVID NAKAMURA"), key="firstname")
doc_number = st.text_input("Номер документа", value=st.session_state.get("doc_number", "A09913982"), key="doc_number")
birth = st.text_input("Дата рождения (ДДММГГ)", value=st.session_state.get("birth", "190383"), key="birth")
expiry = st.text_input("Дата окончания (ДДММГГ)", value=st.session_state.get("expiry", "180133"), key="expiry")
sex = st.selectbox("Пол", ["M", "F", "<"], index=["M", "F", "<"].index(st.session_state.get("sex", "M")), key="sex")
extra_info = st.text_input("Extra Info (до 14 символов)", value=st.session_state.get("extra_info", "534397504"), key="extra_info")

# кнопки действий
col1, col2 = st.columns(2)
with col1:
    gen = st.button("📄 Сгенерировать MRZ")
with col2:
    clr = st.button("🧹 Очистить все поля", on_click=clear_fields)

# логика генерации
if gen:
    try:
        lines = generate_mrz(format_type, doc_type, country, nationality,
                             lastname, firstname, doc_number,
                             birth, expiry, sex, extra_info)
        st.success("✅ MRZ успешно сгенерирован!")
        st.code("\n".join(lines), language="text")
        st.markdown(
            f"""
            <div style='border:1px solid #999;background:#e0e0e0;padding:15px;width:680px;border-radius:6px;'>
                <div style='background:#fff;padding:10px;font-family:Courier;'>
                    <pre style='font-weight:bold;margin:0;line-height:1.2em;'>{'\n'.join(lines)}</pre>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Ошибка: {e}")
