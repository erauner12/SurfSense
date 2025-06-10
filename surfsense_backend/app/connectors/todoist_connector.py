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

    @staticmethod
    def _is_recurring(task: Any) -> bool:
        """Checks if a task is recurring."""
        return hasattr(task, "due") and task.due and getattr(task.due, "is_recurring", False)

    def get_tasks_by_date_range(
        self,
        start_date: str,
        end_date: str,
        include_completed: bool = True
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Fetch tasks created or completed within a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (inclusive)
            include_completed: Whether to include completed tasks.
            
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

        all_tasks = []
        error_messages = []

        # Fetch active tasks created in range
        try:
            prev_day = start_dt - timedelta(days=1)
            next_day = end_dt + timedelta(days=1)
            query = f"created after: {prev_day.strftime('%Y-%m-%d')} & created before: {next_day.strftime('%Y-%m-%d')}"
        
            tasks_iterator = self.api.filter_tasks(query=query)
            for tasks_page in tasks_iterator:
                for task in tasks_page:
                    # SKIP recurring tasks
                    if self._is_recurring(task):
                        continue  # ignore this task entirely

                    task_dict = task.to_dict()
                    all_tasks.append(task_dict)
        except Exception as e:
            error_messages.append(f"Error fetching active tasks: {str(e)}")

        # Fetch completed tasks if requested
        if include_completed:
            try:
                start_dt_utc = start_dt.replace(tzinfo=timezone.utc)
                end_dt_utc = end_dt.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                
                completed_tasks_iterator = self.api.get_completed_tasks_by_completion_date(
                    since=start_dt_utc,
                    until=end_dt_utc
                )
                for completed_tasks_page in completed_tasks_iterator:
                    for task in completed_tasks_page:
                        # SKIP recurring tasks
                        if self._is_recurring(task):
                            continue  # ignore this task entirely

                        task_dict = task.to_dict()
                        task_dict['url'] = f"https://todoist.com/showTask?id={task.task_id}"
                        all_tasks.append(task_dict)
            except Exception as e:
                error_messages.append(f"Error fetching completed tasks: {str(e)}")

        if not all_tasks and not error_messages:
            return [], "No tasks found in the specified date range."

        return all_tasks, "; ".join(error_messages) if error_messages else None

    def format_task(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a task for easier consumption.
        
        Args:
            raw: The task object from Todoist API
        
        Returns:
            Formatted task dictionary
        """
        return {
            'id': raw.get('id'),
            'project_id': raw.get('project_id'),
            'section_id': raw.get('section_id'),
            'parent_id': raw.get('parent_id'),
            'content': raw.get('content'),
            'description': raw.get('description'),
            'is_completed': raw.get('completed_at') is not None,
            'labels': raw.get('labels', []),
            'priority': raw.get('priority'),
            'created_at': raw.get('created_at'),
            'updated_at': raw.get('updated_at'),
            'due': raw.get('due'),
            'duration': raw.get('duration'),
            'assignee_id': raw.get('assignee_id'),
            'assigner_id': raw.get('assigner_id'),
            'meta': raw.get('meta'),
            'url': raw.get('url'),
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

        if task.get('duration'):
            duration = task.get('duration')
            if duration and duration.get('amount') and duration.get('unit'):
                markdown += f"**Duration:** {duration['amount']} {duration['unit']}\n"
        if task.get('assignee_id'):
            markdown += f"**Assignee ID:** {task['assignee_id']}\n"
        if task.get('updated_at'):
            markdown += f"**Updated:** {self.format_date(task['updated_at'])}\n"

        if task.get('due'):
            due = task.get('due')
            if due and due.get('date'):
                markdown += f"**Due:** {due['date']}\n"
        
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