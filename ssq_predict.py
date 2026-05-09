# -*- coding: utf-8 -*-
"""
============================================================
中国福利彩票 - 双色球号码推荐程序
============================================================

Author      : xutao
GitHub      : https://github.com/icekst
Email       : xutao2020@qq.com
Version     : 1.0.0
Create Date : 2026-05-09
Update Date : 2026-05-09
Python      : 3.9+

Description:
    本程序用于中国福利彩票双色球历史开奖数据分析与号码推荐。
    程序会自动从中国福利彩票接口获取历史开奖数据，
    并基于热号、冷号、遗漏值、和值、奇偶比、分区比例等特征，
    生成统计推荐号码。

Features:
    1. 自动从中国福利彩票接口获取双色球历史开奖数据
    2. 输出历史数据统计信息
    3. 输出统计推荐号码
    4. 可选调用大模型 API 输出模型推荐号码
    5. 可通过 SHOW_REASON 控制是否输出推荐理由

Dependencies:
    pip install requests openai

Disclaimer:
    彩票开奖结果具有随机性。
    本程序仅用于 Python 学习、数据分析和娱乐参考。
    程序生成的号码不能保证中奖，请理性使用，切勿沉迷投注。

License:
    MIT License
"""

import json
import random
import re
from collections import Counter
from datetime import datetime, timedelta

import requests


# ============================================================
# 1. 参数配置区域
# ============================================================

# 是否输出推荐理由
# True  ：输出推荐号码 + 推荐理由
# False ：只输出推荐号码
SHOW_REASON = True

# 是否启用统计模型预测
ENABLE_STAT_PREDICT = True

# 是否启用大模型 API 预测
ENABLE_LLM_PREDICT = True

# 统计模型输出几组号码
STAT_PREDICT_COUNT = 10

# 大模型输出几组号码
LLM_PREDICT_COUNT = 10

# 抓取最近多少期历史数据
HISTORY_COUNT = 1500

# 用最近多少期参与统计分析
LOOKBACK_COUNT = 300

# 传给大模型最近多少期原始开奖数据
SEND_RECENT_ISSUES_TO_LLM = 80

# 随机种子
# None 表示每次运行结果不同
# 例如 RANDOM_SEED = 42 表示每次运行结果一致
RANDOM_SEED = None


# ============================================================
# 2. 大模型 API 配置
# ============================================================

API_KEY = "请在这里填入你的API_KEY"

# OpenAI 官方接口
BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"

# 如果使用 DeepSeek、通义千问、智谱、硅基流动、OpenRouter 等 OpenAI 兼容接口，
# 修改 API_KEY、BASE_URL、MODEL_NAME 即可。

# 如果你的接口不支持 json_schema，把这里改成 False
USE_JSON_SCHEMA = True


# ============================================================
# 3. 双色球基础配置
# ============================================================

RED_MIN = 1
RED_MAX = 33
BLUE_MIN = 1
BLUE_MAX = 16
RED_COUNT = 6

CWL_API_URL = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"


# ============================================================
# 4. 基础工具函数
# ============================================================

def format_nums(nums):
    return " ".join(f"{n:02d}" for n in nums)


def parse_number_string(value):
    if value is None:
        return []

    value = str(value)
    value = value.replace("，", ",")
    value = value.replace("+", ",")
    value = value.replace("|", ",")
    value = value.replace(" ", ",")

    parts = [x.strip() for x in value.split(",") if x.strip()]
    nums = []

    for p in parts:
        if p.isdigit():
            nums.append(int(p))

    return nums


def is_valid_reds(reds):
    if not isinstance(reds, list):
        return False

    if len(reds) != 6:
        return False

    if len(set(reds)) != 6:
        return False

    for n in reds:
        if not isinstance(n, int):
            return False

        if n < RED_MIN or n > RED_MAX:
            return False

    return True


def is_valid_blue(blue):
    return isinstance(blue, int) and BLUE_MIN <= blue <= BLUE_MAX


def is_valid_prediction(item):
    if not isinstance(item, dict):
        return False

    reds = item.get("red")
    blue = item.get("blue")

    return is_valid_reds(reds) and is_valid_blue(blue)


def parse_draw_date(date_text):
    """
    兼容以下日期格式：
    2026-05-07
    2026-05-07(四)
    2026-05-07 21:15:00
    """
    match = re.search(r"\d{4}-\d{2}-\d{2}", str(date_text))

    if not match:
        raise RuntimeError(f"无法解析开奖日期：{date_text}")

    return datetime.strptime(match.group(), "%Y-%m-%d").date()


def format_draw_date_cn(date_text):
    """
    将 2026-05-10 转成 2026年5月10日（日）
    """
    date_obj = parse_draw_date(date_text)

    week_map = {
        0: "一",
        1: "二",
        2: "三",
        3: "四",
        4: "五",
        5: "六",
        6: "日",
    }

    return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日（{week_map[date_obj.weekday()]}）"


# ============================================================
# 5. 获取双色球历史数据
# ============================================================

def fetch_history_from_cwl(issue_count=1500):
    params = {
        "name": "ssq",
        "issueCount": issue_count,
        "issueStart": "",
        "issueEnd": "",
        "dayStart": "",
        "dayEnd": "",
        "pageNo": 1,
        "pageSize": issue_count,
        "week": "",
        "systemType": "PC",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Referer": "https://www.cwl.gov.cn/ygkj/kjgg/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(
        CWL_API_URL,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    raw_items = data.get("result", [])

    if isinstance(raw_items, dict):
        raw_items = (
            raw_items.get("list")
            or raw_items.get("records")
            or raw_items.get("data")
            or []
        )

    history = []

    for item in raw_items:
        period = str(
            item.get("code")
            or item.get("qh")
            or item.get("period")
            or ""
        )

        date = str(
            item.get("date")
            or item.get("kjsj")
            or item.get("drawDate")
            or ""
        )

        red_str = item.get("red") or item.get("qq") or ""
        blue_str = item.get("blue") or item.get("hq") or ""

        reds = parse_number_string(red_str)
        blues = parse_number_string(blue_str)

        if len(reds) == 6 and len(blues) >= 1:
            reds = sorted(reds)
            blue = blues[0]

            if is_valid_reds(reds) and is_valid_blue(blue):
                history.append({
                    "period": period,
                    "date": date,
                    "red": reds,
                    "blue": blue
                })

    if not history:
        raise RuntimeError("没有获取到有效历史开奖数据，可能是网络异常或接口结构变化。")

    def period_to_int(item):
        period = str(item.get("period", ""))
        return int(period) if period.isdigit() else 0

    history.sort(key=period_to_int, reverse=True)

    return history


# ============================================================
# 6. 推算下一期开奖日期和期号
# ============================================================

def get_next_draw_info(history):
    """
    双色球通常为每周二、四、日开奖。

    Python weekday:
    周一=0，周二=1，周三=2，周四=3，周五=4，周六=5，周日=6
    """

    latest = history[0]

    latest_period = str(latest["period"])
    latest_date = parse_draw_date(latest["date"])

    draw_weekdays = [1, 3, 6]

    next_date = latest_date + timedelta(days=1)

    while next_date.weekday() not in draw_weekdays:
        next_date += timedelta(days=1)

    if latest_period.isdigit():
        latest_period_num = int(latest_period)

        if str(latest_period).startswith(str(next_date.year)):
            next_period = str(latest_period_num + 1)
        else:
            next_period = f"{next_date.year}001"
    else:
        next_period = "未知"

    return next_period, next_date.strftime("%Y-%m-%d")


# ============================================================
# 7. 历史数据统计分析
# ============================================================

def calculate_omission(history, numbers, ball_type):
    omission = {}

    for num in numbers:
        miss = 0

        for item in history:
            if ball_type == "red":
                appeared = num in item["red"]
            else:
                appeared = num == item["blue"]

            if appeared:
                break

            miss += 1

        omission[num] = miss

    return omission


def analyze_history(history, lookback_count):
    recent = history[:lookback_count]

    red_counter = Counter()
    blue_counter = Counter()

    red_sums = []
    odd_counts = []
    zone_stats = []

    for item in recent:
        reds = item["red"]
        blue = item["blue"]

        red_counter.update(reds)
        blue_counter.update([blue])

        red_sums.append(sum(reds))
        odd_counts.append(sum(1 for n in reds if n % 2 == 1))

        zone_1 = sum(1 for n in reds if 1 <= n <= 11)
        zone_2 = sum(1 for n in reds if 12 <= n <= 22)
        zone_3 = sum(1 for n in reds if 23 <= n <= 33)
        zone_stats.append([zone_1, zone_2, zone_3])

    red_numbers = list(range(RED_MIN, RED_MAX + 1))
    blue_numbers = list(range(BLUE_MIN, BLUE_MAX + 1))

    red_freq = {n: red_counter.get(n, 0) for n in red_numbers}
    blue_freq = {n: blue_counter.get(n, 0) for n in blue_numbers}

    red_omission = calculate_omission(history, red_numbers, "red")
    blue_omission = calculate_omission(history, blue_numbers, "blue")

    hot_red = sorted(red_numbers, key=lambda n: red_freq[n], reverse=True)[:10]
    cold_red = sorted(red_numbers, key=lambda n: red_freq[n])[:10]

    hot_blue = sorted(blue_numbers, key=lambda n: blue_freq[n], reverse=True)[:5]
    cold_blue = sorted(blue_numbers, key=lambda n: blue_freq[n])[:5]

    long_miss_red = sorted(red_numbers, key=lambda n: red_omission[n], reverse=True)[:10]
    long_miss_blue = sorted(blue_numbers, key=lambda n: blue_omission[n], reverse=True)[:5]

    avg_sum = sum(red_sums) / len(red_sums)
    avg_odd = sum(odd_counts) / len(odd_counts)

    avg_zone_1 = sum(z[0] for z in zone_stats) / len(zone_stats)
    avg_zone_2 = sum(z[1] for z in zone_stats) / len(zone_stats)
    avg_zone_3 = sum(z[2] for z in zone_stats) / len(zone_stats)

    return {
        "lookback_count": len(recent),
        "red_freq": red_freq,
        "blue_freq": blue_freq,
        "red_omission": red_omission,
        "blue_omission": blue_omission,
        "hot_red": hot_red,
        "cold_red": cold_red,
        "hot_blue": hot_blue,
        "cold_blue": cold_blue,
        "long_miss_red": long_miss_red,
        "long_miss_blue": long_miss_blue,
        "avg_sum": round(avg_sum, 2),
        "avg_odd": round(avg_odd, 2),
        "avg_zone": [
            round(avg_zone_1, 2),
            round(avg_zone_2, 2),
            round(avg_zone_3, 2)
        ]
    }


# ============================================================
# 8. 统计模型预测
# ============================================================

def normalize(data_dict):
    values = list(data_dict.values())

    if not values:
        return {}

    min_value = min(values)
    max_value = max(values)

    if max_value == min_value:
        return {k: 0.5 for k in data_dict}

    return {
        k: (v - min_value) / (max_value - min_value)
        for k, v in data_dict.items()
    }


def build_stat_weights(freq_dict, omission_dict, mode):
    numbers = list(freq_dict.keys())

    if mode == "random":
        return {n: 1.0 for n in numbers}

    freq_norm = normalize(freq_dict)
    omission_norm = normalize(omission_dict)

    weights = {}

    for n in numbers:
        if mode == "hot":
            weight = 0.75 * freq_norm[n] + 0.10 * omission_norm[n] + 0.15

        elif mode == "cold":
            weight = 0.15 * freq_norm[n] + 0.70 * omission_norm[n] + 0.15

        else:
            weight = 0.50 * freq_norm[n] + 0.35 * omission_norm[n] + 0.15

        weights[n] = max(weight, 0.0001)

    return weights


def weighted_sample_without_replacement(numbers, weights, count):
    pool = numbers[:]
    selected = []

    for _ in range(count):
        total_weight = sum(weights[n] for n in pool)
        r = random.uniform(0, total_weight)

        current = 0.0
        chosen = pool[-1]

        for n in pool:
            current += weights[n]

            if current >= r:
                chosen = n
                break

        selected.append(chosen)
        pool.remove(chosen)

    return selected


def get_red_structure(reds):
    reds = sorted(reds)

    total_sum = sum(reds)
    odd_count = sum(1 for n in reds if n % 2 == 1)
    even_count = 6 - odd_count

    zone_1 = sum(1 for n in reds if 1 <= n <= 11)
    zone_2 = sum(1 for n in reds if 12 <= n <= 22)
    zone_3 = sum(1 for n in reds if 23 <= n <= 33)

    return total_sum, odd_count, even_count, zone_1, zone_2, zone_3


def is_reasonable_red_combo(reds):
    total_sum, odd_count, even_count, zone_1, zone_2, zone_3 = get_red_structure(reds)

    if total_sum < 60 or total_sum > 140:
        return False

    if odd_count not in [2, 3, 4]:
        return False

    if max(zone_1, zone_2, zone_3) >= 5:
        return False

    consecutive_count = 0

    sorted_reds = sorted(reds)

    for a, b in zip(sorted_reds, sorted_reds[1:]):
        if b == a + 1:
            consecutive_count += 1

    if consecutive_count >= 4:
        return False

    return True


def build_stat_reason(reds, blue, mode):
    total_sum, odd_count, even_count, zone_1, zone_2, zone_3 = get_red_structure(reds)

    if mode == "hot":
        mode_text = "偏向近期高频号码"
    elif mode == "cold":
        mode_text = "偏向当前遗漏较久号码"
    elif mode == "random":
        mode_text = "随机基准组合"
    else:
        mode_text = "热号、冷号、遗漏值综合"

    return (
        f"和值{total_sum}，奇偶{odd_count}:{even_count}，"
        f"三区{zone_1}:{zone_2}:{zone_3}，{mode_text}"
    )


def generate_one_stat_prediction(analysis, mode):
    red_numbers = list(range(RED_MIN, RED_MAX + 1))
    blue_numbers = list(range(BLUE_MIN, BLUE_MAX + 1))

    red_weights = build_stat_weights(
        analysis["red_freq"],
        analysis["red_omission"],
        mode
    )

    blue_weights = build_stat_weights(
        analysis["blue_freq"],
        analysis["blue_omission"],
        mode
    )

    for _ in range(500):
        reds = weighted_sample_without_replacement(
            red_numbers,
            red_weights,
            RED_COUNT
        )

        reds = sorted(reds)

        if is_reasonable_red_combo(reds):
            blue = weighted_sample_without_replacement(
                blue_numbers,
                blue_weights,
                1
            )[0]

            reason = build_stat_reason(reds, blue, mode)

            return reds, blue, reason

    reds = sorted(
        weighted_sample_without_replacement(
            red_numbers,
            red_weights,
            RED_COUNT
        )
    )

    blue = weighted_sample_without_replacement(
        blue_numbers,
        blue_weights,
        1
    )[0]

    reason = build_stat_reason(reds, blue, mode)

    return reds, blue, reason


def generate_stat_predictions(analysis, count):
    modes = [
        "balanced",
        "hot",
        "cold",
        "balanced",
        "random"
    ]

    predictions = []
    used = set()
    index = 0

    while len(predictions) < count:
        mode = modes[index % len(modes)]

        reds, blue, reason = generate_one_stat_prediction(analysis, mode)
        key = tuple(reds + [blue])

        if key not in used:
            used.add(key)

            predictions.append({
                "red": reds,
                "blue": blue,
                "reason": reason
            })

        index += 1

        if index > count * 100:
            break

    return predictions


# ============================================================
# 9. 构造大模型输入
# ============================================================

def build_llm_input(history, analysis, next_issue, next_draw_date):
    recent_items = history[:SEND_RECENT_ISSUES_TO_LLM]

    recent_history = []

    for item in recent_items:
        recent_history.append({
            "period": item["period"],
            "date": item["date"],
            "red": item["red"],
            "blue": item["blue"]
        })

    summary = {
        "lottery_type": "中国福利彩票双色球",
        "next_issue": next_issue,
        "next_draw_date": next_draw_date,
        "rule": {
            "red": "1-33中选择6个不重复号码",
            "blue": "1-16中选择1个号码"
        },
        "lookback_count": analysis["lookback_count"],
        "hot_red": analysis["hot_red"],
        "cold_red": analysis["cold_red"],
        "hot_blue": analysis["hot_blue"],
        "cold_blue": analysis["cold_blue"],
        "long_miss_red": analysis["long_miss_red"],
        "long_miss_blue": analysis["long_miss_blue"],
        "avg_red_sum": analysis["avg_sum"],
        "avg_odd_count": analysis["avg_odd"],
        "avg_zone_distribution": analysis["avg_zone"],
        "recent_history": recent_history
    }

    return json.dumps(summary, ensure_ascii=False, indent=2)


# ============================================================
# 10. 调用大模型 API
# ============================================================

def call_llm_for_prediction(llm_input_text, predict_count):
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("未安装 openai，请先运行：pip install openai")

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    system_prompt = """
你是一个彩票历史数据分析助手。
你的任务不是保证中奖，而是基于用户提供的双色球历史统计数据，生成若干组合法的双色球号码。

重要规则：
1. 必须承认彩票是随机事件，不能保证中奖。
2. 只能基于统计特征给出娱乐参考号码。
3. 红球必须从1到33中选6个，不能重复，必须升序排列。
4. 蓝球必须从1到16中选1个。
5. 不要输出任何 JSON 之外的内容。
6. reason 字段要简洁，说明号码结构，例如和值、奇偶比、三区分布、热冷结合、遗漏补充。
"""

    user_prompt = f"""
请根据下面的双色球历史数据和统计结果，生成 {predict_count} 组推荐号码。

要求：
1. 每组包含 red、blue、reason。
2. red 是6个不重复整数，范围1-33，升序排列。
3. blue 是1个整数，范围1-16。
4. 不要迷信热号，也不要全部选择冷号。
5. 尽量让和值、奇偶比、三区分布相对均衡。
6. 输出必须是 JSON。

历史统计数据如下：
{llm_input_text}
"""

    if USE_JSON_SCHEMA:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.8,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ssq_prediction_result",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "disclaimer": {
                                "type": "string"
                            },
                            "predictions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "red": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 1,
                                                "maximum": 33
                                            },
                                            "minItems": 6,
                                            "maxItems": 6
                                        },
                                        "blue": {
                                            "type": "integer",
                                            "minimum": 1,
                                            "maximum": 16
                                        },
                                        "reason": {
                                            "type": "string"
                                        }
                                    },
                                    "required": ["red", "blue", "reason"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["disclaimer", "predictions"],
                        "additionalProperties": False
                    }
                }
            }
        )

    else:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt + """

请严格按照下面 JSON 格式输出，不要输出其他内容：

{
  "disclaimer": "彩票是随机事件，本结果仅供娱乐参考，不能保证中奖。",
  "predictions": [
    {
      "red": [1, 2, 3, 4, 5, 6],
      "blue": 7,
      "reason": "和值101，奇偶3:3，三区2:2:2，热冷结合"
    }
  ]
}
"""
                }
            ],
            temperature=0.8
        )

    return response.choices[0].message.content


# ============================================================
# 11. 解析大模型返回结果
# ============================================================

def extract_json_from_text(text):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"^```", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text


def fix_prediction(item):
    reds = item.get("red", [])
    blue = item.get("blue")

    reds = [int(x) for x in reds]
    blue = int(blue)

    return {
        "red": sorted(reds),
        "blue": blue,
        "reason": str(item.get("reason", ""))
    }


def parse_llm_result(content):
    json_text = extract_json_from_text(content)

    try:
        data = json.loads(json_text)
    except Exception as e:
        raise RuntimeError(f"大模型返回内容不是合法 JSON：{e}\n原始内容：\n{content}")

    predictions = data.get("predictions", [])

    valid_predictions = []
    used = set()

    for item in predictions:
        try:
            fixed = fix_prediction(item)
        except Exception:
            continue

        if not is_valid_prediction(fixed):
            continue

        key = tuple(fixed["red"] + [fixed["blue"]])

        if key in used:
            continue

        used.add(key)
        valid_predictions.append(fixed)

    return {
        "disclaimer": data.get(
            "disclaimer",
            "彩票是随机事件，本结果仅供娱乐参考，不能保证中奖。"
        ),
        "predictions": valid_predictions
    }


def fill_llm_predictions_if_needed(llm_result, stat_predictions, target_count):
    used = set()
    final_predictions = []

    for item in llm_result["predictions"]:
        key = tuple(item["red"] + [item["blue"]])

        if key not in used:
            used.add(key)
            final_predictions.append(item)

    for item in stat_predictions:
        if len(final_predictions) >= target_count:
            break

        key = tuple(item["red"] + [item["blue"]])

        if key not in used:
            used.add(key)

            new_item = item.copy()
            new_item["reason"] = "大模型返回数量不足，使用统计模型补足：" + new_item["reason"]

            final_predictions.append(new_item)

    llm_result["predictions"] = final_predictions
    return llm_result


# ============================================================
# 12. 输出函数
# ============================================================

def print_program_header():
    print("=" * 60)
    print("中国福利彩票 - 双色球号码推荐程序")
    print("=" * 60)
    print("声明：彩票开奖结果具有随机性，本程序仅用于学习、娱乐和数据分析，不能保证中奖。")
    print()


def print_fetching_message():
    print(f"正在从中国福利彩票接口获取最近 {HISTORY_COUNT} 期双色球数据...")


def print_history_analysis(history, analysis):
    latest = history[0]

    print()
    print("=" * 60)
    print("双色球历史数据统计")
    print("=" * 60)
    print(f"历史数据期数：{len(history)}")
    print(f"最近一期期号：{latest['period']}")
    print(f"最近一期日期：{latest['date']}")
    print(f"最近一期开奖号码：红球 [{format_nums(latest['red'])}]  蓝球 [{latest['blue']:02d}]")
    print(f"统计窗口：最近 {analysis['lookback_count']} 期")

    print()
    print("【红球热号】" + format_nums(analysis["hot_red"]))

    print()
    print("【红球冷号】" + format_nums(analysis["cold_red"]))

    print()
    print("【蓝球热号】" + format_nums(analysis["hot_blue"]))

    print()
    print("【蓝球冷号】" + format_nums(analysis["cold_blue"]))

    red_omission_text = " ".join(
        f"{num:02d}({analysis['red_omission'][num]}期)"
        for num in analysis["long_miss_red"]
    )

    blue_omission_text = " ".join(
        f"{num:02d}({analysis['blue_omission'][num]}期)"
        for num in analysis["long_miss_blue"]
    )

    print()
    print("【当前遗漏较久的红球】")
    print(red_omission_text)

    print()
    print("【当前遗漏较久的蓝球】")
    print(blue_omission_text)


def print_recommend_header():
    print()
    print("=" * 60)
    print("双色球推荐号码")
    print("=" * 60)
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print()


def print_draw_header(next_issue, next_draw_date):
    print(f"开奖期号：{next_issue}")
    print(f"开奖日期：{format_draw_date_cn(next_draw_date)}")
    print()
    print()


def print_prediction_numbers(title, predictions):
    print(title)

    for i, item in enumerate(predictions, start=1):
        print(
            f"第 {i:02d} 组："
            f"红球 [{format_nums(item['red'])}]  "
            f"蓝球 [{item['blue']:02d}]"
        )

    print()


def print_prediction_reasons(title, predictions):
    print(title)

    for i, item in enumerate(predictions, start=1):
        reason = item.get("reason", "")

        if reason:
            print(
                f"第 {i:02d} 组："
                f"红球 [{format_nums(item['red'])}]  "
                f"蓝球 [{item['blue']:02d}]\t"
                f"理由：{reason}"
            )
        else:
            print(
                f"第 {i:02d} 组："
                f"红球 [{format_nums(item['red'])}]  "
                f"蓝球 [{item['blue']:02d}]"
            )

    print()


# ============================================================
# 13. 主程序入口
# ============================================================

def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    try:
        print_program_header()

        print_fetching_message()

        history = fetch_history_from_cwl(HISTORY_COUNT)

        analysis = analyze_history(history, LOOKBACK_COUNT)

        next_issue, next_draw_date = get_next_draw_info(history)

        print_history_analysis(history, analysis)

        stat_predictions = []
        llm_predictions = []

        if ENABLE_STAT_PREDICT:
            stat_predictions = generate_stat_predictions(
                analysis,
                STAT_PREDICT_COUNT
            )

        if ENABLE_LLM_PREDICT:
            if API_KEY == "请在这里填入你的API_KEY":
                llm_predictions = []
            else:
                llm_input_text = build_llm_input(
                    history,
                    analysis,
                    next_issue,
                    next_draw_date
                )

                content = call_llm_for_prediction(
                    llm_input_text,
                    LLM_PREDICT_COUNT
                )

                llm_result = parse_llm_result(content)

                if stat_predictions:
                    llm_result = fill_llm_predictions_if_needed(
                        llm_result,
                        stat_predictions,
                        LLM_PREDICT_COUNT
                    )

                llm_predictions = llm_result["predictions"]

        print_recommend_header()

        print_draw_header(next_issue, next_draw_date)

        if stat_predictions:
            print_prediction_numbers(
                "统计推荐号码：",
                stat_predictions
            )

        if llm_predictions:
            print_prediction_numbers(
                "模型推荐号码：",
                llm_predictions
            )

        if SHOW_REASON:
            if stat_predictions:
                print_prediction_reasons(
                    "统计推荐号码理由：",
                    stat_predictions
                )

            if llm_predictions:
                print_prediction_reasons(
                    "模型推荐号码理由：",
                    llm_predictions
                )

        if ENABLE_LLM_PREDICT and API_KEY == "请在这里填入你的API_KEY":
            print("提示：未填写 API_KEY，已跳过模型推荐号码。")
            print("如需启用大模型预测，请在代码顶部填写 API_KEY。")

    except Exception as e:
        print("\n程序运行失败：")
        print(e)


if __name__ == "__main__":
    main()