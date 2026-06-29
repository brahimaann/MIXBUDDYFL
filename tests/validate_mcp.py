"""Quick validation: start the MCP server and verify it lists 8 tools."""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "server.py")

async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER])
    
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = sorted(t.name for t in tools.tools)
            
            expected_count = 8
            if len(names) == expected_count:
                print(f"✓ MCP server running: {len(names)} tools")
                for name in names:
                    print(f"  - {name}")
                return 0
            else:
                print(f"✗ Expected {expected_count} tools, got {len(names)}: {names}")
                return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
