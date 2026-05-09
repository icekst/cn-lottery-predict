# -*- coding: utf-8 -*-
"""
示例配置文件

使用方法：
1. 复制本文件
2. 重命名为 config.py
3. 填入自己的 API Key
"""


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
