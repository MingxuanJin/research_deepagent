M1. deepagents 0.7 必须显式传 TodoListMiddleware，write_todos 才会出现在工具列表。
M2. 一个模型响应最多一次 write_todos，并行多次会被 middleware 拒绝。
M3. todos 随 checkpoint 持久化；todo 标 completed 不代表报告已写入。
