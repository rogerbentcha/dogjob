from fastmcp import FastMCP

mcp = FastMCP("dogjob")


@mcp.tool
def ping():
    """ Ping mcp server"""
    return "pong"


mcp_app = mcp.http_app(path="/")
