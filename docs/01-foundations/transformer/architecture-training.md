# 网络结构与训练

> 所属章节：[Transformer](README.md)｜本文件共 **4** 题。

<a id="trans-048"></a>
### 1. Pre-Norm、Post-Norm 和 Sandwich Norm 有什么区别？为什么深层模型常用 Pre-Norm？（高级）

**归一化位置改变残差支路的梯度路径：Pre-Norm在子层前归一化，提供更直接的恒等梯度通道；Post-Norm在残差相加后归一化，表示性质不同但深层训练更敏感。**

1. Pre-Norm形式近似`x + F(Norm(x))`，即使子层梯度不稳定，残差主干仍可传播；因此通常更容易训练深层网络并减少Warmup敏感性。Post-Norm为`Norm(x + F(x))`，可能获得更强的层间变换，但需精细初始化、学习率和残差缩放。
2. Sandwich Norm在子层前后都归一化，可改善特定大规模或低精度训练稳定性，却增加归一化算子、显存读写和计算开销；只有隐藏维被跨设备切分且归一化统计需要跨卡聚合时，才会额外体现为通信开销。具体实现还要明确最后是否存在Final Norm，不能只看架构名称。
3. 比较时记录训练Loss、梯度范数、激活幅度、NaN率、收敛Token数和最终任务质量；稳定不等于效果一定更好，结论依赖深度、初始化与优化器。

**相关知识点：** Pre-LN、Post-LN、Sandwich Norm、残差通路、梯度传播、Residual Scaling、Training Stability。
<a id="trans-049"></a>
### 2. RMSNorm 与 LayerNorm 有什么区别，为什么很多大模型选择 RMSNorm？（高级）

**LayerNorm同时去均值并按方差缩放，RMSNorm只按均方根缩放；后者计算更简单，并保留了对激活尺度的控制。**

1. 对向量`x`，LayerNorm使用`(x-mean)/std`，RMSNorm使用`x/rms(x)`，随后乘可学习权重。RMSNorm省去均值中心化，内核更易融合，主要减少统计计算和显存访问；是否降低跨卡通信取决于隐藏维切分与归一化实现，不能作为普遍结论。
2. RMSNorm不具备平移不变性，但残差网络、初始化和训练过程常能适应该差异；不能据此断言它在所有模型上更优。epsilon、累积精度和归一化维度错误都可能在FP16/BF16下放大不稳定。
3. 选型需在相同训练预算下比较收敛速度、激活与梯度分布、吞吐及下游质量，并确保推理内核、量化和权重转换一致。

**相关知识点：** LayerNorm、RMSNorm、均值中心化、尺度不变性、Kernel Fusion、Mixed Precision。
<a id="trans-050"></a>
### 3. Transformer 中 FFN/MLP 层承担什么作用？SwiGLU 为什么常见？（高级）

**Attention负责跨Token混合信息，FFN在每个Token位置独立进行通道变换和非线性特征组合；两者缺一不可。**

1. 标准FFN先从`d_model`扩展到`d_ff`，激活后再投影回来，参数和FLOPs通常占模型很大比例。它不直接交换Token，但会将Attention聚合的信息变换为新的特征。
2. GLU类结构用一条分支作为门控；SwiGLU通常计算`SiLU(xW_gate) ⊙ (xW_up)`再下投影，表达力与训练表现常优于相同设置的ReLU/GELU FFN。公平比较需调整隐藏维度，使参数量和计算量接近。
3. 优化可使用算子融合、张量并行、激活检查点、结构化剪枝或MoE，但应验证困惑度、下游质量、吞吐和显存，不能只比较单层理论FLOPs。

**相关知识点：** Feed-Forward Network、MLP、GELU、GLU、SwiGLU、门控、通道混合、算子融合。
<a id="trans-060"></a>
### 4. Transformer 训练出现 Loss Spike、梯度爆炸或 NaN，如何系统定位？（高级）

**定位训练不稳定应固定可复现检查点，先区分数据、数值精度、优化器和分布式通信问题，再通过最小变量回放找到首个异常算子或批次。**

1. 保存异常前模型、优化器、随机数和数据游标，单卡高精度回放同一Batch；检查非法Token、超长样本、Mask全空、标签越界和重复异常数据。若单卡稳定而多卡失败，重点检查通信、分片状态和不同Rank输入。
2. 监控各层激活、梯度、参数范数、学习率、Loss Scale和非有限值首次出现位置。常见止损包括降低学习率、增加Warmup、梯度裁剪、BF16替代FP16、提高归一化或Softmax累积精度，但止损不能替代根因分析。
3. 分别关闭新内核、量化、Checkpoint和并行优化做二分消融；修复后从异常前检查点跨越原批次回归，并验证吞吐与最终质量没有被保守配置显著损害。

**相关知识点：** Loss Spike、NaN、Gradient Clipping、Loss Scaling、BF16、Deterministic Replay、Anomaly Detection、二分消融。
