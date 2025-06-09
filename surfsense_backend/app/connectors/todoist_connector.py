"""
Todoist Connector Module

A module for retrieving tasks from Todoist.
"""
from todoist_api_python.api import TodoistAPI
from datetime import datetime, timezone, timedelta
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
        Fetch tasks created within a date range using a filter query.
        Todoist API does not support filtering by updated_at.
        This method fetches only active tasks. Completed tasks are not included.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (inclusive)
            include_completed: This parameter is currently ignored.
            
        Returns:
            Tuple containing (tasks list, error message or None)
        """
        if not self.api:
            return [], "Todoist token not initialized. Call set_token() first."

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            return [], f"Invalid date format: {str(e)}. Please use YYYY-MM-DD."

        try:
            # To get tasks from start_date to end_date inclusive, we need to query for
            # tasks created after (start_date - 1 day) AND created before (end_date + 1 day).
            prev_day = start_dt - timedelta(days=1)
            next_day = end_dt + timedelta(days=1)

            query = f"created after: {prev_day.strftime('%Y-%m-%d')} & created before: {next_day.strftime('%Y-%m-%d')}"
        
            all_tasks = []
            tasks_iterator = self.api.filter_tasks(query=query)
            for tasks_page in tasks_iterator:
                for task in tasks_page:
                    task_dict = task.to_dict()
                    task_dict['url'] = task.url  # Manually add url from property
                    all_tasks.append(task_dict)
        
            if not all_tasks:
                return [], "No tasks found in the specified date range."
        
            return all_tasks, None
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
            "is_completed": raw.get("completed_at") is not None,
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