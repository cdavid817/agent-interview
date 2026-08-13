# 推理与性能优化

> 所属章节：[Transformer](README.md)｜本文件共 **1** 题。

<a id="trans-056"></a>
### TRANS-056 · Prefill 与 Decode 的瓶颈为什么不同？何时考虑分离部署？（高级）

> 稳定 ID：`TRANS-056`｜原题号：56

**Prefill一次处理整段输入，通常更偏计算密集；Decode每步只生成一个Token并频繁读取权重与KV Cache，通常更偏内存带宽和调度。**

1. 长Prompt会让Prefill占用大块算力并拉高TTFT；Decode阶段大量并发小步执行，目标是稳定TPOT和高Batch利用率。二者混跑可能互相干扰，长Prefill阻塞交互式Decode。
2. 分离部署可让Prefill节点和Decode节点使用不同并行度、Batch与硬件，并独立扩缩容；代价是KV Cache跨节点传输、路由、容错和资源碎片。短上下文或低负载下，传输开销可能超过收益。
3. 应根据输入输出长度分布、TTFT/TPOT SLO、KV传输带宽和峰值并发建模，再用端到端压测决定；同时设置请求取消、背压和故障回退。

**相关知识点：** Prefill-Decode Disaggregation、Compute-bound、Memory-bound、KV Transfer、TTFT、TPOT、Head-of-Line Blocking。
