from __future__ import annotations

from datetime import date, datetime


STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_META = {
    "甲": {"element": "木", "yang": True},
    "乙": {"element": "木", "yang": False},
    "丙": {"element": "火", "yang": True},
    "丁": {"element": "火", "yang": False},
    "戊": {"element": "土", "yang": True},
    "己": {"element": "土", "yang": False},
    "庚": {"element": "金", "yang": True},
    "辛": {"element": "金", "yang": False},
    "壬": {"element": "水", "yang": True},
    "癸": {"element": "水", "yang": False},
}

BRANCH_ELEMENT = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}

BRANCH_HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

HOUR_BRANCH_BY_HOUR = {
    23: "子",
    0: "子",
    1: "丑",
    2: "丑",
    3: "寅",
    4: "寅",
    5: "卯",
    6: "卯",
    7: "辰",
    8: "辰",
    9: "巳",
    10: "巳",
    11: "午",
    12: "午",
    13: "未",
    14: "未",
    15: "申",
    16: "申",
    17: "酉",
    18: "酉",
    19: "戌",
    20: "戌",
    21: "亥",
    22: "亥",
}

GENERATE_MAP = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROL_MAP = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

CHONG_PAIRS = {
    frozenset(["子", "午"]),
    frozenset(["丑", "未"]),
    frozenset(["寅", "申"]),
    frozenset(["卯", "酉"]),
    frozenset(["辰", "戌"]),
    frozenset(["巳", "亥"]),
}

HE_PAIRS = {
    frozenset(["子", "丑"]),
    frozenset(["寅", "亥"]),
    frozenset(["卯", "戌"]),
    frozenset(["辰", "酉"]),
    frozenset(["巳", "申"]),
    frozenset(["午", "未"]),
}

STEM_CHONG_PAIRS = {
    frozenset(["甲", "庚"]),
    frozenset(["乙", "辛"]),
    frozenset(["丙", "壬"]),
    frozenset(["丁", "癸"]),
}

STEM_HE_PAIRS = {
    frozenset(["甲", "己"]),
    frozenset(["乙", "庚"]),
    frozenset(["丙", "辛"]),
    frozenset(["丁", "壬"]),
    frozenset(["戊", "癸"]),
}

BRANCH_XING_PAIRS = {
    frozenset(["寅", "巳"]),
    frozenset(["巳", "申"]),
    frozenset(["丑", "戌"]),
    frozenset(["戌", "未"]),
    frozenset(["子", "卯"]),
}

BRANCH_HAI_PAIRS = {
    frozenset(["子", "未"]),
    frozenset(["丑", "午"]),
    frozenset(["寅", "巳"]),
    frozenset(["卯", "辰"]),
    frozenset(["申", "亥"]),
    frozenset(["酉", "戌"]),
}


def _jiazi_index(gz: str) -> int:
    if not gz or len(gz) < 2:
        return 0
    stem_idx = STEMS.index(gz[0])
    branch_idx = BRANCHES.index(gz[1])
    for i in range(60):
        if i % 10 == stem_idx and i % 12 == branch_idx:
            return i
    return 0


def _jiazi_by_index(idx: int) -> str:
    return _jiazi(idx % 60)


def _stem_relation_desc(flow_stem: str, natal_stem: str) -> str:
    if flow_stem == natal_stem:
        return "同气比和"
    pair = frozenset([flow_stem, natal_stem])
    if pair in STEM_HE_PAIRS:
        return "天干合"
    if pair in STEM_CHONG_PAIRS:
        return "天干冲"
    flow_el = STEM_META.get(flow_stem, {}).get("element")
    natal_el = STEM_META.get(natal_stem, {}).get("element")
    if not flow_el or not natal_el:
        return "关系平"
    if GENERATE_MAP[flow_el] == natal_el:
        return "流年生命局"
    if GENERATE_MAP[natal_el] == flow_el:
        return "命局生日年"
    if CONTROL_MAP[flow_el] == natal_el:
        return "流年克命局"
    if CONTROL_MAP[natal_el] == flow_el:
        return "命局克流年"
    return "关系平"


def _branch_relation_desc(flow_branch: str, natal_branch: str) -> str:
    if flow_branch == natal_branch:
        return "同支伏吟"
    pair = frozenset([flow_branch, natal_branch])
    if pair in CHONG_PAIRS:
        return "六冲"
    if pair in HE_PAIRS:
        return "六合"
    if pair in BRANCH_XING_PAIRS:
        return "相刑"
    if pair in BRANCH_HAI_PAIRS:
        return "相害"
    return "关系平"


def _current_dayun(year_pillar: str, month_pillar: str, age: int, gender: str) -> tuple[str, int]:
    # 参考常见口径：阳男阴女顺行，阴男阳女逆行；起运岁数这里使用近似值 8 岁。
    is_male = str(gender) == "男"
    year_stem = year_pillar[0]
    year_is_yang = STEM_META.get(year_stem, {}).get("yang", True)
    forward = (is_male and year_is_yang) or ((not is_male) and (not year_is_yang))

    start_age = 8
    step = 1 if forward else -1
    dayun_index = max(0, (max(age, 1) - start_age) // 10)
    month_idx = _jiazi_index(month_pillar)
    current_idx = month_idx + step * (dayun_index + 1)
    return _jiazi_by_index(current_idx), dayun_index


def _parse_birth_date(value: str) -> date | None:
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except Exception:
            continue
    return None


def _safe_hour(value: str | int | None) -> int:
    try:
        hour = int(value)
    except Exception:
        return 12
    if hour < 0 or hour > 23:
        return 12
    return hour


def _jiazi(index: int) -> str:
    return STEMS[index % 10] + BRANCHES[index % 12]


def _pillar_year(y: int) -> str:
    # 1984 年是甲子年，这里做简化年柱计算（不含节气切换）。
    return _jiazi((y - 1984) % 60)


def _pillar_month(y_stem: str, m: int) -> str:
    month_branch_seq = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    mb = month_branch_seq[(m - 1) % 12]
    start_map = {"甲": "丙", "己": "丙", "乙": "戊", "庚": "戊", "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬", "戊": "甲", "癸": "甲"}
    start_stem = start_map.get(y_stem, "丙")
    start_idx = STEMS.index(start_stem)
    stem = STEMS[(start_idx + (m - 1)) % 10]
    return stem + mb


def _pillar_day(d: date) -> str:
    # 以 1900-01-31 甲子日为参考做简化推算。
    base = date(1900, 1, 31)
    delta = (d - base).days
    return _jiazi(delta % 60)


def _pillar_hour(day_stem: str, hour: int) -> str:
    hb = HOUR_BRANCH_BY_HOUR.get(hour, "午")
    day_stem_idx = STEMS.index(day_stem)
    # 甲己日从甲子起，乙庚日从丙子起，丙辛日从戊子起，丁壬日从庚子起，戊癸日从壬子起
    start_stem_idx_map = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}
    start_idx = start_stem_idx_map.get(day_stem_idx, 0)
    branch_idx = BRANCHES.index(hb)
    hs = STEMS[(start_idx + branch_idx) % 10]
    return hs + hb


def _ten_god(day_stem: str, other_stem: str) -> str:
    if day_stem == other_stem:
        return "日主"
    day_meta = STEM_META[day_stem]
    other_meta = STEM_META[other_stem]
    same_yinyang = day_meta["yang"] == other_meta["yang"]
    day_el = day_meta["element"]
    other_el = other_meta["element"]

    if day_el == other_el:
        return "比肩" if same_yinyang else "劫财"
    if GENERATE_MAP[day_el] == other_el:
        return "食神" if same_yinyang else "伤官"
    if GENERATE_MAP[other_el] == day_el:
        return "偏印" if same_yinyang else "正印"
    if CONTROL_MAP[day_el] == other_el:
        return "偏财" if same_yinyang else "正财"
    return "七杀" if same_yinyang else "正官"


def _age_range(age: int) -> tuple[str, str]:
    if age <= 10:
        return "1-10岁", "儿童"
    if age <= 17:
        return "11-17岁", "少年"
    if age <= 30:
        return "18-30岁", "青年"
    if age <= 49:
        return "31-49岁", "中年"
    if age <= 59:
        return "50-59岁", "中老年"
    return "60岁及以上", "老年"


def _cn_number(num: int) -> str:
    chars = "零一二三四五六七八九"
    if num < 10:
        return chars[num]
    if num < 20:
        return "十" if num == 10 else "十" + chars[num % 10]
    if num < 100:
        tens, ones = divmod(num, 10)
        return chars[tens] + "十" + (chars[ones] if ones else "")
    return str(num)


def _nominal_age_and_label(birth_date: date, today: date) -> tuple[int, str]:
    nominal_age = max(1, today.year - birth_date.year + 1)
    return nominal_age, "{}岁".format(_cn_number(nominal_age))


def _relationships(branches: list[str], stems: list[str]) -> dict:
    chong = []
    he = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            pair = frozenset([branches[i], branches[j]])
            if pair in CHONG_PAIRS:
                chong.append(branches[i] + branches[j] + "冲")
            if pair in HE_PAIRS:
                he.append(branches[i] + branches[j] + "合")

    stem_he_pairs = {
        frozenset(["甲", "己"]),
        frozenset(["乙", "庚"]),
        frozenset(["丙", "辛"]),
        frozenset(["丁", "壬"]),
        frozenset(["戊", "癸"]),
    }
    stem_he = []
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            if frozenset([stems[i], stems[j]]) in stem_he_pairs:
                stem_he.append(stems[i] + stems[j] + "合")

    return {
        "chong": chong,
        "he": he,
        "stem_he": stem_he,
    }


def build_bazi_profile(birth_date_text: str, birth_hour_value: str | int | None, gender: str = "未知") -> dict:
    birth_date = _parse_birth_date(birth_date_text)
    if not birth_date:
        return {}

    hour = _safe_hour(birth_hour_value)

    # 优先尝试 lunar_python 的高精度四柱，失败时回退到简化计算。
    year_pillar = month_pillar = day_pillar = time_pillar = ""
    lunar_birth_text = ""
    try:
        from lunar_python import Solar  # type: ignore

        solar = Solar.fromYmdHms(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            hour,
            0,
            0,
        )
        ec = solar.getLunar().getEightChar()
        lunar = solar.getLunar()
        year_pillar = ec.getYear()
        month_pillar = ec.getMonth()
        day_pillar = ec.getDay()
        time_pillar = ec.getTime()
        lunar_birth_text = "{}年{}月{} {}时".format(
            lunar.getYearInChinese(),
            lunar.getMonthInChinese(),
            lunar.getDayInChinese(),
            BRANCHES[BRANCHES.index(time_pillar[1])] if len(time_pillar) >= 2 and time_pillar[1] in BRANCHES else "午",
        )
    except Exception:
        year_pillar = _pillar_year(birth_date.year)
        month_pillar = _pillar_month(year_pillar[0], birth_date.month)
        day_pillar = _pillar_day(birth_date)
        time_pillar = _pillar_hour(day_pillar[0], hour)
        lunar_birth_text = "农历信息暂缺 {}时".format(HOUR_BRANCH_BY_HOUR.get(hour, "午"))

    pillars = [year_pillar, month_pillar, day_pillar, time_pillar]
    stems = [p[0] for p in pillars]
    branches = [p[1] for p in pillars]

    wuxing_list = [STEM_META[s]["element"] + BRANCH_ELEMENT[b] for s, b in zip(stems, branches)]
    wuxing_detail_parts = []
    for idx, branch in enumerate(branches):
        hidden = BRANCH_HIDDEN_STEMS.get(branch, [])
        hidden_text = "".join(hidden) if hidden else "-"
        wuxing_detail_parts.append("{}柱{}藏{}".format(["年", "月", "日", "时"][idx], branch, hidden_text))
    day_master = day_pillar[0]
    day_master_element = STEM_META.get(day_master, {}).get("element", "")
    wuxing_summary = "日主{}({})；{}".format(
        day_master,
        day_master_element,
        "；".join(wuxing_detail_parts),
    )
    shishen = [
        _ten_god(day_pillar[0], stems[0]),
        _ten_god(day_pillar[0], stems[1]),
        "日主",
        _ten_god(day_pillar[0], stems[3]),
    ]

    today = date.today()
    age = max(0, today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))
    nominal_age, nominal_age_cn = _nominal_age_and_label(birth_date, today)
    age_range, age_stage = _age_range(age)

    relation = _relationships(branches, stems)
    current_year_ganzhi = _pillar_year(today.year)
    next_year_ganzhi = _pillar_year(today.year + 1)
    current_dayun_ganzhi, dayun_index = _current_dayun(year_pillar, month_pillar, age, gender)

    flow_stem = current_year_ganzhi[0]
    flow_branch = current_year_ganzhi[1]
    stem_compare_lines = []
    for idx, natal_stem in enumerate(stems):
        stem_compare_lines.append(
            "{}柱{}：{}".format(["年", "月", "日", "时"][idx], natal_stem, _stem_relation_desc(flow_stem, natal_stem))
        )

    branch_compare_lines = []
    for idx, natal_branch in enumerate(branches):
        branch_compare_lines.append(
            "{}柱{}：{}".format(["年", "月", "日", "时"][idx], natal_branch, _branch_relation_desc(flow_branch, natal_branch))
        )

    dayun_stem = current_dayun_ganzhi[0]
    dayun_branch = current_dayun_ganzhi[1]
    flow_dayun_effect = "当前大运{}（约第{}步运）与流年{}叠加：干支关系为天干{}、地支{}。".format(
        current_dayun_ganzhi,
        dayun_index + 1,
        current_year_ganzhi,
        _stem_relation_desc(flow_stem, dayun_stem),
        _branch_relation_desc(flow_branch, dayun_branch),
    )

    return {
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "birth_hour": hour,
        "bazi_str": " ".join(pillars),
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "time_pillar": time_pillar,
        "wuxing": " ".join(wuxing_list),
        "wuxing_summary": wuxing_summary,
        "wuxing_list": wuxing_list,
        "shishen": shishen,
        "age": age,
        "nominal_age": nominal_age,
        "nominal_age_cn": nominal_age_cn,
        "age_range": age_range,
        "age_stage": age_stage,
        "lunar_birth_text": lunar_birth_text,
        "gender": gender,
        "relationships": relation,
        "current_year_ganzhi": current_year_ganzhi,
        "next_year_ganzhi": next_year_ganzhi,
        "current_dayun_ganzhi": current_dayun_ganzhi,
        "flow_year_stem_compare": stem_compare_lines,
        "flow_year_branch_compare": branch_compare_lines,
        "flow_dayun_effect": flow_dayun_effect,
    }
