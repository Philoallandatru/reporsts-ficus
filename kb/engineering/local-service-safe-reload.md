---
type: Playbook
title: 本机服务的安全重载与只读自检
description: 改动本机 Node 服务代码后，用锁文件 instanceId 校验身份再重载，并用 --dry-run 做不产生副作用的自检。
summary: 先校验锁文件里的实例身份再重载，用 dry-run 做无副作用自检
tags:
- engineering
- local-service
- verification
- debugging
sources:
- 'session: 2026-11-18 finance 看板收盘持仓接口重载与自检'
- C:/Users/Administrator/Documents/Code/tasks/finance/a-share-chart-lab/scripts/workflow.mjs
createdAt: '2026-11-18'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 本机服务的安全重载与只读自检

**改了本机 Node 服务代码后，跑着的进程仍是旧版；重载前必须用锁文件里的 instanceId 校验身份，自检要用 `--dry-run` 这类在写状态之前就返回的开关。**

## 背景

小A看板的工作流服务跑在 8788（行情代理在 8787）。本次改了 `/api/workflow/recap/positions` 的实现（改为按日期读持仓快照），重新构建前端后直接调接口，拿到的仍是旧版行为——返回的是按成交流水重放出来的持仓，和快照里的 3 只完全对不上。

## 核心内容

### 重载流程：先验身份，再停进程

```text
1. 读锁文件 <dataFile>.lock
   { instanceId, pid, apiPort, port, lan }
        |
2. 调 /.well-known/xiao-a-workflow 比对 instanceId
   + 查 pid 的进程命令行，确认是 scripts/workflow.mjs
        |  三者对不上 → 停手，不要杀
        v
3. Stop-Process -Id <pid>，确认进程真的退出
4. 移走残留的锁文件（进程被杀时不会自己清理）
        |
5. 按原参数脱离启动：
   XA_WORKFLOW_PORT=8788  XA_API_PORT=8787
   XA_WORKFLOW_FILE=<私有 workflow.json>
   Start-Process node scripts/workflow.mjs -WindowStyle Hidden
        |
6. 回读接口验证（不是「启动成功」就算完）
```

第 6 步是重点：进程起来 ≠ 新代码在跑。必须真的打一次接口，断言返回内容是新的：

```js
const recap = await read('/api/workflow/recap/positions?date=2026-11-17');
assert.deepEqual(Object.fromEntries(recap.rows.map(p => [p.symbol, p.quantity])),
                 { sh588170: 72400, sh600869: 600, sh603533: 400 });
```

### 自检要挑无副作用的开关

盘中监控脚本有个容易踩的细节：`--dry-run` 在**写状态文件和推送之前**就 `return 0`，所以可以用它做自检而不产生任何副作用。

```text
py holdings/intraday_push.py --dry-run --force
        |
        +-- 打印渲染结果（不写 .private/intraday/briefs/）
        +-- 不推送飞书
        +-- 不覆写 state.json（板块快照仍可用于下次「板块移动」比对）
```

反过来，真正的运行（不带 `--dry-run`）每跑一次就真推一次飞书，并按分钟覆盖存档文件——**不要为了「看退出码」重跑**。

### 停服务前先确认身份

`netstat` 只能告诉你 8788 被谁占着，不能保证那个进程就是你要重启的那个工作流服务。校验顺序是：锁文件的 instanceId → health 接口的 instanceId → 进程命令行包含启动脚本路径。三者一致才动手；任何一个对不上就停手报告，不要「先杀了再说」。

## 关键要点

- 长跑的本机服务**不能挂在会话后台任务上**（有回收时限），要用 `Start-Process` 脱离启动。
- 锁文件在进程被强杀后会残留，下次启动会因 `EEXIST` 拒绝启动——移走它，但先确认旧进程真的没了。
- 改动服务端代码后，跑着的实例不会自动加载新代码；必须重启并回读接口断言。
- 前端改动要 `npm run build`，类型改动要 `npm run typecheck`，回归跑 `node --test`。
- 自检选「在副作用之前返回」的路径，而不是跑一遍真实推送再检查结果。

## 相关

- [[single-account-holdings-snapshot]] — 本次重载是为了让看板读取同一份持仓快照
- [[broker-screenshot-cost-reconciliation]] — 回读断言里的数量与成本就来自那套核对口径
