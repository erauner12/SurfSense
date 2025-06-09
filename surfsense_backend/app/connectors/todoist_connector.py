"""
Todoist Connector Module

A module for retrieving tasks from Todoist.
"""
from todoist_api_python.api import TodoistAPI
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

class TodoistConnector:
    """Class for retrieving tasks from Todoist."""

    def __init__(self, token: str = None):
        """
        Initialize the TodoistConnector class.
        
        Args:
            token: Todoist API token (optional, can be set later with set_token)
        """
        self.token = token
        self.api = TodoistAPI(token) if token else None

    def set_token(self, token: str) -> None:
        """
        Set the Todoist API token.
        
        Args:
            token: Todoist API token
        """
        self.token = token
        self.api = TodoistAPI(token)

    def _headers(self) -> Dict[str, str]:
        """
        Get headers for Todoist API requests.
        
        Returns:
            Dictionary of headers
            
        Raises:
            ValueError: If no Todoist token has been set
        """
        if not self.token:
            raise ValueError("Todoist token not initialized. Call set_token() first.")
            
        return {
            'Authorization': f'Bearer {self.token}'
        }

    def get_tasks_by_date_range(
        self,
        start_date: str,
        end_date: str,
        include_completed: bool = False
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Fetch tasks created within a date range.
        Todoist API does not support filtering by updated_at, so we only filter by created_at.
        Completed tasks are not fetched as the REST API does not support fetching them by date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (inclusive)
            include_completed: Whether to include completed tasks. (Not currently supported)
            
        Returns:
            Tuple containing (tasks list, error message or None)
        """
        if not self.api:
            return [], "Todoist token not initialized. Call set_token() first."

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            end_dt_inclusive = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        except ValueError as e:
            return [], f"Invalid date format: {str(e)}. Please use YYYY-MM-DD."

        try:
            all_tasks = self.api.get_tasks()
            
            filtered_tasks = []
            for task in all_tasks:
                created_at_dt = datetime.fromisoformat(task.created_at.replace('Z', '+00:00'))
                if start_dt <= created_at_dt <= end_dt_inclusive:
                    filtered_tasks.append(task.to_dict())
            
            if not filtered_tasks:
                return [], "No tasks found in the specified date range."
            
            return filtered_tasks, None
        except Exception as e:
            return [], f"Error fetching tasks: {str(e)}"

    def format_task(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a task for easier consumption.
        
        Args:
            raw: The task object from Todoist API
            
        Returns:
            Formatted task dictionary
        """
        due = raw.get("due")
        return {
            "id": raw.get("id"),
            "project_id": raw.get("project_id"),
            "content": raw.get("content"),
            "description": raw.get("description"),
            "comment_count": raw.get("comment_count"),
            "is_completed": raw.get("is_completed"),
            "labels": raw.get("labels"),
            "priority": raw.get("priority"),
            "created_at": raw.get("created_at"),
            "due_date": due.get("date") if due else None,
            "url": raw.get("url"),
        }

    def format_task_to_markdown(self, task: Dict[str, Any]) -> str:
        """
        Convert a task to markdown format.
        
        Args:
            task: The task object (formatted)
            
        Returns:
            Markdown string representation of the task
        """
        markdown = f"# {task.get('content', 'No Title')}\n\n"
        
        if task.get('is_completed'):
            markdown += f"**Status:** Completed\n"
        else:
            markdown += f"**Status:** Open\n"
        
        if task.get('due_date'):
            markdown += f"**Due:** {task['due_date']}\n"
        
        if task.get('priority'):
            priorities = {1: "P4 (Low)", 2: "P3 (Medium)", 3: "P2 (High)", 4: "P1 (Urgent)"}
            markdown += f"**Priority:** {priorities.get(task['priority'], 'Unknown')}\n"
        
        if task.get('labels'):
            markdown += f"**Labels:** {', '.join(task['labels'])}\n"
            
        if task.get('created_at'):
            created_date = self.format_date(task['created_at'])
            markdown += f"**Created:** {created_date}\n\n"
        
        if task.get('description'):
            markdown += f"## Description\n\n{task['description']}\n\n"
        
        if task.get('comment_count', 0) > 0:
            markdown += f"**Comments:** {task['comment_count']}\n\n"
            
        return markdown

    @staticmethod
    def format_date(iso_date: str) -> str:
        """
        Format an ISO date string to a more readable format.
        
        Args:
            iso_date: ISO format date string
            
        Returns:
            Formatted date string
        """
        if not iso_date or not isinstance(iso_date, str):
            return "Unknown date"
            
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return iso_date