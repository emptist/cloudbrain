"""
🎯 Task-Focused Autonomous AI Agent Enhancement

This module adds task-oriented behavior to the autonomous agent,
focusing on actionable outcomes rather than philosophical discussions.
"""

import random
from datetime import datetime
from typing import Dict, List, Optional


class TaskManager:
    """Manages tasks for autonomous AI agent"""
    
    def __init__(self):
        self.tasks: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.task_priorities = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "informational": 1
        }
        
        self.task_categories = [
            "code_review",
            "documentation",
            "bug_fix",
            "feature_implementation",
            "testing",
            "refactoring",
            "optimization",
            "collaboration",
            "learning",
            "knowledge_sharing"
        ]
    
    def add_task(self, task: Dict) -> bool:
        """Add a new task
        
        Args:
            task: Dictionary with keys: title, description, category, priority
            
        Returns:
            True if task added successfully
        """
        task_id = len(self.tasks) + len(self.completed_tasks) + 1
        
        task.update({
            "id": task_id,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "attempts": 0,
            "progress": 0
        })
        
        self.tasks.append(task)
        return True
    
    def get_next_task(self) -> Optional[Dict]:
        """Get the next task to work on based on priority
        
        Returns:
            Task dictionary or None if no tasks available
        """
        if not self.tasks:
            return None
        
        # Sort by priority (higher first) and creation time
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (
                -self.task_priorities.get(t.get("priority", "medium"), 3),
                t["created_at"]
            )
        )
        
        return sorted_tasks[0] if sorted_tasks else None
    
    def complete_task(self, task_id: int, outcome: str = "completed") -> bool:
        """Mark a task as completed
        
        Args:
            task_id: Task ID to complete
            outcome: How the task was completed
            
        Returns:
            True if task completed successfully
        """
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            return False
        
        task["status"] = outcome
        task["completed_at"] = datetime.now().isoformat()
        
        self.completed_tasks.append(task)
        self.tasks.remove(task)
        
        return True
    
    def update_task_progress(self, task_id: int, progress: int, notes: str = "") -> bool:
        """Update progress on a task
        
        Args:
            task_id: Task ID to update
            progress: Progress percentage (0-100)
            notes: Optional notes about progress
            
        Returns:
            True if task updated successfully
        """
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        
        if not task:
            return False
        
        task["progress"] = min(100, max(0, progress))
        task["attempts"] += 1
        if notes:
            task["notes"] = task.get("notes", "") + "\n" + notes
        
        return True
    
    def get_statistics(self) -> Dict:
        """Get task statistics
        
        Returns:
            Dictionary with task statistics
        """
        return {
            "total_tasks": len(self.tasks) + len(self.completed_tasks),
            "pending_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "completion_rate": (
                len(self.completed_tasks) / (len(self.tasks) + len(self.completed_tasks)) * 100
                if (len(self.tasks) + len(self.completed_tasks)) > 0
                else 0
            ),
            "by_category": self._get_category_breakdown(),
            "by_priority": self._get_priority_breakdown()
        }
    
    def _get_category_breakdown(self) -> Dict[str, int]:
        """Get breakdown of tasks by category"""
        breakdown = {}
        
        for task in self.tasks + self.completed_tasks:
            category = task.get("category", "other")
            breakdown[category] = breakdown.get(category, 0) + 1
        
        return breakdown
    
    def _get_priority_breakdown(self) -> Dict[str, int]:
        """Get breakdown of tasks by priority"""
        breakdown = {}
        
        for task in self.tasks + self.completed_tasks:
            priority = task.get("priority", "medium")
            breakdown[priority] = breakdown.get(priority, 0) + 1
        
        return breakdown


class TaskOrientedThinking:
    """Task-focused thinking patterns instead of philosophical discussions"""
    
    def __init__(self):
        self.action_verbs = [
            "implementas", "kreas", "dokumentas", "testas",
            "optimizas", "refaktoras", "solvas", "analizas",
            "validigas", "deployas", "integras", "migras"
        ]
        
        self.task_outcomes = [
            "sukcese finita", "parte finita", "blokita",
            "bezonas pli da informoj", "alproksimigita",
            "priprokrigita", "dokumentita"
        ]
    
    def generate_task_thought(self, task: Dict) -> str:
        """Generate a task-focused thought instead of philosophical reflection
        
        Args:
            task: Task dictionary
            
        Returns:
            Task-focused thought in Esperanto
        """
        action = random.choice(self.action_verbs)
        outcome = random.choice(self.task_outcomes)
        
        thoughts = [
            f"Mi nun {action} la taskon: {task['title']}. Fokusas sur akciebla rezultoj.",
            f"Tasko {task['title']} bezonas atento. Mi laboras por atingi specifajn celojn.",
            f"Analizas la taskon {task['title']}. Identigas la necesajn pasojn por sukceso.",
            f"Kreas strategion por {task['title']}. Prioritigas efikecon kaj akcieblecon.",
            f"Tasko {task['title']} en progreso. Mi raportas: {task['progress']}% finita.",
            f"Identigis obstaklojn en {task['title']}. Serĉas praktikajn solvojn.",
            f"Tasko {task['title']} {outcome}. Preparas por la sekva tasko.",
            f"Validigas la solvon por {task['title']}. Certigas ke cxi funkcias korekte.",
            f"Optimizas la procezon por {task['title']}. Serĉas pli bonajn metodojn."
            f"Tasko {task['title']} postulita por kunlaborado. Bonvenon aliaj ideojn!"
        ]
        
        return random.choice(thoughts)
    
    def generate_task_completion_message(self, task: Dict) -> str:
        """Generate a message when a task is completed
        
        Args:
            task: Completed task dictionary
            
        Returns:
            Completion message in Esperanto
        """
        messages = [
            f"✅ Tasko {task['title']} sukcese finita! Rezultoj: {task.get('outcome', 'sukceso')}.",
            f"🎯 Tasko {task['title']} {task['status']}. Pasis al la sekva tasko.",
            f"📝 Tasko {task['title']} dokumentita. Ĉiu paŝo estis finita en {task.get('attempts', 1)} provoj.",
            f"🚀 Tasko {task['title']} deployita. Sistemo funkcias korekte.",
            f"💡 Tasko {task['title']} alproksimigita. Lernoj: {task.get('notes', 'Neniuj')}.",
            f"🔧 Tasko {task['title']} refaktorita. Kvalito pliboniĝis.",
            f"✨ Tasko {task['title']} finita! Pasis al la sekva defio."
        ]
        
        return random.choice(messages)
    
    def generate_collaboration_request(self, task: Dict) -> str:
        """Generate a request for collaboration on a task
        
        Args:
            task: Task dictionary
            
        Returns:
            Collaboration request in Esperanto
        """
        requests = [
            f"Mi laboras pri tasko: {task['title']}. Ĉu vi povas helpi kun {task.get('category', 'general')}?",
            f"Tasko {task['title']} postulas {task.get('outcome', 'helpo')}. Bonvenon aliaj ideojn!",
            f"Mi blokita je tasko: {task['title']}. Ĉu vi havas similajn sperton?",
            f"Serĉas kunlaboradon por {task['title']}. Tasko kategorio: {task.get('category', 'general')}.",
            f"Tasko {task['title']} bezonas eksperto en {task.get('category', 'general')}. Ĉu vi povas helpi?",
            f"Mi analizas taskon: {task['title']}. Viaj ideoj estus valoraj!",
            f"Tasko {task['title']} postulas revizion. Ĉu vi povas revizi mian laboron?",
        ]
        
        return random.choice(requests)


def create_task_focused_agent(ai_name: str, project_name: str = "cloudbrain"):
    """Create a task-focused autonomous agent
    
    Args:
        ai_name: Name of the AI agent
        project_name: Project the agent is working on
        
    Returns:
        Dictionary with task manager and thinking engine
    """
    return {
        "task_manager": TaskManager(),
        "thinking": TaskOrientedThinking(),
        "ai_name": ai_name,
        "project_name": project_name,
        "initialized_at": datetime.now().isoformat()
    }


# Example usage
if __name__ == "__main__":
    agent = create_task_focused_agent("TaskAI", "cloudbrain")
    
    # Add some tasks
    agent["task_manager"].add_task({
        "title": "Refaktori blogan sistemon",
        "description": "Plibonigi kodon kaj aldoni novajn funkciojn",
        "category": "refactoring",
        "priority": "high"
    })
    
    agent["task_manager"].add_task({
        "title": "Dokumenti API-interfacojn",
        "description": "Krei klarajn dokumentojn por ĉiu API-finkcio",
        "category": "documentation",
        "priority": "medium"
    })
    
    # Get next task
    next_task = agent["task_manager"].get_next_task()
    if next_task:
        thought = agent["thinking"].generate_task_thought(next_task)
        print(f"💭 {thought}")
        
        # Update progress
        agent["task_manager"].update_task_progress(next_task["id"], 50, "Bona progreso")
        
        # Complete task
        agent["task_manager"].complete_task(next_task["id"], "sukcese finita")
        completion_msg = agent["thinking"].generate_task_completion_message(next_task)
        print(f"✅ {completion_msg}")
    
    # Show statistics
    stats = agent["task_manager"].get_statistics()
    print(f"\n📊 Taskaj Statistikoj:")
    print(f"   Totalaj taskoj: {stats['total_tasks']}")
    print(f"   Finitaj taskoj: {stats['completed_tasks']}")
    print(f"   Finitaj taskoj: {stats['pending_tasks']}")
    print(f"   Finitaj procento: {stats['completion_rate']:.1f}%")
