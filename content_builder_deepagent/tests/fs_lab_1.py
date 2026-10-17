"""练习1：写 → 读回 → 补丁改 → 失败不改 → 整篇覆盖（无 API 调用）"""
import hashlib
import os
from pathlib import Path

os.environ.setdefault("AGENTSEEK_MODEL_PROVIDER", "openai")
os.environ.setdefault("AGENTSEEK_MODEL", "course-scripted")
os.environ.setdefault("OPENAI_API_KEY", "unused-scripted-key")
os.environ.setdefault("CONTENT_MODE", "text")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from scripted_model import ScriptedModel, call

from content_builder_deepagent import agent

root = Path(agent.EXAMPLE_DIR)
outline = root / "notes" / "outline.md"
report = root / "blogs" / "fslab" / "post.md"
REPORT_V1 = "# FS lab\n\n## Context\n初稿 v1\n\n## Sources\n- sources/files.md\n"

model = ScriptedModel(replies=[
    call("write_file", {"file_path": "/notes/outline.md",
                        "content": "一、背景\n二、发现\n三、步骤\n"}, "w1"),
    call("read_file", {"file_path": "/notes/outline.md"}, "r1"),
    call("edit_file", {"file_path": "/notes/outline.md",
                       "old_string": "二、发现", "new_string": "二、发现（已核对）"}, "e1"),
    call("read_file", {"file_path": "/notes/outline.md"}, "r2"),
    call("edit_file", {"file_path": "/notes/outline.md",
                       "old_string": "这行不存在", "new_string": "x"}, "e2"),
    call("read_file", {"file_path": "/notes/outline.md"}, "r3"),
    call("save_report", {"slug": "fslab", "content": REPORT_V1}, "s1"),
    call("read_report", {"slug": "fslab"}, "r4"),
    call("save_report", {"slug": "fslab", "content": REPORT_V1.replace("v1", "v2")}, "s2"),
    call("read_report", {"slug": "fslab"}, "r5"),
    AIMessage(content="done"),
])


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12] if path.exists() else "-"


graph = agent.build_graph(model, checkpointer=InMemorySaver())
seen, last = {}, ("-", "-")
for chunk in graph.stream(
    {"messages": [{"role": "user", "content": "练习1"}]},
    {"configurable": {"thread_id": "fslab-1"}},
    stream_mode="updates",
):
    for update in chunk.values():
        if not isinstance(update, dict):
            continue
        for m in update.get("messages") or []:
            if getattr(m, "type", None) == "tool":
                seen[m.tool_call_id] = str(m.content)
                print(f"\n[{m.name}] {str(m.content).splitlines()[0]}")
    now = (digest(outline), digest(report))
    if now != last:
        print(f"  disk  outline={now[0]}  report={now[1]}")
        last = now

checks = {
    "大纲最终内容正确": outline.read_text() == "一、背景\n二、发现（已核对）\n三、步骤\n",
    "报告被整篇覆盖为 v2": "v2" in report.read_text(),
    "首次读回没有修改后的字样": "已核对" not in seen["r1"],
    "失败编辑后读回与成功编辑后一致": seen["r2"] == seen["r3"],
    "失败编辑返回 Error": seen["e2"].startswith("Error"),
}
print()
for name, ok in checks.items():
    print("PASS" if ok else "FAIL", name)