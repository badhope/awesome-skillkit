# ADR 001 — Pydantic v2 + ClassVar Depends

- **状态**：已采纳
- **日期**：2026-06-01

## 背景

FastAPI 依赖函数需要能被框架调用。当我们把依赖以类属性的形式暴露时，FastAPI
可能会直接尝试调用**该属性本身**（而非其底层的函数），从而报错
`TypeError: 'X' object is not callable`。

## 决策

1. **所有配置、Schema、请求/响应模型统一使用 Pydantic v2**。
2. 当某个依赖函数必须作为类属性暴露时（例如 `PaginationParams`
   数据类上的 `get_pagination`），把它声明为
   `ClassVar[Callable[..., T]]`，从而让 Pydantic 不会把它当作字段处理。
3. 使用现代的 `Depends(get_pagination)` 模式替代
   `Depends(PaginationParams)`。

```python
class PaginationParams:
    page: int = 1
    size: int = 20

    # 用 ClassVar，避免 pydantic-settings / pydantic v2 把它当作字段
    get_pagination: ClassVar[Callable[..., "PaginationParams"]] = None
```

## 后果

- Pydantic v2 的严格模式会早期拒绝非法输入。
- `ClassVar` 声明避免了"不可调用"这个隐式陷阱。
- 分页依赖保持为一个普通函数 —— 测试与 mock 都更清晰。
