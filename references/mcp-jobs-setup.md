# mcp-jobs 安装与配置指南

## 什么是 mcp-jobs

**GitHub 仓库：https://github.com/mergedao/mcp-jobs**

**npm 包：https://www.npmjs.com/package/mcp-jobs**

[mcp-jobs](https://github.com/mergedao/mcp-jobs) 是一个开源的 MCP 服务器（作者 @mergedao），
提供 `mcp_search_job` 和 `mcp_job_detail` 工具，可以批量搜索猎聘、BOSS直聘、
智联招聘、51job 等国内招聘平台的真实岗位信息。

它是本 skill 推荐的**最优数据源**：比 WebSearch 返回更多结构化岗位数据，
比手写爬虫更稳定（由社区维护，跟随招聘网站更新）。

## 安装方式

### 方式零：来源选择（优先级递减）

安装时按以下顺序尝试，任一成功即停止。若自动化 agent 将修改 MCP 配置或全局安装依赖，应先说明影响范围，并在写入配置前备份已有文件：

1. **npm registry**：`npm install -g mcp-jobs`
2. **GitHub clone**：`git clone https://github.com/mergedao/mcp-jobs.git && cd mcp-jobs && npm install && npm link`

### 方式一：WorkBuddy（自动配置）

Skill 在阶段一检测到 mcp-jobs 不可用时，会自动：

1. 安装 mcp-jobs npm 包到 WorkBuddy 管理的 Node 环境
2. 将配置写入 `~/.workbuddy/mcp.json`
3. 提示你到「连接器管理」页面点击 "Trust" 启用

无需手动操作。

### 方式二：Claude Code / Cursor / 通用 MCP 客户端

在终端中运行：

```bash
# 确认 Node.js >= 18 已安装
node -v

# 全局安装 mcp-jobs（需要 Playwright，首次会自动下载 Chromium）
npm install -g mcp-jobs

# 测试是否能正常运行
npx mcp-jobs
```

然后在你的 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "mcp-jobs": {
      "command": "npx",
      "args": ["-y", "mcp-jobs"]
    }
  }
}
```

**Claude Code 用户**：配置写到 `~/.claude/mcp.json` 或项目的 `.claude/mcp.json`。
**Cursor / Windsurf 用户**：在设置 → MCP Servers 中添加。

### 方式三：Docker（待官方镜像确认）

目前本文档未确认 mcp-jobs 官方 Docker 镜像地址。不要直接使用占位镜像名运行生产环境容器；如需容器化部署，请优先参考 mcp-jobs 官方仓库发布的最新说明，或自行基于 npm 包构建内部镜像。

## 首次使用

安装后重载 MCP 连接器。首次调用 `mcp_search_job` 时，
mcp-jobs 会自动下载 Chromium（约 150MB，仅一次）。

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `mcp_search_job` 工具不存在 | MCP 未连接或配置未生效 | 重载连接器，确认 config 中 `disabled: false` |
| 调用返回空结果 | Playwright 未安装 Chromium | 运行 `npx playwright install chromium` |
| Timeout | 招聘网站响应慢 | 增加 timeout 或检查网络 |
| `EBADENGINE` 错误 | Node 版本不兼容 | 切换到 Node >= 18 |

## 无 mcp-jobs 时的回退方案

如果因环境限制无法安装 mcp-jobs（如无 Node.js、无浏览器环境），
skill 会自动回退到 WebSearch 路径，使用以下关键词搜索：

```
"AI产品经理 招聘 [行业] [地点] site:zhipin.com OR site:liepin.com"
"AI product manager [industry] [city] hiring [year]"
```

数据覆盖面和结构化程度会略低于 mcp-jobs，但分析框架和报告质量不受影响。
