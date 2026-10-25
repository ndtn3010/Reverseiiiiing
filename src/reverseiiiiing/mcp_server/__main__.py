"""Entry: `reverseiii-mcp` → stdio MCP server."""
from __future__ import annotations

import sys


def main() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("mcp package not installed. pip install 'reverseiiiiing[mcp]'", file=sys.stderr)
        return 1

    from reverseiiiiing.mcp_server.server import register_tools

    app = FastMCP("reverseiii")
    register_tools(app)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
