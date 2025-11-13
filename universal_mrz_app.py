# === UNIVERSAL MRZ GENERATOR ===
# Совместим со всеми странами (форматы TD3 и TD1)

def mrz_check_digit(data: str) -> str:
    """Расчет контрольной цифры по ICAO DOC 9303"""
    values = {**{str(i): i for i in range(10)},
              **{chr(i + 55): i for i in range(10, 36)},
              '<': 0}
    weights = [7, 3, 1]
    total = sum(values.get(ch, 0) * weights[i % 3] for i, ch in enumerate(data))
    return str(total % 10)

def convert_date(date_str: str) -> str:
    """ДДММГГ -> ГГММДД"""
    if len(date_str) == 6:
        d, m, y = date_str[:2], date_str[2:4], date_str[4:6]
        return y + m + d
    return date_str

def generate_mrz(format_type="TD3", doc_type="P", country="USA", nationality="USA",
                 lastname="HULTON", firstname="DAVID NAKAMURA", doc_number="A09913982",
                 birth="190383", expiry="180133", sex="M", extra_info="534397504"):
    """Генерация MRZ для TD3 (паспорт) и TD1 (ID-карта)"""

    lastname = lastname.upper().replace(" ", "<")
    firstname = firstname.upper().replace(" ", "<")
    doc_number = doc_number.upper()
    country = country.upper()
    nationality = nationality.upper()
    sex = sex.upper() if sex else "<"
    extra_info = extra_info.upper().replace(" ", "<")
    birth = convert_date(birth)
    expiry = convert_date(expiry)

    # контрольные цифры
    doc_cd = mrz_check_digit(doc_number)
    birth_cd = mrz_check_digit(birth)
    expiry_cd = mrz_check_digit(expiry)

    # ===== PASSPORT TD3 =====
    if format_type.upper() == "TD3":
        line1 = f"{doc_type}<{country}{lastname}<<{firstname}".ljust(44, "<")[:44]
        optional = extra_info.ljust(14, "<")[:14]
        body = f"{doc_number}{doc_cd}{nationality}{birth}{birth_cd}{sex}{expiry}{expiry_cd}{optional}"
        total_cd = mrz_check_digit(body)
        line2 = (body + total_cd).ljust(44, "<")[:44]
        return [line1, line2]

    # ===== ID CARD TD1 =====
    elif format_type.upper() == "TD1":
        line1 = f"{doc_type}<{country}{doc_number}{doc_cd}".ljust(30, "<")[:30]
        base2 = f"{birth}{birth_cd}{sex}{expiry}{expiry_cd}{nationality}{extra_info[:14]}"
        temp2 = base2.ljust(29, "<")
        total_cd = mrz_check_digit(line1 + temp2)
        line2 = (temp2 + total_cd)[:30]
        line3 = f"{lastname}<<{firstname}".ljust(30, "<")[:30]
        return [line1, line2, line3]

    else:
        raise ValueError("Неверный формат: выбери 'TD3' или 'TD1'")

# ===== MAIN TEST =====
if __name__ == "__main__":
    mrz = generate_mrz(
        format_type="TD3",   # TD3 или TD1
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

    print("=== MRZ CODE ===")
    for line in mrz:
        print(line)
