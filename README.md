# cn-lottery-predict

中国福利彩票双色球号码推荐程序。

本项目用于学习 Python、历史开奖数据分析、统计特征提取，以及演示如何结合大模型 API 生成娱乐性质的双色球推荐号码。

> **重要声明**  
> 彩票开奖结果具有随机性，本项目不能预测未来开奖结果，不能保证中奖。  
> 本项目仅用于 Python 学习、数据分析和娱乐参考，请理性使用，切勿沉迷投注。

---

## 项目功能

- 自动从中国福利彩票接口获取双色球历史开奖数据
- 输出双色球历史数据统计信息
- 统计红球、蓝球热号
- 统计红球、蓝球冷号
- 统计当前遗漏较久的号码
- 基于统计特征生成推荐号码
- 可选调用大模型 API 生成模型推荐号码
- 支持控制是否输出推荐理由
- 自动推算下一期开奖期号和开奖日期
- 支持将 API Key 和运行参数放到独立配置文件中
- 支持 PyCharm 直接运行

---

## 项目结构

推荐项目结构如下：

```text
cn-lottery-predict/
├── main.py
├── config.example.py
├── config.py
├── README.md
├── LICENSE
├── .gitignore
└── requirements.txt
```

说明：

```text
main.py              主程序文件
config.example.py    示例配置文件，可以上传到 GitHub
config.py            本地真实配置文件，不要上传到 GitHub
README.md            项目说明文件
LICENSE              开源许可证
.gitignore           Git 忽略规则
requirements.txt     依赖列表
```

重点：

```text
config.py 中可以填写真实 API Key
config.py 不应该上传到 GitHub
config.example.py 用于给其他用户参考
```

---

## 输出示例

```text
============================================================
中国福利彩票 - 双色球号码推荐程序
============================================================
声明：彩票开奖结果具有随机性，本程序仅用于学习、娱乐和数据分析，不能保证中奖。

正在从中国福利彩票接口获取最近 1500 期双色球数据...

============================================================
双色球历史数据统计
============================================================
历史数据期数：1500
最近一期期号：2026051
最近一期日期：2026-05-07(四)
最近一期开奖号码：红球 [09 14 15 16 29 30]  蓝球 [10]
统计窗口：最近 300 期

【红球热号】02 13 03 09 17 18 22 30 06 08

【红球冷号】21 26 28 29 31 12 05 20 07 11

【蓝球热号】10 16 03 11 15

【蓝球冷号】09 02 08 07 14

【当前遗漏较久的红球】
05(34期) 26(24期) 01(13期) 13(13期) 23(11期) 08(10期) 12(9期) 19(9期) 32(8期) 22(7期)

【当前遗漏较久的蓝球】
09(77期) 11(29期) 14(27期) 06(18期) 08(15期)

============================================================
双色球推荐号码
============================================================
生成时间：2026-05-09 11:26:30


开奖期号：2026052
开奖日期：2026年5月10日（日）


统计推荐号码：
第 01 组：红球 [01 06 16 18 27 29]  蓝球 [16]
第 02 组：红球 [06 08 15 23 26 30]  蓝球 [16]
第 03 组：红球 [05 06 10 13 22 25]  蓝球 [01]

模型推荐号码：
第 01 组：红球 [02 07 15 22 28 31]  蓝球 [14]
第 02 组：红球 [06 09 13 18 24 30]  蓝球 [11]
第 03 组：红球 [03 08 15 21 27 30]  蓝球 [01]
```

如果开启推荐理由：

```text
统计推荐号码理由：
第 01 组：红球 [01 06 16 18 27 29]  蓝球 [16]    理由：和值97，奇偶3:3，三区2:2:2，热号、冷号、遗漏值综合

模型推荐号码理由：
第 01 组：红球 [02 07 15 22 28 31]  蓝球 [14]    理由：和值105，奇偶3:3，三区2:2:2，热冷结合
```

---

## 环境要求

建议使用：

```text
Python 3.9+
```

安装依赖：

```bash
pip install requests openai
```

如果你不使用大模型 API，也可以只安装：

```bash
pip install requests
```

也可以创建 `requirements.txt`：

```text
requests
openai
```

然后执行：

```bash
pip install -r requirements.txt
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/icekst/cn-lottery-predict.git
cd cn-lottery-predict
```

### 2. 安装依赖

```bash
pip install requests openai
```

### 3. 复制配置文件

项目中建议提供一个示例配置文件：

```text
config.example.py
```

首次运行前，请复制一份并重命名为：

```text
config.py
```

Git Bash 可以执行：

```bash
cp config.example.py config.py
```

Windows 也可以直接手动复制：

```text
复制 config.example.py
粘贴到同一目录
重命名为 config.py
```

### 4. 修改 config.py

打开 `config.py`，根据需要填写自己的配置。

如果不使用大模型 API，可以设置：

```python
ENABLE_LLM_PREDICT = False
```

如果要使用大模型 API，请填写：

```python
API_KEY = "你的真实API_KEY"
BASE_URL = "你的接口地址"
MODEL_NAME = "你的模型名称"
```

### 5. 运行程序

如果主程序文件名是 `main.py`：

```bash
python main.py
```

也可以直接使用 PyCharm 打开项目，右键主程序文件运行。

---

## 配置文件说明

本项目推荐将所有可变参数放到 `config.py` 中，避免把 API Key 写死在主程序中。

### config.example.py 示例

```python
# -*- coding: utf-8 -*-
"""
示例配置文件

使用方法：
1. 复制本文件
2. 重命名为 config.py
3. 在 config.py 中填写自己的 API Key 和相关参数
"""

# ============================================================
# 大模型 API 配置
# ============================================================

API_KEY = "请在这里填入你的API_KEY"

BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"

# 如果你的接口不支持 json_schema，请改成 False
USE_JSON_SCHEMA = True


# ============================================================
# 程序功能配置
# ============================================================

# 是否输出推荐理由
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
RANDOM_SEED = None
```

---

## 大模型 API 配置

如果你要使用 OpenAI 官方接口，可以这样配置：

```python
API_KEY = "你的OpenAI_API_KEY"
BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"
```

如果你使用 OpenAI 兼容接口，例如 DeepSeek、通义千问、智谱、硅基流动、OpenRouter 等，只需要修改：

```python
API_KEY = "你的API_KEY"
BASE_URL = "你的接口地址"
MODEL_NAME = "你的模型名称"
```

如果你的接口不支持 `json_schema`，请修改：

```python
USE_JSON_SCHEMA = False
```

---

## 不使用大模型 API

如果你只想使用本地统计推荐号码，不想调用大模型 API，可以在 `config.py` 中设置：

```python
ENABLE_LLM_PREDICT = False
```

这样程序只会输出统计推荐号码。

---

## 输出推荐理由

如果需要输出推荐理由，在 `config.py` 中设置：

```python
SHOW_REASON = True
```

如果不需要推荐理由：

```python
SHOW_REASON = False
```

---

## main.py 中如何导入配置

主程序中应该从 `config.py` 导入配置，例如：

```python
try:
    from config import (
        API_KEY,
        BASE_URL,
        MODEL_NAME,
        USE_JSON_SCHEMA,
        SHOW_REASON,
        ENABLE_STAT_PREDICT,
        ENABLE_LLM_PREDICT,
        STAT_PREDICT_COUNT,
        LLM_PREDICT_COUNT,
        HISTORY_COUNT,
        LOOKBACK_COUNT,
        SEND_RECENT_ISSUES_TO_LLM,
        RANDOM_SEED,
    )
except ImportError:
    raise RuntimeError(
        "未找到 config.py 配置文件。\\n"
        "请复制 config.example.py 并重命名为 config.py，"
        "然后填写你的 API_KEY 和相关配置。"
    )
```

---

## .gitignore 配置

为了避免真实 API Key 被上传到 GitHub，请确保 `.gitignore` 中包含以下内容：

```gitignore
# Python cache
__pycache__/
*.py[cod]
*.pyo
*.pyd

# Virtual environment
venv/
.venv/
env/
ENV/

# PyCharm / IDE
.idea/
.vscode/

# Local config / API key
config.py
.env
.env.*

# Logs
*.log

# OS files
.DS_Store
Thumbs.db

# Build / dist
build/
dist/
*.egg-info/
```

重点是：

```gitignore
config.py
.env
.env.*
```

这可以避免本地真实配置文件和环境变量文件被提交到 GitHub。

---

## 如果 config.py 已经被 Git 跟踪过

如果你之前已经把 `config.py` 或包含真实 API Key 的文件提交过，`.gitignore` 不会自动取消跟踪。

需要执行：

```bash
git rm --cached config.py
git commit -m "Stop tracking local config file"
git push
```

如果你已经把真实 API Key 推送到了公开仓库，请立即去大模型平台后台删除或重置旧 Key。  
已经推送到 GitHub 的 Key 应视为泄露，不能继续使用。

---

## 统计模型说明

本项目中的统计推荐并不是真正意义上的预测模型，而是根据历史开奖数据进行加权随机生成。

主要参考特征包括：

- 红球出现频率
- 蓝球出现频率
- 红球冷号
- 蓝球冷号
- 当前遗漏值
- 红球和值
- 奇偶比例
- 三区分布
- 连号数量

生成号码时会过滤部分过于极端的组合，例如：

- 红球和值过低或过高
- 奇偶比例过于极端
- 号码过度集中在某一区间
- 连号数量过多

这些规则只能让号码结构更接近历史常见形态，不能提高中奖概率。

---

## 大模型推荐说明

大模型 API 的作用是：

- 读取程序整理后的历史数据摘要
- 参考热号、冷号、遗漏值、和值、奇偶比、三区分布
- 输出若干组合法双色球号码
- 给出简短推荐理由

需要注意：

大模型无法预测真实开奖结果，输出结果本质上仍然是基于历史数据和提示词生成的参考号码。

---

## 常见问题

### 1. 运行时报错：未找到 config.py 配置文件

请先复制配置示例文件：

```bash
cp config.example.py config.py
```

然后打开 `config.py` 填写配置。

### 2. 运行时报错：未安装 requests

执行：

```bash
pip install requests
```

### 3. 运行时报错：未安装 openai

执行：

```bash
pip install openai
```

如果你不使用大模型 API，可以在 `config.py` 中设置：

```python
ENABLE_LLM_PREDICT = False
```

### 4. 大模型 API 返回 JSON 解析失败

可以尝试在 `config.py` 中设置：

```python
USE_JSON_SCHEMA = False
```

或者检查所使用的大模型平台是否兼容 OpenAI SDK。

### 5. GitHub 推送时不要上传 API Key

请不要把真实 API Key 写进 `main.py` 或提交到 GitHub。

推荐做法：

```text
config.example.py 上传 GitHub
config.py 不上传 GitHub
```

并确保 `.gitignore` 中包含：

```gitignore
config.py
.env
.env.*
```

---

## Git 提交建议

修改配置文件分离后，建议提交这些文件：

```bash
git add main.py config.example.py .gitignore README.md
git commit -m "Move config to separate file"
git push
```

不要提交：

```text
config.py
.env
```

可以通过下面命令检查是否会提交敏感文件：

```bash
git status
```

如果看到 `config.py` 出现在待提交列表中，说明 `.gitignore` 没有生效，或者该文件之前已经被 Git 跟踪。

---

## 风险提示

彩票开奖结果是随机事件，任何基于历史数据的统计、机器学习、大模型推理都无法稳定预测未来开奖结果。

本项目不构成任何投注建议。请理性娱乐，量力而行。

---

## 作者信息

Author: xutao

GitHub: https://github.com/icekst

---

## License

MIT License