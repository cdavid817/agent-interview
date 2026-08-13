# MoE

> 所属章节：[Transformer](README.md)｜本文件共 **2** 题。

<a id="trans-051"></a>
### MoE Transformer 为什么能扩大参数量却不同比例增加计算？它的工程难点是什么？（高级）

**MoE为每个Token只激活少量专家，因此总参数可大幅增长而单Token计算近似由激活专家数决定；代价是路由、通信、负载均衡和显存部署更复杂。**

1. Router为Token选择Top-K专家，专家通常是独立FFN；共享Attention保持稠密。容量因子过小会丢弃或重路由Token，过大则浪费显存和计算。
2. 热门专家会形成负载倾斜，需要辅助均衡Loss、Router Z-Loss、容量控制或无辅助Loss策略；专家并行产生All-to-All通信，跨机带宽和拓扑常成为瓶颈。推理还要解决小Batch下专家利用率低与权重常驻显存问题。
3. 评测同时关注任务质量、每Token激活参数、专家负载方差、丢Token率、All-to-All占比、吞吐和故障恢复；参数总量不能直接等同于推理成本或能力。

**相关知识点：** Mixture of Experts、Top-K Routing、Expert Parallelism、Capacity Factor、Load Balancing、All-to-All、Router Z-Loss。
<a id="trans-059"></a>
### 数据并行、张量并行、流水线并行、序列并行和专家并行如何组合？（高级）

**并行策略应按“什么状态装不下、什么通信最昂贵”组合：数据并行切Batch，张量并行切单层矩阵，流水线并行切层，Sequence Parallel切分可逐Token计算的激活，Expert Parallel切MoE专家；超长Attention通常还需单独的Context Parallel。**

1. 数据并行需要同步梯度并分片优化器状态；张量并行每层产生All-Reduce或All-Gather，适合节点内高速互联；流水线并行跨Stage传激活，但会有Bubble和微批调度复杂度。
2. Megatron式Sequence Parallel通常与Tensor Parallel配合，沿序列维切分LayerNorm、Dropout及残差等可逐Token计算的激活，减少重复激活显存；它不等于切分完整Attention上下文。Context Parallel才把长序列的Q/K/V或Attention计算分布到设备，并通过Ring或All-Gather类通信获得跨分片上下文。
3. Expert Parallel把不同MoE专家放到不同设备，会产生All-to-All并受路由倾斜影响。实际3D/4D/5D组合要让高频、大流量通信尽量留在NVLink等高速域；通过参数、梯度、优化器、激活和KV显存模型排除不可行方案，再Profile计算通信重叠、Bubble、链路利用率、吞吐和扩展效率。

**相关知识点：** Data Parallelism、Tensor Parallelism、Pipeline Parallelism、Sequence Parallelism、Context Parallelism、Expert Parallelism、ZeRO、All-Reduce、All-to-All、Pipeline Bubble。
