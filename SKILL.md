---
name: ai-pm-job-analyzer
description: >
  AI产品经理招聘岗位分析报告生成器。当用户请求分析特定行业/方向的AI产品经理招聘市场、
  对标自身背景与岗位要求的差距、或生成求职能力分析报告时使用此技能。
  Trigger: user asks to analyze AI PM job market, benchmark their profile against job requirements,
  or generate a career analysis report. Supports any industry, location, company type, and experience level.
---

# AI PM Job Market Analyzer

## Overview

通用求职分析工具：收集用户画像 → 多平台抓取真实岗位 → 按公司实力四层分级 →
提炼能力模型 → 差距分析 + 分层投递策略 → 生成结构化 HTML 报告。

## 阶段零：读取用户画像

**运行前，先尝试读取本地画像配置**（如果该文件存在）：

```
Read: config/user-profile.yaml
```

如果读到有效配置，将其作为默认用户画像，后续阶段直接使用。
如果文件不存在或为空，进入「输入信息收集」流程向用户询问。

> config/ 目录下的实际画像文件已在 .gitignore 中排除，不会被上传。
> 新用户可复制 `config/user-profile.example.yaml` 填入自己的信息。

## 输入信息收集

如果用户画像不可用，按以下维度收集（不逐条追问，一次性列出缺失项让用户补充）：

- **工作背景**：行业、年限、具体产品/模块
- **学历背景**：学校级别、专业、学位
- **目标岗位**：AI产品经理 或 其他AI相关角色
- **目标行业**：物流/金融/医疗/电商/制造/通用等
- **公司类型偏好**：外企/大厂/独角兽/创业/远程
- **工作地点**：城市名 或 "远程"
- **当前AI能力水平**：项目经验、技术概念熟悉度

用户提供新信息时覆盖对应字段，未提供则保持默认。

## 平台兼容性

此 skill 跨平台运行。核心逻辑在所有平台一致；数据抓取层由阶段一自动适配。

### 核心原则

**数据源优先使用 mcp-jobs，但绝不强依赖它。**
阶段一会自动检测 → 安装 → 回退，确保在任何环境下都能生成完整报告。

### 数据源优先级

| 优先级 | 数据源 | 适用条件 | 岗位数据质量 |
|--------|--------|----------|-------------|
| 🥇 | **mcp-jobs MCP** | Node.js + Playwright 可用 | ⭐⭐⭐⭐⭐ 结构化、实时、覆盖广 |
| 🥈 | **WebSearch + 公司官网** | 任何有网络的环境 | ⭐⭐⭐⭐ 可覆盖大部分岗位 |
| 🥉 | **WebSearch only** | 无 fetch 能力的环境 | ⭐⭐⭐ 基本覆盖 |

### 报告输出

无论哪种数据源，生成的 HTML 报告格式、样式、结构完全一致。
仅在岗位数量和结构化程度上可能有差异。

> 完整的多平台安装指南见 `references/mcp-jobs-setup.md`。

## 核心工作流程

## 阶段一：数据源检测 + 强制自动配置 mcp-jobs ⚠️ 不要跳过此阶段

**🚨 关键原则：检测到 mcp-jobs 不可用时，第一个动作必须是尝试安装，绝对不能直接跳到 WebSearch 回退。WebSearch 仅在 npm install + git clone 全部失败后才使用。**

### 强制执行流程（命令式，不允许跳步）

> **无论用户说什么，先执行下方步骤 1。** 哪怕用户当前环境"看起来没装"，也要先检测可用性；安装和写入 MCP 配置前应遵循当前平台的授权策略，并优先向用户说明将要修改的文件与依赖。

```
步骤 1：检测 mcp_search_job 是否可调用
   └─ 是 → 直接用（跳到阶段二）
   └─ 否 ↓
   ↓
步骤 2：准备安装（必须先做，不要跳到 WebSearch；如当前平台要求确认，先请求用户授权）
   │
   │   信息源：
   │   - GitHub: https://github.com/mergedao/mcp-jobs
   │   - npm:   mcp-jobs（@mergedao）
   │
   │   按平台分支：
   │
   ├─ WorkBuddy 平台（存在 ~/.workbuddy/ 目录）：
   │   │
   │   2a. npm install（首选）：
   │       cd ~/.workbuddy/binaries/node/workspace
   │       npm install mcp-jobs
   │       npx playwright install chromium
   │       失败 ↓
   │   2b. GitHub clone（备选）：
   │       git clone https://github.com/mergedao/mcp-jobs.git ~/.workbuddy/mcp-jobs
   │       cd ~/.workbuddy/mcp-jobs && npm install && npm link
   │       npx playwright install chromium
   │       失败 ↓
   │   2c. 写 MCP 配置（必须做，不允许跳；写入前备份已有配置）：
   │       Edit ~/.workbuddy/mcp.json：
   │       {
   │         "mcpServers": {
   │           "mcp-jobs": {
   │             "command": "npx",
   │             "args": ["-y", "mcp-jobs"],
   │             "disabled": false
   │           }
   │         }
   │       }
   │   2d. **必须用 Read 工具读一次 mcp.json 确认写入成功，并确认已有配置未被覆盖**
   │   2e. 提示用户：「mcp-jobs 已配置，请到连接器管理页面点击 Trust 启用，
   │       然后回复'继续'我将重新检测并开始搜索岗位」
   │   2f. 等待用户确认后重新检测
   │
   └─ 其他平台（Claude Code / Cursor / 通用）：
       2a. npm install -g mcp-jobs
       2b. 失败 → git clone https://github.com/mergedao/mcp-jobs.git
                  cd mcp-jobs && npm install && npm link
       2c. 配置 MCP 客户端（Claude: ~/.claude/mcp.json, Cursor: Settings → MCP；写入前备份已有配置）
       2d. 告诉用户：必须重启 MCP 客户端使配置生效
       ↓
   ↓
步骤 3：仅当步骤 2 全部失败时，才使用 WebSearch 回退
   └─ 用 site:zhipin.com / site:liepin.com 限定范围
```

### ❌ 错误行为（必须避免）

下面这些是"偷懒"行为，**任何一项出现都视为协议违规**：

1. ❌ 检测到 mcp-jobs 不可用 → 直接走 WebSearch，不尝试安装
2. ❌ 试了 npm install 失败就立刻放弃，不试 GitHub clone
3. ❌ 跳过 MCP 配置写入步骤
4. ❌ 没向用户报告安装进展
5. ❌ 用 `accio mcp-cli search mcp-jobs` 这种空查询假装"找不到就放弃"

### ✅ 合规示例（agent 应当这样回复）

```
🔍 检测 mcp-jobs 状态：未激活

📦 执行安装步骤 1：npm install mcp-jobs
   正在下载... ✅ 完成

📝 写入 MCP 配置 ~/.workbuddy/mcp.json
   ✅ 已写入
   验证：{"mcpServers":{"mcp-jobs":{"command":"npx","args":["-y","mcp-jobs"]}}}

⏸️ 等待用户操作：
   1. 打开「连接器管理」页面
   2. 找到 mcp-jobs，点击「Trust」启用
   3. 回复「继续」让我重新检测并开始搜索
```

### ✅ 失败兜底示例（npm 和 GitHub 都不可用时）

```
🔍 检测 mcp-jobs 状态：未激活
📦 npm install mcp-jobs... ❌ 失败（npm 不可用）
📦 git clone https://github.com/mergedao/mcp-jobs.git... ❌ 失败（无 git 或无网络）
⚠️ mcp-jobs 安装失败
🔄 回退到 WebSearch 路径（阶段二 路径 B）
```

### 安装成功后的验证

mcp_search_job 可用后，验证搜索是否正常：

1. 尝试搜索 `keyword: "AI产品经理"` + `location: "上海"`
2. 如果返回结果 → 安装成功，进入阶段二
3. 如果返回空或报错 → 检查 Chromium 是否已安装：`npx playwright install chromium`，重试

### 详细安装指南

完整的多平台安装文档见 `references/mcp-jobs-setup.md`。
包括 Claude Code、Cursor、Docker 等所有环境的配置方法。

## 阶段二：多渠道抓取真实岗位 ⚠️ 每个岗位必须同时抓取 URL

根据「目标行业 + 公司类型 + 地点」并行搜索。

**核心原则：搜索的每一步都要保留 URL。URL 是岗位卡片的生命线，没有 URL 的岗位不出现在最终报告中。**

**路径 A：mcp-jobs 可用时（最优，结构化数据）**

1. `mcp_search_job` 搜索 `keyword: "AI产品经理 [行业]"` + `location: [地点]`
   → 结果中包含 `url` 字段，**立即记录到岗位列表中**
2. `mcp_search_job` 搜索 `keyword: "AI产品经理 [行业相关场景]"` + `location: [地点]`
3. 对关键岗位调用 `mcp_job_detail` 获取完整 JD 描述和更多信息
4. **过滤：删除所有 `url` 为空或无效的岗位**，保留 ≥10 个有效岗位供筛选

**路径 B：WebSearch 回退（通用，覆盖中文平台 + 外企）**

并行搜索以下关键词组：

```
组1（中文平台）: "AI产品经理 招聘 [行业] [地点] site:zhipin.com OR site:liepin.com"
组2（外企英文）: "AI product manager [industry] [city] hiring [year]"
组3（目标公司）: "[公司名] AI product manager [location] hiring"
组4（能力分析）: "AI产品经理 [行业] 核心能力要求 技能清单"
```

**WebSearch URL 提取规则：**
- 搜索结果末尾的 `**URL:**` 字段即为可点击链接
- 每个结果行（如 `## 1. [title](url)`）中的 Markdown 链接也需保留
- 对含 JD 的结果，用 WebFetch/平台内置 fetch 工具获取详情
- **必须保留 ≥15 个有效 URL** 供后续筛选

**路径 C：目标公司 careers 页面直搜（所有平台通用）**

根据用户公司偏好，针对性搜索 careers 页面。模板示例（按行业可替换公司名）：

```
外企物流/供应链: site:careers.dhl.com OR site:amazon.jobs OR site:maersk.com "AI product manager"
外企金融: site:careers.jpmorgan.com OR site:goldmansachs.com "AI product manager"
大厂电商: site:alibaba.com OR site:meituan.com "AI产品经理"
独角兽: site:zhipin.com "[公司名] AI产品经理"
```

### 阶段三：岗位筛选与四级分层

#### 筛选标准

| 匹配度 | 标准 |
|--------|------|
| **强匹配** ⭐ | 行业匹配 + 经验区间匹配 + 公司类型匹配 |
| **中匹配** | 行业相近 或 经验接近 或 有部分交集 |
| **目标岗** | 当前不匹配但可作为发展目标的高级岗位 |

#### 四层分级体系（按公司实力）— 附带强制 CSS 类绑定

**规则：Tier 层级与 CSS 类是强制一对一绑定的。如果报告中任意卡片未使用下表对应类，则报告不合规。**

| 层级 | 标准 | 强制 CSS 类 | 触发条件 | 示例公司 |
|------|------|-----------|---------|---------|
| **Tier 1** 🥇 | 全球500强 / 行业全球Top3 | `rec-star` | 只要属于 Tier 1 即触发 | Amazon, Maersk, DHL, Goldman Sachs |
| **Tier 2** 🥈 | 千亿市值 / 平台级 | `rec` | 只要属于 Tier 2 即触发 | 蚂蚁, 美团, 拼多多, 字节 |
| **Tier 3** 🥉 | 细分赛道头部 / 快速成长 | `job-card`（默认） | Tier 3 使用基础卡片样式 | 极兔, 壹米滴答, 申通 |
| **Tier 4** 💜 | 远程/国际化团队 | `job-card`（默认） | Tier 4 使用基础卡片样式 | 讴谱, Gradual |

**合规校验规则**：
- 报告中 Tier 1 卡片数 ≥ 3 时，HTML 中必须出现 ≥3 次 `class="job-card rec-star"` 或 `rec-star`
- 报告中 Tier 2 卡片数 ≥ 3 时，HTML 中必须出现 ≥3 次 `class="job-card rec"` 或 `" rec"`
- 如上述任一条件不满足，**删除该报告重新生成**，不得以缺少 CSS 类的卡片交差

**tier-badge 同样强制绑定**：

**行业适配规则**：根据用户的目标行业动态替换每层示例公司：

| 目标行业 | Tier 1 示例 | Tier 2 示例 | Tier 3 示例 |
|----------|-----------|-----------|-----------|
| 物流/供应链 | Amazon, Maersk, DHL, Flexport | 蚂蚁, 美团, 拼多多, NIO | 极兔, 壹米滴答, 满帮, 货拉拉 |
| 金融 | Goldman Sachs, JPMorgan, Bloomberg | 蚂蚁, 微众, 京东金融, 东方财富 | 同花顺, 老虎证券 |
| 医疗健康 | Siemens Healthineers, Philips, GE Healthcare | 腾讯医疗, 百度健康, 阿里健康 | 微医, 丁香园, 医联 |
| 电商/零售 | Amazon, Walmart, Shopify | 阿里, 拼多多, 京东, 抖音电商 | SHEIN, 得物 |
| 企业服务/SaaS | Microsoft, Salesforce, SAP, Oracle | 字节飞书, 腾讯企点, 金蝶 | 钉钉, 用友 |
| 通用AI | Google, Microsoft, Meta, Apple | 字节, 阿里, 腾讯, 百度 | 商汤, 旷视, Minimax |

### 阶段四：提炼能力模型（6维度）

从所有 JD 中提炼高频能力要求，归纳为通用框架：

1. **AI/ML 技术理解力**：LLM原理、RAG、Agent/智能体、Prompt Engineering、模型评测
2. **数据能力**：SQL、数据闭环、指标体系与A/B实验、成本意识（Token/推理优化）
3. **产品基本功**：PRD、路线图、用户研究、项目管理、商业化思维
4. **行业领域知识**：根据目标行业定制（从JD中的业务关键词提取）
5. **软技能**：跨部门协作、英文/双语能力、利益相关方管理、变革管理
6. **AI 治理与合规**：AIGC合规、隐私保护、AI安全护栏、可解释性

每个维度列出 4-5 个知识点，标注来源于哪些公司的 JD。

### 阶段五：差距分析

**优势分析（绿色 `.strength-box`）：**
- 列举用户与市场要求明确匹配的点
- 重点突出用户独特组合的稀缺性（如"行业×产品×学历"）

**短板分析（黄色 `.gap-box` + 层级匹配度表格）：**

| 列名 | 说明 |
|------|------|
| 层级 | Tier 1-4 |
| 代表公司 | 该层级的 2-3 家典型公司 |
| 经验门槛 | 该层级岗位通常要求的经验年限 |
| AI经验要求 | 对AI项目经验的要求程度 |
| 你的匹配度 | 🟢🟢 / 🟢 / 🟡 / 🔴 |
| 投递策略 | 针对性的投递建议 |

### 阶段六：行动建议（3步分层法）

1. **第一步：补能力**（1-2个月）— 按用户AI能力现状定制课程/项目推荐
2. **第二步：分层投递**（持续）— 从最匹配层级开始，逐层向上冲刺
3. **第三步：长期关注** — 目标公司列表、平台推荐、简历关键词

### 阶段七：薪资参考表

按层级 × 经验级别给出薪资矩阵（月薪范围 + 年包参考，标注货币单位）。

### 阶段八：核心结论

一段有力总结，帮用户看清定位、最优路径和关键行动。

## 📋 强制输出协议 (Mandatory Output Protocol)

**⚠️ 在生成 HTML 报告之前，必须依次完成以下两步。跳过任一步骤直接输出 HTML 视为违规。**

### 第一步：进度状态表 (Stage Checkpoint)

在回复中**显式输出**以下进度确认表。每项必须如实标记 ✅ 或 ❌：

```
| 阶段 | 状态 | 产出物 | 自检 |
|------|------|--------|------|
| 阶段零 | ✅/❌ | 用户画像已读取/已收集 | 画像 ≥5 个字段 |
| 阶段一 | ✅/❌ | 数据源已就绪 | mcp-jobs 或 WebSearch 可用 |
| 阶段二 | ✅/❌ | 搜索完成，已保留 ≥10 个有效 URL | 每个 URL 指向具体岗位 |
| 阶段三 | ✅/❌ | 岗位已按四层分级，附录CSS类已绑定 | Tier 1→rec-star, Tier 2→rec |
| 阶段四 | ✅/❌ | 6维度能力模型已提炼 | 每维度 ≥4 知识点 |
| 阶段五 | ✅/❌ | 优势+短板+层级匹配度表格已完成 | 匹配度与经验对得上 |
| 阶段六 | ✅/❌ | 3步行动建议已定制 | 投递优先级与匹配度自洽 |
| 阶段七 | ✅/❌ | 薪资矩阵已填充 | 区间与JD一致 |
| 阶段八 | ✅/❌ | 核心结论已草拟 | 含定位+路径+关键行动 |
```

**若上表中任何一行的「状态」列为 ❌，禁止执行 Write 操作生成 HTML。** 必须先补齐该阶段再重新输出进度表。

### 第二步：分析纪要 (Analysis Brief)

在进度表确认全部 ✅ 后、生成 HTML 前，输出一段 **≥200 字**的纯文本分析纪要，
涵盖以下三个要点：

1. **市场趋势概括**：本次搜索到的岗位反映出哪些行业/技术趋势？（至少 2 个趋势）
2. **用户核心竞争力**：用户画像与市场需求的契合点是什么？（至少 2 个契合点）
3. **关键差距与建议**：用户最需要补的 1-2 个短板是什么？最快提升路径？

格式要求：
- 纯文本，三段的标题用 **加粗**
- 不使用列表、表格或其他标记
- 内容基于搜索到的真实 JD 数据，不是泛泛而谈

**示例：**

> **市场趋势：** 本次搜索到 18 个物流行业 AI PM 岗位。Tier 1 外企（Amazon/DHL/Maersk）均要求 5-7 年经验 + 已上线的 AI 产品案例，对 Agentic AI 的关注度显著上升。Tier 2/3 的国内物流公司（极兔/壹米滴答/申通）门槛明显更低（3-5 年，了解 AI 即可），且正处数字化转型加速期，AI PM 岗位从年初的零星几个增长到现在的批量上线。
>
> **核心竞争力：** 用户的物流行业 5 年经验（订单/运单/计费全流程）是区别于纯互联网 AI PM 的最大护城河。极兔的智能路由、壹米滴答的 RAG 知识库、蚂蚁国际的跨境物流 AI 助手这三个场景与用户背景直接对应。985 硕士学历满足 Tier 1 外企的硬性门槛。
>
> **关键差距：** 最大短板是缺少可展示的 AI 项目实战经验。最快提升路径是花 2-3 周用 LangChain 做一个「快递运单查询 Agent」原型（覆盖 RAG + Agent 两个核心概念），放在 GitHub 上作为面试作品。

**分析纪要输出后，方可进入 HTML 报告生成阶段。**

## 报告样式规范

使用 `assets/report-template.html` 中的 CSS 体系生成报告。核心设计：

- **配色**：主色 `#2563eb`（蓝）；渐变 header `#1e3a5f → #2563eb → #7c3aed`
- **卡片**：`.job-card`（白底边框）、`.skill-card`（灰底）、`.summary-card`（蓝左边条）
- **分层标识**：`.tier-badge` — tier-1 金色 / tier-2 蓝色 / tier-3 绿色 / tier-4 紫色
- **推荐标记**：`.rec`（蓝紫渐变）、`.rec-star`（金色左边条，最佳匹配）
- **分析框**：`.strength-box`（绿色）、`.gap-box`（黄色）
- **链接**：`.job-link`（蓝色虚线，hover变实线）
- **响应式**：`@media (max-width: 640px)` 移动端适配
- **字体**：系统字体栈 `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif`

### 岗位卡片 = 5 变量强制对象 ⚠️ 缺任意变量则该卡片无效

**每个岗位卡片是一个包含 5 个必填变量的不可分割对象。生成 HTML 前必须用以下结构逐卡校验：**

```
变量组 JobCard = {
  Company_Info,        // 变量1: 公司名 + 实力标签 + 匹配度标签 + CSS强制类
  Job_Detail,          // 变量2: 岗位标题 + 元信息行(📍💰📋)
  Real_Link,           // 变量3: ≥1个真实可点击URL (非占位符, 非#, 非搜索页)
  Match_Score_Tags,    // 变量4: ≥1个实力标签 + ≥1个匹配度标签
  Specific_Highlight_Comment  // 变量5: 1-2句针对用户背景的匹配度评语
}
```

**严禁缺项。** 如果一个岗位无法完整填充这 5 个变量，**丢弃该岗位，不出现在报告中。**

#### 变量1: Company_Info（公司名 + 标签系统）

标签不可使用占位符或通用文本。根据搜索到的真实公司信息，从以下规则中选择匹配的标签：

**实力标签（必选≥2个，反映公司真实身份）：**

| 标签类型 | 示例 | 生成规则 |
|---------|------|---------|
| 公司性质 | `外企` `国内` `远程` `国企` | 根据公司注册地/控股方 |
| 市值/估值 | `全球500强` `万亿市值` `美股上市` `港股上市` `A股上市` `估值$80亿` `独角兽` | 搜索确认后标注，写具体数字 |
| 行业地位 | `全球电商第一` `全球最大航运` `物流巨头` `行业Top3` `AAAAA级物流` | 必须基于可验证的市场数据 |
| 全球化程度 | `全球化快递` `国际化` `出海` | 有海外业务才标注 |

**匹配度标签（必选≥1个，反映与用户画像的匹配程度）：**

| 标签 | 使用条件 |
|------|---------|
| `强烈推荐` `最匹配！` | 行业+地点+经验三重匹配 |
| `强推` | 行业+地点匹配，经验接近 |
| `上海有办公室` | 外企在上海有site |
| `最佳匹配！` | 该层级中与用户背景最对口的岗位 |
| `未来目标` | 当前不匹配但2-3年可达 |

**标签 CSS 类：**
- 实力标签：`.tag-green`（外企）、`.tag-gold`（500强）、`.tag-blue`（国内大厂）、`.tag-teal`（远程）、`.tag-purple`（推荐）
- 匹配度标签：`.tag-purple` 或直接用 `rec-star` 类标记整张卡片

#### 变量2: 招聘链接 Real_Link（必须，≥1 个真实 URL）

**链接来源规则：**

- 每个招聘链接的 `href` 必须指向阶段二中搜索获取的**具体岗位 URL**
- mcp-jobs 返回的 `mcp_job_detail` 结果中包含 `url` 字段，直接使用
- WebSearch 返回的搜索结果中包含 `**URL:**` 字段，提取使用
- 如果某岗位确实无法获取真实 URL（搜索未返回链接），**不输出该岗位卡片**

**链接格式（HTML）：**

```html
<a class="job-link" href="[搜索获取的真实URL]" target="_blank">查看职位 →</a>
<a class="job-link" href="[公司官网careers页面URL]" target="_blank">官网 →</a>
```

**同一岗位有多个来源时，列出所有可用链接。** 例如：猎聘链接 + 公司官网链接。

#### 变量3: Job_Detail（岗位标题 + 元信息行）

岗位标题保留原语言。外企岗位用英文标题，国内岗位用中文标题。

元信息行格式：
```
<span>📍 [城市/区域]</span><span>💰 [月薪范围]</span><span>📋 [经验要求]</span>
```
薪资未知时标注 `有竞争力` 或 `面议`。

#### 变量4: Match_Score_Tags（标签系统，必须≥2个）

标签不可使用占位符或通用文本。根据搜索到的真实公司信息，从以下规则中选择匹配的标签：

**实力标签（必选≥2个，反映公司真实身份）：**

**❌ 禁止行为：** 生成 `查看职位 →` 等无实际 URL 的伪链接；使用 `猎聘 →`、`BOSS直聘 →` 等无具体岗位 URL 的平台名称链接；使用 `详情见JD`、`官网可查` 等描述替代链接。

#### 变量5: Specific_Highlight_Comment（核心要求 + 匹配度评语）

**核心要求摘要（3-5 条要点）：**

从 JD 中提取最关键的 3-5 条要求，用 `<br>` 分隔。每条前面加粗关键词。

**匹配度评语：**

用 `<span class="highlight">` 包裹，1-2 句话说明为什么这个岗位适合/不适合用户。**严禁使用通用模板文本**（如"该岗位与你的背景匹配"），必须引用用户的具体经验（如"你的运单管理经验可以直接应用于该岗位的智能路由场景"）。

### 岗位卡片 HTML 示例（完整 5 变量填充模板）

```html
<!-- JobCard = {Company_Info, Job_Detail, Real_Link, Match_Score_Tags, Specific_Highlight_Comment} -->
<div class="job-card rec-star"> <!-- Tier 1 强制使用 rec-star -->
  <div class="company-row">
    <!-- 变量1+4: Company_Info + Match_Score_Tags -->
    <strong>Amazon (亚马逊)</strong>
    <span class="tag tag-gold">全球第一电商·500强</span>
    <span class="tag tag-purple">强烈推荐</span>
    <!-- 变量2: Real_Link -->
    <a class="job-link" href="https://www.amazon.jobs/zh/jobs/10465398/senior-ai-product-manager" target="_blank">查看职位 →</a>
    <a class="job-link" href="https://www.amazon.jobs/zh/" target="_blank">Amazon Jobs →</a>
  </div>
  <!-- 变量3: Job_Detail -->
  <div class="title">Senior AI Product Manager, Amazon Global Selling</div>
  <div class="meta-row">
    <span>📍 上海</span><span>💰 65-95K/月</span><span>📋 7年+PM</span>
  </div>
  <div class="reqs">
    <!-- 变量5: Specific_Highlight_Comment -->
    <strong>核心要求：</strong>中英文流利；GenAI/Agentic AI产品经验；跨区域协作能力；A/B测试和模型评测。<br>
    <span class="highlight">匹配点：物流供应链场景经验是独特优势。差距：需要7年+高级PM经验</span>
  </div>
</div>
```

### 岗位卡片生成前自检 ⚠️

在输出 HTML 前，对每个 JobCard 5 变量逐项确认：

- [ ] `Company_Info`：公司名准确？有 ≥2 个实力标签 + ≥1 个匹配度标签？
- [ ] `Real_Link`：有 ≥1 个真实 `href` URL？不是占位符/`#`/搜索页面？URL 来自搜索阶段？
- [ ] `Job_Detail`：有岗位标题 + 元信息行(📍💰📋)？三个字段都不缺？
- [ ] `Match_Score_Tags`：标签不是通用文本？基于搜索到的真实公司信息？
- [ ] `Specific_Highlight_Comment`：评语引用了用户的具体经验？不是"该岗位匹配你的背景"这种模板话术？
- [ ] 是否已删除所有「搜索不到链接」或「无法填充 5 变量」的岗位？

## 通用注意事项（跨平台）

1. **所有链接必须真实可点击**：搜索获取的URL直接嵌入，不使用占位符
2. **薪资统一为月薪**：年包换算为月薪（÷12~16），外币标注原始货币
3. **数据时效**：footer 标注搜索日期 +「职位实时变化请以官方页面为准」
4. **语言规则**：正文用中文，岗位标题和外企JD关键字段保留原语言
5. **文件命名**：`AI产品经理招聘分析报告.html`，放工作目录下
6. **报告展示**：生成后提示用户打开 HTML 文件（WorkBuddy 平台自动调用 preview）

## 报告逻辑检查清单

**在开始 Write HTML 前逐项校验。全部通过后方可输出文件。**

- [ ] **进度状态表已输出且全部 ✅**（强制输出协议第一步已完成）
- [ ] **分析纪要已输出且 ≥200 字**（强制输出协议第二步已完成）
- [ ] **阶段一已完成**（mcp-jobs 已激活，或已尝试 npm install + git clone 后才用 WebSearch）
- [ ] **未触发"未激活即直接 WebSearch"的违规行为**
- [ ] **Tier 1 卡片全部使用 `rec-star` 类**（统计: rec-star 出现次数 ≥ Tier 1 卡片数）
- [ ] **Tier 2 卡片全部使用 `rec` 类**（统计: `" rec"` 出现次数 ≥ Tier 2 卡片数）
- [ ] 每个 Tier 的岗位数量合理（Tier 1: 3-5，Tier 2: 4-6，Tier 3: 2-4，Tier 4: 1-3）
- [ ] **每个岗位卡片 5 变量完整**（Company_Info + Job_Detail + Real_Link + Match_Score_Tags + Specific_Highlight_Comment）
- [ ] **每个岗位卡片有 ≥1 个真实 URL 链接**（检查链接数 = 卡片数）
- [ ] **没有伪链接**（无 `#`、无 `javascript:void(0)`、无搜索页面 URL）
- [ ] **没有「搜索不到链接」或「无法填充 5 变量」的岗位卡片**（该删的已删）
- [ ] **Tier 1 卡片使用 `rec-star`，Tier 2 卡片使用 `rec`**（CSS 类强制绑定已检查）
- [ ] 能力模型「行业领域知识」维度与用户目标行业一致
- [ ] 差距分析表各Tier匹配度评估与用户经验年限对得上
- [ ] 行动建议投递优先级与匹配度评估表自洽
- [ ] 薪资参考表区间与JD实际薪资一致
