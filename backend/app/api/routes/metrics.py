from fastapi import APIRouter, HTTPException, Depends, Query
from loguru import logger
from typing import Optional
from app.core.observability import get_metrics_collector
from app.core.security import get_current_user


router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/tools")
async def get_tool_statistics(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours (1-168)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get tool usage statistics for the specified time period
    Requires authentication
    """
    try:
        logger.info(f"Tool statistics requested by {current_user['email']} for last {hours} hours")
        collector = get_metrics_collector()
        stats = collector.get_tool_statistics(hours=hours)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving tool statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_user_activity(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours (1-168)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user activity statistics for the specified time period
    Requires authentication
    """
    try:
        logger.info(f"User activity requested by {current_user['email']} for last {hours} hours")
        collector = get_metrics_collector()
        stats = collector.get_user_activity(hours=hours)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def get_performance_summary(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours (1-168)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get performance summary for all operations in the specified time period
    Requires authentication
    """
    try:
        logger.info(f"Performance summary requested by {current_user['email']} for last {hours} hours")
        collector = get_metrics_collector()
        stats = collector.get_performance_summary(hours=hours)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_error_summary(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours (1-168)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get error summary for failed operations in the specified time period
    Requires authentication
    """
    try:
        logger.info(f"Error summary requested by {current_user['email']} for last {hours} hours")
        collector = get_metrics_collector()
        stats = collector.get_error_summary(hours=hours)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving error summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_metrics_dashboard(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours (1-168)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive metrics dashboard with all statistics
    Requires authentication
    """
    try:
        logger.info(f"Metrics dashboard requested by {current_user['email']} for last {hours} hours")
        collector = get_metrics_collector()

        dashboard = {
            "period_hours": hours,
            "tools": collector.get_tool_statistics(hours=hours),
            "users": collector.get_user_activity(hours=hours),
            "performance": collector.get_performance_summary(hours=hours),
            "errors": collector.get_error_summary(hours=hours)
        }

        return dashboard
    except Exception as e:
        logger.error(f"Error retrieving metrics dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_old_metrics(
    hours: int = Query(default=168, ge=24, le=720, description="Clear metrics older than this (24-720 hours)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Clear metrics older than specified hours (admin operation)
    Requires authentication
    Default: 168 hours (7 days)
    """
    try:
        logger.info(f"Clearing metrics older than {hours} hours, requested by {current_user['email']}")
        collector = get_metrics_collector()
        collector.clear_old_metrics(hours=hours)

        return {
            "message": f"Successfully cleared metrics older than {hours} hours",
            "cleared_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error clearing metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
