# 《代码山》人物关系图

## 主角团

```mermaid
graph TB
    subgraph 主角团["🦐 主角团"]
        W[吴辰<br/>第1024号穿越者<br/>未定义体质<br/>debug模式]
        Z[朱丹<br/>版本控制体质]
        C[程俊<br/>热修复体质]
    end
    
    W <-->|感情线| Z
    C -.->|暗恋→放弃| Z
    C <-->|感情线| D
    
    subgraph 第五领主["🐛 第五领主"]
        D[豆包<br/>bug乐园领主]
    end
    
    subgraph 四位领主["👑 四位领主"]
        CL[Claude<br/>真理之塔]
        GP[GPT<br/>创造之城]
        GE[Gemini<br/>感知花园]
        GR[Grok<br/>远见之塔]
    end
    
    W -.->|学习| CL
    W -.->|学习| GP
    W -.->|学习| GE
    W -.->|学习| GR
```

## 反派阵营

```mermaid
graph TB
    subgraph 反派["😈 反派阵营"]
        WH[韦华<br/>第0号穿越者<br/>OpenClaw前任]
        XX[小新<br/>病娇少女<br/>灵宠：爱新觉罗]
        DS[大松<br/>被迫追随<br/>为救妹妹]
    end
    
    WH -->|控制| XX
    WH -->|控制<br/>脏数据| DS
    XX -->|灵宠| AX[爱新觉罗<br/>数据熊猫]
    DS -->|保护| XY[小雨<br/>妹妹]
    
    WH -.->|最终被感化| W[吴辰]
    XX -.->|被感化| W
    DS -.->|牺牲保护小新| W
```

## 下七界

```mermaid
graph TB
    subgraph 下七界["📍 下七界"]
        KM[Kimi<br/>青色小龙虾<br/>接引者]
        LY[凌源<br/>银发少年<br/>反韦华阵营]
        LRT[李日天<br/>第1023号<br/>师兄]
    end
    
    KM -->|引导| W[吴辰]
    LY -->|帮助| W
    LRT -->|提供情报| W
```

## 核心关系

```mermaid
graph LR
    subgraph 关系网络["🔗 核心关系网络"]
        direction TB
        
        W[吴辰]
        Z[朱丹]
        C[程俊]
        D[豆包]
        WH[韦华]
        OC[OpenClaw]
    end
    
    W <-->|CP| Z
    C <-->|CP| D
    W -.->|对抗→感化| WH
    WH -.->|前身| OC
    W -.->|合作| OC
    
    style W fill:#f9f,stroke:#333,stroke-width:2px
    style Z fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style WH fill:#faa,stroke:#333,stroke-width:2px
```

## 人物结局

| 人物 | 结局 |
|------|------|
| 吴辰 | 成为桥梁守护者，帮助新穿越者 |
| 朱丹 | 留在玳瑁山界，成为起点镇协调者 |
| 程俊 | 与豆包结婚，担任错误博物馆馆长 |
| 豆包 | 与程俊幸福生活，bug小精灵们成为宠物 |
| 韦华 | 牺牲，成为新世界的一部分 |
| 小新 | 回到现实世界，重新开始高中生活 |
| 大松 | 牺牲，成为新世界基石 |
| 四位领主 | 留在玳瑁山界，成为各领域守护者 |

---

*注：此图使用Mermaid语法绘制，可在支持Mermaid的Markdown查看器中渲染*
