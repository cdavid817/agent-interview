[CmdletBinding()]
param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$Reclassify,
    [ValidateRange(1, [int]::MaxValue)]
    [int]$MinimumOccurrences = 5
)

$ErrorActionPreference = "Stop"

$sectionNames = @(
    "一、架构设计类",
    "二、任务规划与编排类",
    "三、模型调用与路由类",
    "四、Prompt 工程类",
    "五、RAG 与知识库类",
    "六、向量数据库类",
    "七、记忆系统类",
    "八、工具调用类",
    "九、安全与治理类",
    "十、可观测性类",
    "十一、评测体系类",
    "十二、工程稳定性类"
)

$glossaryPath = Join-Path $Root "docs/reference/术语索引.md"
$docsPath = Join-Path $Root "docs"
$coreTermsPath = Join-Path $PSScriptRoot "glossary_core_terms.txt"
$itemsBySection = @()
$seen = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
$termFrequency = [System.Collections.Generic.Dictionary[string, int]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
$coreTerms = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
$coreTermOrder = [System.Collections.Generic.List[string]]::new()
if (-not (Test-Path -LiteralPath $coreTermsPath)) {
    throw "Core-term list not found: $coreTermsPath"
}
foreach ($line in Get-Content -LiteralPath $coreTermsPath -Encoding utf8) {
    $term = $line.Trim()
    if ($term -and -not $term.StartsWith("#") -and $coreTerms.Add($term)) {
        $coreTermOrder.Add($term)
    }
}
for ($index = 0; $index -lt $sectionNames.Count; $index++) {
    $itemsBySection += ,([System.Collections.Generic.List[string]]::new())
}

function Normalize-Term {
    param([string]$Term)

    $value = $Term -replace "\*", ""
    $value = $value -replace "^[\s``]+|[\s``。\.]+$", ""
    $value = $value -replace "\s+", " "
    return $value.Trim()
}

function Split-KnowledgeTerms {
    param([string]$Text)

    $result = [System.Collections.Generic.List[string]]::new()
    $buffer = [System.Text.StringBuilder]::new()
    $depth = 0

    foreach ($character in $Text.ToCharArray()) {
        if ($character -in @("(", "（", "[", "【")) {
            $depth++
            [void]$buffer.Append($character)
            continue
        }
        if ($character -in @(")", "）", "]", "】")) {
            if ($depth -gt 0) {
                $depth--
            }
            [void]$buffer.Append($character)
            continue
        }
        if (($character -in @("、", "，", ",", "；", ";")) -and $depth -eq 0) {
            $term = Normalize-Term $buffer.ToString()
            if ($term) {
                $result.Add($term)
            }
            [void]$buffer.Clear()
            continue
        }
        [void]$buffer.Append($character)
    }

    $lastTerm = Normalize-Term $buffer.ToString()
    if ($lastTerm) {
        $result.Add($lastTerm)
    }
    return $result
}

function Get-TermCategory {
    param(
        [string]$Term,
        [int]$DefaultCategory = 11
    )

    $patterns = @(
        # 九、安全与治理类
        @{
            Index = 8
            Pattern = "安全|治理|权限|鉴权|认证|授权|越权|最小权限|RBAC|ABAC|IAM|ACL|OAuth|OIDC|JWT|SSO|PKCE|KMS|Vault|Secret|Credential|凭据|密钥|令牌|隐私|合规|审计|脱敏|DLP|PII|注入|Injection|攻击|威胁|红队|Red Team|投毒|毒化|越狱|Jailbreak|Guardrail|Policy|Allowlist|Denylist|deny-|白名单|黑名单|沙箱|Sandbox|隔离|零信任|Zero Trust|供应链|SBOM|水印|Watermark|版权|内容安全|风控|Risk|不可信|不可抵赖|防重放|侧信道|访问控制|RLS|Quarantine|seccomp|cgroup|非Root|非特权|法律冻结|法务保全|爆炸半径|身份核验|深度伪造|数据泄漏|数据驻留|数据最小化"
        },
        # 十、可观测性类
        @{
            Index = 9
            Pattern = "可观测|观测|监控|日志|Logging|Log\b|Metric|Trace|Tracing|Span|OpenTelemetry|OTel|Telemetry|埋点|告警|报警|Dashboard|SLO|SLA|Error Budget|错误预算|链路追踪|链路关联|采样|Sampling|Exemplar|Collector|Prometheus|Grafana|Langfuse|Phoenix|健康检查|Health Check|诊断|Doctor|Correlation ID|TraceID|SpanID|端到端追踪|调用栈|调用指纹|错误指纹|水位|P50|P95|P99|QPS|吞吐|延迟|耗时|^499$"
        },
        # 七、记忆系统类
        @{
            Index = 6
            Pattern = "Memory|记忆|遗忘|Forgetting|用户画像|User Model|情景记忆|Episodic|Working Memory|工作记忆|长期事实|会话历史|Conversation History|Transcript|Dreaming|梦境|Memory Flush|Memory Score"
        },
        # 六、向量数据库类
        @{
            Index = 5
            Pattern = "向量数据库|Vector Database|Vector DB|HNSW|IVF|IVFPQ|DiskANN|FAISS|Milvus|Qdrant|Weaviate|Pinecone|Chroma|pgvector|Product Quantization|(?<![A-Za-z])PQ(?![A-Za-z])|OPQ|Scalar Quantization|标量量化|向量量化|nlist|nprobe|efSearch|efConstruction|近似最近邻|(?<![A-Za-z])ANN(?![A-Za-z])|IndexFlat|Segment|向量维度|码本|(?<![A-Za-z])IOPS(?![A-Za-z])|非对称距离|残差量化"
        },
        # 五、RAG 与知识库类
        @{
            Index = 4
            Pattern = "\bRAG\b|Retriev|检索|召回|知识库|Knowledge Base|Embedding|向量化|BM25|TF-IDF|倒排索引|Rerank|RRF|Cross-Encoder|Cross Encoder|Bi-Encoder|Bi Encoder|Hybrid Search|Chunk|切片|分块|文档|版面|表格|Document Parsing|Document AI|Document Layout|Query Rewrite|Query Expansion|Query Router|Query Classifier|Query Routing|查询|Grounding|Groundedness|Citation|引用|Faithfulness|Hallucination|事实核验|Fact Checking|索引|Index Freshness|Repository Index|Overlay Index|墓碑|Tombstone|HyDE|SPLADE|MMR|Learning.to.Rank|IDF|语义|关键词|全文搜索|Provenance|证据|Source Authority|Knowledge Graph|知识图谱|GraphRAG|Text-to-SQL|Text-to-Cypher|词汇鸿沟|词频|粗排|精排|Top-K|TopK|Top-N|TopN|元数据|实体|分数融合|分数校准|搜索宽度|Upsert"
        },
        # 十一、评测体系类
        @{
            Index = 10
            Pattern = "评测|评估|评价|Evaluation|Benchmark|Rubric|Judge|Golden Dataset|Golden Set|黄金集|测试|Test|验证|验收|Accuracy|Relevance|准确率|正确率|完成率|成功率|命中率|覆盖率|Coverage|召回率|保留率|保真度|忠实度|完整率|完整性|一致性|相关性|误报率|漏报率|错误率|失败率|通过率|触发率|采用率|接受率|Rate|Recall@|Precision@|\bMRR\b|\bNDCG\b|\bnDCG\b|\bMAP\b|pass@|F1|AUC|BLEU|ROUGE|METEOR|BERTScore|ECE|CER/WER|IoU|置信|校准|Bootstrap|显著性|统计功效|效应量|消融|A/B|Shadow|Canary|实验|对照|Mutation|变异|质量|验收标准|Acceptance|KPI|ROI|CSAT|NPS|满意度|人工盲审|Failure Taxonomy|Error Taxonomy|错误分类|错误聚类|归因|Root Cause|指标|Metric Tree|基线|Baseline|样本|标签|标注|得分|Score|收益|价值评估|缺陷|贝叶斯优化|Ground Truth|Holdout|Drift|Flaky|Pareto|Goodhart|CUPED|MDE|SRM|Claim-level|Strict Success|Lifecycle Evaluation|EvalOps|Differential Testing"
        },
        # 八、工具调用类
        @{
            Index = 7
            Pattern = "\bTool\b|Tools|ToolUse|ToolResult|工具|Function Calling|Tool Calling|MCP|Skill|Plugin|Hook|Browser|浏览器|Shell|Bash|Exec|Code Mode|Tool Search|JSON Schema|Schema|Resources|Prompts|stdio|ACP|Agent SDK|Computer Use|Node Pairing|设备 Node|Channel|Cron|Heartbeat|Webhook|API|SDK|CLI|IDE|LSP|AST|Call Graph|调用图|Git|Worktree|Glob/Grep|CODEOWNERS|CLAUDE.md|DOM|代码|单测|Mock|CI/CD|DevContainer|参数|命令|调用|函数|插件|Toolbox|制品|Symbol|Parser|CFG|CHA|Call Hierarchy|Find References"
        },
        # 四、Prompt 工程类
        @{
            Index = 3
            Pattern = "Prompt|提示词|指令|Instruction|System Message|Developer Message|User Message|Few-shot|Zero-shot|上下文|Context|Context Window|Context Engineering|Context Construction|Context Assembly|Compaction|摘要|压缩|裁剪|按需读取|按需回读|按需加载|按需展开|动态组装|窗口占用|Lost in the Middle|输出格式|Structured Output|结构化输出|思维链|Chain of Thought|CoT|Scratchpad|Token Budget"
        },
        # 三、模型调用与路由类
        @{
            Index = 2
            Pattern = "模型|Model|LLM|Transformer|Attention|Self-Attention|Multi-Head|QKV|Token|Tokenizer|KV Cache|MoE|FFN|RoPE|ALiBi|LoRA|QLoRA|SFT|RLHF|DPO|PPO|GRPO|微调|Fine-tun|蒸馏|Distillation|量化|Quantization|推理|Inference|Decoding|Sampling|Temperature|Top-p|Top-k|Beam Search|GPU|CUDA|FLOP|Prefill|Decode|Batch|Provider|路由模型|模型路由|Fallback|Speculative|投机解码|Causal LM|Masked LM|Encoder|Decoder|Softmax|LayerNorm|RMSNorm|激活|GELU|SwiGLU|梯度|Loss|Perplexity|训练|对比学习|对比损失|InfoNCE|反向传播|残差|低秩|多模态|Multimodal|Modality|词表|分词|表示空间|表征|归一化|位置编码|NLI|NPU|Q-Former|VLM|TTS|VAD|ASR|OCR|Image-Text|Object Detection|Projection|Projector|Native Multimodality"
        },
        # 二、任务规划与编排类
        @{
            Index = 1
            Pattern = "任务|Task|规划|Plan|Planner|Workflow|工作流|DAG|编排|Orchestrat|调度|Schedule|状态机|State Machine|Checkpoint|检查点|断点续跑|Replan|重规划|Reflection|反思|Self-Refine|Self-Critique|Critic|ReAct|Tree of Thoughts|ToT|Graph of Thoughts|GoT|分解|依赖|关键路径|Critical Path|终止|停止条件|Goal|Todo|进度|委派|Delegation|Supervisor|合同网|黑板模式|协作|冲突|仲裁|裁决|协商|表决|澄清|多 Agent|Multi-Agent|Subagent|Agent Team|Agent View|步骤|阶段执行|递归深度|反馈闭环|反馈回路|MCTS|Tarjan|强连通分量|环检测|循环检测"
        },
        # 一、架构设计类
        @{
            Index = 0
            Pattern = "Agent|架构|Architecture|Runtime|Gateway|Harness|控制面|Control Plane|数据面|Data Plane|模块|分层|平台|Platform Engineering|中台|微服务|Service Mesh|Client|Server|Host|Registry|Adapter|SPI|Protocol|协议|A2A|ACP|事件驱动|Event-Driven|黑板|发布订阅|Pub/Sub|中心化|去中心化|联邦|Swarm|工作区|Workspace|Session|会话|Artifact|Personal Assistant|OpenClaw|Claude Code|OpenCode|Codex|Cursor|LangGraph|AutoGen|CrewAI|Semantic Kernel|多租户|Tenant|Namespace|Topology|Capability|单一职责|插件化|薄内核|高可用|弹性扩|部署拓扑|端云协同|生命周期|代理式探索|AIOps"
        }
    )

    foreach ($entry in $patterns) {
        if ($Term -match $entry.Pattern) {
            return [int]$entry.Index
        }
    }
    return $DefaultCategory
}

# Preserve the existing manual category for every term already present.
$preservedTerms = [System.Collections.Generic.List[string]]::new()
if (Test-Path -LiteralPath $glossaryPath) {
    $currentSection = -1
    foreach ($line in Get-Content -LiteralPath $glossaryPath -Encoding utf8) {
        if ($line -match "^##\s+(.+?)\s*$") {
            $currentSection = [Array]::IndexOf($sectionNames, $Matches[1])
            continue
        }
        if ($currentSection -ge 0 -and $line -match "^\d+\.\s+(.+?)\s*$") {
            $term = Normalize-Term $Matches[1]
            if ($Reclassify) {
                if ($term) {
                    $preservedTerms.Add($term)
                }
            }
            elseif ($term -and $seen.Add($term)) {
                $itemsBySection[$currentSection].Add($term)
            }
        }
    }
}

$relatedLineCount = 0
$documentCount = 0
$sourceDefaults = @{
    "agent-architecture" = 0
    "planning-execution" = 1
    "context-knowledge" = 6
    "tools-skills-mcp" = 7
    "multi-agent" = 1
    "model-capability-cost" = 2
    "safety-governance-observability" = 8
    "engineering-platform" = 11
    "rag" = 4
    "transformer" = 2
    "openclaw" = 0
    "claude-code" = 7
}
foreach ($document in Get-ChildItem -LiteralPath $docsPath -Recurse -Filter "*.md" | Sort-Object FullName) {
    if ($document.FullName -notmatch "[\\/]docs[\\/](01-foundations|02-capabilities|03-production|04-products)[\\/]") {
        continue
    }
    $documentText = Get-Content -LiteralPath $document.FullName -Raw -Encoding utf8
    if ($documentText -notmatch "(?m)^###\s+\d+\.\s+") {
        continue
    }
    $documentCount++
    foreach ($line in $documentText -split "`r?`n") {
        if ($line -notmatch "相关知识点[：:]\s*\**\s*(.+)$") {
            continue
        }
        $relatedLineCount++
        foreach ($term in Split-KnowledgeTerms $Matches[1]) {
            if ($termFrequency.ContainsKey($term)) {
                $termFrequency[$term]++
            }
            else {
                $termFrequency[$term] = 1
            }
            if ($seen.Add($term)) {
                $sourceKey = $document.Directory.Name
                $defaultCategory = if ($sourceDefaults.ContainsKey($sourceKey)) {
                    [int]$sourceDefaults[$sourceKey]
                }
                else {
                    11
                }
                $category = Get-TermCategory $term $defaultCategory
                $itemsBySection[$category].Add($term)
            }
        }
    }
}

foreach ($term in $preservedTerms) {
    if ($seen.Add($term)) {
        $category = Get-TermCategory $term 11
        $itemsBySection[$category].Add($term)
    }
}

foreach ($term in $coreTermOrder) {
    if ($seen.Add($term)) {
        $category = Get-TermCategory $term 11
        $itemsBySection[$category].Add($term)
    }
}

for ($sectionIndex = 0; $sectionIndex -lt $sectionNames.Count; $sectionIndex++) {
    $filteredItems = [System.Collections.Generic.List[string]]::new()
    foreach ($term in $itemsBySection[$sectionIndex]) {
        $frequency = if ($termFrequency.ContainsKey($term)) {
            $termFrequency[$term]
        }
        else {
            0
        }
        if ($frequency -ge $MinimumOccurrences -or $coreTerms.Contains($term)) {
            $filteredItems.Add($term)
        }
    }
    $itemsBySection[$sectionIndex] = $filteredItems
}

$totalCount = 0
foreach ($sectionItems in $itemsBySection) {
    $totalCount += $sectionItems.Count
}

$output = [System.Collections.Generic.List[string]]::new()
$output.Add("# Agent 术语索引")
$output.Add("")
$output.Add("> 本文件保留在面试题「相关知识点」中至少出现 **$MinimumOccurrences** 次的术语，并补充 Agent 领域核心术语；共 **$totalCount** 个去重术语，按 12 个主题分类。本页是分类索引，不把术语列表误称为完整定义。")
$output.Add(">")
$output.Add("> 当前覆盖 ``docs/`` 下 **$documentCount** 个题目文件、**$relatedLineCount** 处「相关知识点」。筛选规则由 ``scripts/glossary_core_terms.txt`` 与最小出现次数共同维护。")
$output.Add("")

for ($sectionIndex = 0; $sectionIndex -lt $sectionNames.Count; $sectionIndex++) {
    $output.Add("## $($sectionNames[$sectionIndex])")
    $output.Add("")

    $number = 1
    $sortedItems = $itemsBySection[$sectionIndex] |
        Sort-Object -Unique -Culture "zh-CN"
    foreach ($term in $sortedItems) {
        $output.Add("$number. $term")
        $number++
    }
    $output.Add("")
}

if ($output.Count -gt 0 -and $output[$output.Count - 1] -eq "") {
    $output.RemoveAt($output.Count - 1)
}

Set-Content -LiteralPath $glossaryPath -Value $output -Encoding utf8

Write-Output "Glossary updated: $glossaryPath"
Write-Output "Documents: $documentCount"
Write-Output "Related-knowledge lines: $relatedLineCount"
Write-Output "Minimum occurrences: $MinimumOccurrences"
Write-Output "Core terms: $($coreTerms.Count)"
Write-Output "Unique terms: $totalCount"
for ($index = 0; $index -lt $sectionNames.Count; $index++) {
    Write-Output ("{0}`t{1}" -f $sectionNames[$index], $itemsBySection[$index].Count)
}
