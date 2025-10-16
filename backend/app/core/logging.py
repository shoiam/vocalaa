from loguru import logger
import sys

def setup_logging():
    
    logger.remove()

    # Console logging (stderr)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    # File logging - General application logs
    logger.add(
        "logs/vocalaa.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="10 MB",  # Create new file when current reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip"  # Compress old log files
    )

    # File logging - Error logs only
    logger.add(
        "logs/vocalaa_errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="zip"
    )

    # File logging - MCP specific logs
    logger.add(
        "logs/mcp_requests.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="5 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: "MCP" in record["message"] or record["name"] == "mcp"
    )

    # File logging - Observability & Metrics logs
    logger.add(
        "logs/metrics.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        filter=lambda record: "MCP_TOOL_CALL" in record["message"] or "MCP_PERFORMANCE" in record["message"]
    )

    # File logging - Performance metrics only (JSON format for easier parsing)
    logger.add(
        "logs/performance.jsonl",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra}",
        level="INFO",
        rotation="5 MB",
        retention="14 days",
        compression="zip",
        filter=lambda record: "MCP_PERFORMANCE" in record["message"],
        serialize=True  # Output as JSON lines
    )

    # File logging - Tool usage analytics (JSON format)
    logger.add(
        "logs/tool_usage.jsonl",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra}",
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        filter=lambda record: "MCP_TOOL_CALL" in record["message"],
        serialize=True  # Output as JSON lines for analytics
    )
