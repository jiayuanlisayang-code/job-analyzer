# Job Market Analyzer 🧠📊

[![Platform](https://img.shields.io/badge/platform-WorkBuddy%20%7C%20Claude%20Code%20%7C%20Cursor-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://github.com/jiayuanlisayang-code/job-analyzer/actions/workflows/validate.yml/badge.svg)](https://github.com/jiayuanlisayang-code/job-analyzer/actions/workflows/validate.yml)

**通用招聘岗位分析报告生成器** — 根据目标岗位/行业/城市从多平台抓取真实岗位，按公司实力四层分级，
提炼能力模型，对标用户差距，生成结构化 HTML 求职分析报告。

## 快速开始

**推荐路径：两步即可使用，无需手动编辑文件。**

1. **向 AI 助手说出你的需求：**

```
帮我分析目标岗位的招聘市场，例如：AI产品经理、数据分析师、增长产品经理
```

2. **在聊天框里回答几个问题**（首次使用时 Skill 会自动引导你填写画像，下次直接跳过）：

> 工作背景？学历？想去哪个行业/城市/公司？

Skill 会自动：
- 读取或收集你的画像（首次使用引导填写，可保存到本地，下次无需重复输入）
- 检测并安装 mcp-jobs（如需）
- 搜索匹配岗位
- 生成 HTML 报告（默认输出到 `reports/` 目录）

### 可选：使用 YAML 预填写画像

如果你希望提前配置个人画像，也可以复制 `config/user-profile.example.yaml` 为 `config/user-profile.yaml` 后填写。该文件可能包含个人敏感信息，应通过 `.gitignore` 保持本地私有。

## 功能架构

```
用户画像 → 多平台岗位抓取 → 四层分级 → 能力提炼 → 差距分析 → 行动建议 → HTML报告
```

### 四层分级体系

| 层级 | 公司类型 | 分析视角 |
|------|---------|---------|
| **Tier 1** 🥇 | 全球500强外企 | 目标岗，2-3年发展方向 |
| **Tier 2** 🥈 | 互联网大厂 | 跳板岗，1-2年可达 |
| **Tier 3** 🥉 | 行业独角兽/上市 | 主攻岗，当前最佳匹配 |
| **Tier 4** 💜 | 远程/国际化团队 | 灵活选择 |

### 支持行业

物流供应链（完整公司清单）/ 金融 / 医疗健康 / 电商零售 / 企业服务(SaaS) / 通用AI — 物流供应链已有较完整保底公司列表，其他行业依赖实时发现 + Tier 动态分级。

## 数据源

| 优先级 | 数据源 | 适用条件 |
|--------|--------|----------|
| 🥇 | **mcp-jobs** (猎聘/Boss/智联/51job) | 自动检测+安装 |
| 🥈 | **WebSearch + 官网** | 任何环境 |
| 🥉 | **WebSearch only** | 零依赖回退 |

> 详细安装指南见 [`references/mcp-jobs-setup.md`](references/mcp-jobs-setup.md)

## 报告示例

生成的 HTML 报告包含：

- 📋 **精选岗位卡片**（含真实招聘链接）
- 🧠 **动态能力模型**（根据目标岗位 + JD 高频词自动生成 5-7 维度）
- 📊 **差距分析表**（四层级匹配度评估）
- 🎯 **三层投递行动路线图**
- 💰 **薪资参考矩阵**

## 文件结构

```
job-market-analyzer/
├── SKILL.md                          # 核心工作流程
├── assets/
│   └── report-template.html          # HTML 报告 CSS 模板
├── config/
│   └── user-profile.example.yaml     # 用户画像模板（可选复制后填写）
└── references/
    └── mcp-jobs-setup.md             # 多平台 mcp-jobs 安装指南
```

## 兼容性

| 平台 | 状态 |
|------|------|
| WorkBuddy | ✅ 完全支持（含 mcp-jobs 自动安装） |
| Claude Code / Cursor | ✅ 支持（需手动安装 mcp-jobs） |
| 通用环境 | ✅ WebSearch 回退可用 |

## 输出文件

生成的报告默认保存在 `reports/` 目录，命名为 `{日期}-{目标岗位}-{城市}.html`。该目录已在 `.gitignore` 中忽略，报告文件不会提交到版本控制。

## License

MIT — 详见 [LICENSE](LICENSE)

## 开发校验

修改报告模板或 Skill 规则后，建议运行：

```bash
python3 scripts/validate_report_template.py
```

CI 会在每次 push 和 PR 时自动运行该校验（[`.github/workflows/validate.yml`](.github/workflows/validate.yml)）。
