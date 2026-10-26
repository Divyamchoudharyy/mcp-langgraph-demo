from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")


# The docstring of each tool is what the LLM reads to decide when to use it.
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


if __name__ == "__main__":
    # stdio: requests/responses go over stdin/stdout; the client launches this process.
    mcp.run(transport="stdio")
