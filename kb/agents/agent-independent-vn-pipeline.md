---
type: Architecture
title: 不依赖特定 Agent 的本地视觉小说制作流程
description: 用项目文件、稳定素材编号和可恢复任务连接生成模型与可玩游戏。
summary: 用项目文件、稳定素材编号和可恢复任务连接生成模型与可玩游戏
tags:
- agents
- comfyui
- renpy
sources:
- 'session: 2026-09-27 AIGal 下班以后先吃饭'
- C:/Users/Administrator/Documents/ChatGPT/AIGal/work/after-hours-vn/reports/findings.md
createdAt: '2026-09-27'
status: active
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
---

# 不依赖特定 Agent 的本地视觉小说制作流程

**把剧本、素材选择、生成任务和验证结果存成项目文件，Agent 只调用可独立运行的入口，关闭会话不会丢失工程。**

## 背景

本地 AIGal 试验把两个人物、三处场景、24 句中文配音和两段 AI 配乐装配成 Ren'Py 短章，并生成不含模型权重的 Windows 包。使用 RTX 5080 CUDA 推理，未训练 LoRA。

## 核心内容

剧本用 `story.json` 作为唯一可编辑源，生成普通 Ren'Py 脚本和带稳定 ID 的台词清单。角色锚点、提示和模型在 `project.json`，选稿在 `asset-selection.json`，候选与运行记录分别保存。代理选稿明确标记 provisional，不代替用户审美批准。

ComfyUI 返回的任务编号必须先保存再观察。网络中断后恢复同一个编号；提交结果不明或服务历史失联时，不盲目重复生成。一个任务 ID 已产生完整结果后，变更输入必须使用新 ID，避免覆盖候选。

```text
Human / Codex / Pi
        |
    run.ps1
        |
Project data -> Explicit jobs -> Local CUDA models
        |              |                 |
        |          Job records       Candidates
        |                                |
        +-------- Selection <------------+
                     |
               Ren'Py + Tests
                     |
              Standalone game
```

## 关键要点

- 同姿势表情只编辑脸部并合成回母版，复用透明边缘。像素不变的身体比“用同一 seed 再画一次”更可靠；这不证明跨姿势一致。
- 文字描述风格、角色身份参考、空间结构控制是三件事，不能因一个工作流有 LoadImage 就认定它会保留全部属性。
- 音频技术检查只证明文件有效，不证明读音和表演正确。音乐波形衔接平滑也不等于乐句自然。
- 本轮测试覆盖 13 项离线流程检查、5 项实际引擎测试和独立包内引擎测试。真实运行会暴露缺 GUI 图片、状态回标题重置等问题。
- 原型仍缺并发写锁、全量模型哈希锁定和人工审批日志，不应称为完整生产平台。Pi 能接手统一命令，但本轮未调用其推理。

## 相关

- [工程说明](C:/Users/Administrator/Documents/ChatGPT/AIGal/work/after-hours-vn/README.md)
- [实测与下一步实验](C:/Users/Administrator/Documents/ChatGPT/AIGal/work/after-hours-vn/reports/findings.md)
