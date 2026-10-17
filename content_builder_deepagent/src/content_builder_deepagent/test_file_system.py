# 在 content_builder_deepagent/ 下：uv run python
from deepagents.backends import FilesystemBackend
fs = FilesystemBackend(root_dir=".", virtual_mode=True)

print(fs.write("/notes/lab.md", "v1\n第一行\n"))   # 虚拟路径
print(fs.read("/notes/lab.md"))                   # 返回带行号的文本
print(fs.ls("/notes"))
print(fs.edit("/notes/lab.md", "v1", "v2"))
print(fs.read("/notes/../notes/lab.md"))          # 应被拒：virtual_mode 阻止 ..