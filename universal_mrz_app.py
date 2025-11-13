# UNIVERSAL MRZ GENERATOR (by ICAO DOC 9303)
# Работает для всех стран и типов документов TD1 / TD3

def mrz_check_digit(data: str) -> str:
    """Вычисление контрольной цифры MRZ (алгоритм 7-3-1 ICAO DOC 9303)"""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(data):
        total += values.get(ch, 0) * weights[i % 3]
    return str(total % 10)


def convert_date(date_str: str) -> str:
    """Преобразует дату ДДММГГ в формат ГГММДД"""
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str


def generate_mrz(
    format_type="TD3",
    doc_type="P",
    country="XXX",
    nationality="XXX",
    lastname="SURNAME",
    firstname="GIVENNAME",
    doc_number="A0000000",
    birth="010199",
    expiry="010199",
    sex="M",
    extra_info=""
):
    """
    Генерирует MRZ по стандарту ICAO DOC 9303.
    format_type: 'TD3' (паспорт) или 'TD1' (ID-карта)
    """
    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    extra_info = extra_info.upper().replace(" ", "<")
    sex = sex.upper() if sex else "<"
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные цифры
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # формат TD3 ─ паспорта
    if format_type.upper() == "TD3":
        # первая строка
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        # вторая строка
        optional_data = extra_info.ljust(14, "<")[:14]
        body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional_data}"
        total_cd = mrz_check_digit(body)
        line2 = (body + total_cd).ljust(44, "<")[:44]
        return [line1, line2]

    # формат TD1 ─ ID-карты
    elif format_type.upper() == "TD1":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        line2_body = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp_line2 = line2_body.ljust(29, "<")
        total_cd = mrz_check_digit(line1 + temp_line2)
        line2 = (temp_line2 + total_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    else:
        raise ValueError("Укажите правильный формат: TD3 или TD1")


# =====================
# ======= DEMO ========
# =====================
if __name__ == "__main__":
    # Пример 1: Паспорт (TD3)
    mrz_td3 = generate_mrz(
        format_type="TD3",
        doc_type="P",
        country="USA",
        nationality="USA",
        lastname="HULTON",
        firstname="DAVID NAKAMURA",
        doc_number="A09913982",
        birth="190383",
        expiry="180133",
        sex="M",
        extra_info="534397504"
    )

    print("=== MRZ TD3 (Паспорт) ===")
    for line in mrz_td3:
        print(line)

    print("\n" + "="*50 + "\n")

    # Пример 2: ID‑карта (TD1)
    mrz_td1 = generate_mrz(
        format_type="TD1",
        doc_type="ID",
        country="DEU",
        nationality="DEU",
        lastname="MUSTER",
        firstname="MAX",
        doc_number="L3H8HG5CY",
        birth="261293",
        expiry="120832",
        sex="<",
        extra_info="2108"
    )

    print("=== MRZ TD1 (ID‑карта) ===")
    for line in mrz_td1:
        print(line)
