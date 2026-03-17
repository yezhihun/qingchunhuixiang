# 青春回响 - 事件系统设计方案

## 设计原则
1. **配置驱动** - 事件内容与逻辑分离
2. **渐进式复杂度** - 从简单到复杂，避免过度设计
3. **可维护性** - 内容创作者能轻松修改
4. **性能优先** - 微信小游戏资源受限

## 核心架构

### 1. 事件模板 (EventTemplate)
```json
{
  "id": "teacher_pop_quiz",
  "name": "突击小测验",
  "description": "老师突然宣布进行小测验",
  "category": "classroom",
  "conditions": {
    "time_periods": ["08:00-12:00", "14:00-17:00"],
    "min_students": 5,
    "probability": 0.15,
    "cooldown_hours": 24
  },
  "effects": [
    {
      "type": "attribute_change",
      "target": "all_students",
      "changes": {
        "stress": {"operation": "add", "value": 20, "max": 100},
        "focus": {"operation": "add", "value": 15, "max": 100}
      }
    },
    {
      "type": "relationship_impact",
      "target": "random_pair",
      "impact": "study_competition"
    }
  ],
  "notifications": {
    "title": "突发情况！",
    "message": "老师要进行突击小测验！",
    "duration_seconds": 5
  }
}
```

### 2. 效果插件系统
- **内置效果**: attribute_change, relationship_impact, mood_change
- **自定义效果**: 通过Python插件实现复杂逻辑
- **效果组合**: 支持多个效果按顺序执行

### 3. 条件系统
- 时间条件
- 学生状态条件  
- 关系条件
- 随机概率
- 冷却时间

### 4. 文件组织
```
config/
├── events/
│   ├── classroom/
│   │   ├── academic.json
│   │   └── discipline.json
│   ├── social/
│   │   ├── friendship.json
│   │   └── romance.json
│   └── special/
│       └── holiday_events.json
├── effects/
│   └── effect_definitions.json
└── scenarios/
    └── time_scenarios.json
```

## 实施计划

### Phase 1: 基础配置系统 (1-2天)
- 实现事件模板加载
- 基础效果系统
- 简单条件判断

### Phase 2: 高级功能 (3-5天)  
- 复杂条件系统
- 效果插件机制
- 配置验证工具

### Phase 3: 工具链 (1周)
- 可视化编辑器
- 事件预览器
- 性能优化

## 向后兼容
- 保留现有API接口
- 支持混合模式（新旧事件共存）
- 渐进式迁移路径