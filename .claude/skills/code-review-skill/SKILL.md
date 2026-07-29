---
name: code-review-skill
description: 全面的代码审查技能，覆盖 React 19、Vue 3、Rust、TypeScript、TanStack Query v5 等多种技术栈。对代码进行领域感知审查——先分类代码领域，再审查该领域常见的失败模式。当用户需要代码审查、PR review、代码质量检查时使用。
---

# Code Review Skill

A comprehensive code review skill covering multiple technology stacks. Classify the code by domain first, then review for the failure modes that domain actually has.

## Supported Domains

- React 19 — hooks rules, state management, effects, memo patterns
- Vue 3 — composition API, reactivity, component design
- TypeScript — type safety, generics, strict mode patterns
- Rust — ownership, borrowing, lifetimes, unsafe code
- TanStack Query v5 — query keys, cache invalidation, optimistic updates
- General — naming, structure, error handling, performance

## Review Process

1. **Domain Classification** — 识别代码所属的技术领域
2. **Pattern Matching** — 匹配该领域的最佳实践和反模式
3. **Failure Mode Analysis** — 检查该领域常见的失败模式
4. **Severity Scoring** — 按严重程度排序发现的问题
5. **Actionable Report** — 输出可执行的具体修复建议

## Usage

当用户说"review this code"、"审查代码"、"code review"、"检查这段代码"时自动触发。
