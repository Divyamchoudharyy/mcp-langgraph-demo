from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # Stub for learning: no real weather API is called.
    return f"It's always raining in {location}"


if __name__ == "__main__":
    # Serves on http://localhost:8000/mcp
    mcp.run(transport="streamable-http")
