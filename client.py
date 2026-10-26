import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = "openai/gpt-oss-120b"  # override with GROQ_MODEL in .env
WEATHER_URL = "http://localhost:8000/mcp"  # weather.py must be running

QUESTIONS = [
    ("Math", "what's (3 + 5) x 12?"),
    ("Weather", "what is the weather in California?"),
]


def build_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            # stdio: the client starts this server itself as a subprocess
            "math": {
                "command": sys.executable,
                "args": [str(HERE / "mathserver.py")],
                "transport": "stdio",
            },
            # streamable_http: this server runs separately (python weather.py)
            "weather": {
                "url": WEATHER_URL,
                "transport": "streamable_http",
            },
        }
    )


def _leaf_errors(exc):
    """MCP wraps connection errors in ExceptionGroups; unwrap to the real cause."""
    if isinstance(exc, BaseExceptionGroup):
        for inner in exc.exceptions:
            yield from _leaf_errors(inner)
    else:
        yield exc


async def run(model) -> None:
    client = build_client()
    try:
        tools = await client.get_tools()
    except Exception as e:
        reasons = "; ".join(f"{type(x).__name__}: {x}" for x in _leaf_errors(e))
        raise SystemExit(
            f"Could not connect to the MCP servers ({reasons}).\n"
            "Start the weather server first, in another terminal:  python weather.py"
        )

    print("Tools loaded:", ", ".join(t.name for t in tools))
    agent = create_react_agent(model, tools)

    for label, question in QUESTIONS:
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        print(f"{label} response:", result["messages"][-1].content)


def main() -> None:
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")
    model = ChatGroq(model=os.getenv("GROQ_MODEL", DEFAULT_MODEL))
    asyncio.run(run(model))


if __name__ == "__main__":
    main()
