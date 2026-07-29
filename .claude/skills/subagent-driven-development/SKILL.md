---
name: subagent-driven-development
description: 中文 Subagent 驱动开发工作流。将复杂任务自动分解为子任务，启动专用子 Agent 并行处理，自动汇总结果。适用场景：大型功能开发、多模块重构、跨项目任务。41 installs on skills.sh.
source: 21307369/superpowers-zh
triggers: Subagent, 子代理, 并行任务, 多任务, 分解任务, 自动化开发
---

# Subagent 驱动开发 (中文)

将复杂开发任务分解为多个子任务，驱动专用 Subagent 并行执行。

## 核心理念

**不要让一个 Agent 做所有事。** 像管理团队一样管理 Agent：
- 拆解任务 → 分配给专家 → 并行执行 → 汇总审查

## 工作流程

### 第一步：任务分析
1. 阅读用户需求
2. 识别可并行的子任务
3. 评估每个子任务的复杂度

### 第二步：Subagent 定义
为每个子任务创建专用 Subagent：
```
名称: bug-finder
职责: 扫描代码库寻找潜在 bug
工具: read, search, grep
输出: bug 列表（含文件和行号）
```

### 第三步：并行执行
- 同时启动所有 Subagent
- 每个 Subagent 专注自己领域
- 结果写入独立文件防止冲突

### 第四步：汇总整合
- 主 Agent 读取所有 Subagent 输出
- 去重、排序、形成最终报告
- 展示给用户确认

## 常见 Subagent 类型

| 类型 | 用途 |
|------|------|
| code-reviewer | 代码审查 |
| test-writer | 编写测试 |
| bug-finder | 发现 bug |
| doc-generator | 生成文档 |
| refactor-agent | 重构代码 |
| security-scanner | 安全扫描 |

## 适用场景

- 需要同时修改多个模块
- 大型 PR 审查
- 跨项目重构
- 全栈功能开发（前端 + 后端 + 数据库）
