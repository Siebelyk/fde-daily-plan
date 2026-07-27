# Day 4: 大模型推理与 KV Cache

> LLM 基础 | 第 1 周

## Demo: KV Cache 原理推演 + Cache 污染攻击模型

手画 4 token 推理时 KV Cache 变化，分析 cache 被污染后如何影响后续生成

- 难度：基础
- 预计时间：1.5h

## 复现步骤

- 1. 画出 4 token 推理每步 KV Cache 变化
- 2. 标注哪些计算被复用
- 3. 分析 K/V 被篡改的影响
- 4. 写攻击场景描述
- 5. 思考防御方案

## 保姆教程

## 纸笔练习

Step 1: K1,V1     Cache: [K1,V1]
Step 2: K2,V2     Cache: [K1,K2,V1,V2]   <- 复用 K1,V1
Step 3: K3,V3     Cache: [K1,K2,K3,...]  <- 全复用
Step 4: K4,V4     只新增 K4,V4

攻击：若 K2/V2 被替换为恶意值
正常:  Q4 dot [K1,K2,K3,K4] -> 正常分布
被污染: Q4 dot [K1,K2_evil,K3,K4] -> 被引导到恶意位置

防御：每 session 独立 cache / cache 完整性校验

## 安全分析
KV Cache 污染是推理服务的高级攻击面
