# 测试指南

## 单元测试原则

- **拆分可测试逻辑**：长逻辑应拆分为职责单一的小函数，避免将复杂业务逻辑集中在一处，确保每个函数独立可测。
- **优先使用 Table Driven Tests**：通过表格驱动的方式组织测试用例，将输入、期望输出统一定义为数据表，循环执行断言，减少重复代码，便于扩展新用例。
- **无副作用（No Side Effects）**：单元测试不应依赖或修改外部状态（文件系统、数据库、网络、全局变量等），保证测试可重复执行且结果稳定。
- **最小功能化**：每个测试只验证一个最小功能点，逐步积累覆盖，确保每层逻辑稳定后再向上组合。
- **AI 不可删除**：任何已有单元测试不得由 AI 自行删除或跳过；若测试因代码变更而失败，必须由人工确认并决定修复或移除，以保证代码稳定性。

```
// 示例结构（以 Go 为例）
tests := []struct {
    name  string
    input SomeType
    want  SomeType
}{
    {"case 1", input1, expected1},
    {"case 2", input2, expected2},
}
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got := FunctionUnderTest(tt.input)
        assert.Equal(t, tt.want, got)
    })
}
```

## 目录与命名规范

测试目录结构和文件命名约定见对应语言的 reference 文件。若语言 reference 中未定义，维持语言/框架的默认惯例，不得自行约定。

## 如何运行测试

```bash
# 运行全部测试
<命令>

# 运行单个文件
<命令>

# 监听模式（开发时）
<命令>
```

> 补充实际命令后删除此提示。
