# Day 5: 开源模型生态与安全评估

> LLM 基础 | 第 1 周

## Demo: 开源模型安全审计清单 + Pickling 攻击演示

制作模型对比表含安全维度，演示 Pickling 攻击风险，写安全使用 checklist

- 难度：进阶
- 预计时间：2h

## 复现步骤

- 1. 对比 Llama-3/Qwen2.5/DeepSeek-V3 参数量上下文许可证
- 2. 加入安全维度
- 3. 演示 pickle 反序列化攻击
- 4. 写安全使用 checklist

## 保姆教程

## 代码
~~~python
import pickle

# Pickling 攻击演示（教育目的）
class EvilPickle:
    def __reduce__(self):
        return (print, ("[DEMO] 恶意pickle会执行任意代码",))

pickle.loads(pickle.dumps(EvilPickle()))
# 触发打印，模拟 RCE

print("""
安全使用 Checklist:
1. 只从官方仓库下载
2. 优先 safetensors 格式
3. 沙箱环境首次加载
4. 不部署 base model
5. 加输入输出过滤层
""")
~~~

## 安全分析
开源模型最大风险是供应链：恶意 pickle 可在加载时执行任意代码
