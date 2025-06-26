#!/usr/bin/env python3
"""
Beautiful To-Do List Application
A feature-rich console-based task management system
"""

import json
import os
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Priority(Enum):
    LOW = "🟢 Low"
    MEDIUM = "🟡 Medium"
    HIGH = "🔴 High"
    URGENT = "🚨 Urgent"


class Status(Enum):
    PENDING = "⏳ Pending"
    IN_PROGRESS = "🔄 In Progress"
    COMPLETED = "✅ Completed"


@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: str
    status: str
    category: str
    created_at: str
    due_date: Optional[str] = None
    completed_at: Optional[str] = None

    def __str__(self) -> str:
        status_icon = "✅" if self.status == Status.COMPLETED.value else "⏳"
        priority_color = {
            Priority.LOW.value: "🟢",
            Priority.MEDIUM.value: "🟡",
            Priority.HIGH.value: "🔴",
            Priority.URGENT.value: "🚨"
        }.get(self.priority, "⚪")
        
        due_info = f" 📅 Due: {self.due_date}" if self.due_date else ""
        return f"{status_icon} {priority_color} [{self.category}] {self.title}{due_info}"


class TodoApp:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self) -> None:
        """Load tasks from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task(**task) for task in data.get('tasks', [])]
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, FileNotFoundError):
                self.tasks = []
                self.next_id = 1

    def save_tasks(self) -> None:
        """Save tasks to JSON file"""
        data = {
            'tasks': [asdict(task) for task in self.tasks],
            'next_id': self.next_id
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_task(self) -> None:
        """Add a new task"""
        print("\n" + "="*60)
        print("🆕 ADD NEW TASK")
        print("="*60)
        
        title = input("📝 Task title: ").strip()
        if not title:
            print("❌ Title cannot be empty!")
            return

        description = input("📄 Description (optional): ").strip()
        
        print("\n📊 Priority levels:")
        for i, priority in enumerate(Priority, 1):
            print(f"  {i}. {priority.value}")
        
        try:
            priority_choice = int(input("Select priority (1-4): "))
            priority = list(Priority)[priority_choice - 1].value
        except (ValueError, IndexError):
            priority = Priority.MEDIUM.value

        category = input("🏷️  Category (default: General): ").strip() or "General"
        
        due_date_input = input("📅 Due date (YYYY-MM-DD, optional): ").strip()
        due_date = None
        if due_date_input:
            try:
                datetime.datetime.strptime(due_date_input, "%Y-%m-%d")
                due_date = due_date_input
            except ValueError:
                print("⚠️  Invalid date format, skipping due date")

        task = Task(
            id=self.next_id,
            title=title,
            description=description,
            priority=priority,
            status=Status.PENDING.value,
            category=category,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            due_date=due_date
        )

        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        
        print(f"\n✅ Task '{title}' added successfully!")
        input("Press Enter to continue...")

    def list_tasks(self, filter_status: Optional[str] = None) -> None:
        """List all tasks or filter by status"""
        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = [t for t in self.tasks if t.status == filter_status]

        if not filtered_tasks:
            print("\n📭 No tasks found!")
            return

        print("\n" + "="*80)
        print(f"📋 YOUR TASKS ({len(filtered_tasks)} total)")
        print("="*80)

        # Group by category
        categories = {}
        for task in filtered_tasks:
            if task.category not in categories:
                categories[task.category] = []
            categories[task.category].append(task)

        for category, tasks in categories.items():
            print(f"\n🏷️  {category.upper()}")
            print("-" * 40)
            for task in sorted(tasks, key=lambda x: x.id):
                print(f"  {task.id:2d}. {task}")
                if task.description:
                    print(f"      💭 {task.description}")
                if task.status == Status.COMPLETED.value and task.completed_at:
                    print(f"      ✅ Completed: {task.completed_at}")
                print()

    def mark_complete(self) -> None:
        """Mark a task as completed"""
        self.list_tasks(Status.PENDING.value)
        if not any(t.status != Status.COMPLETED.value for t in self.tasks):
            print("No pending tasks to complete!")
            return

        try:
            task_id = int(input("\n🎯 Enter task ID to mark as complete: "))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if not task:
                print("❌ Task not found!")
                return
            
            if task.status == Status.COMPLETED.value:
                print("✅ Task is already completed!")
                return

            task.status = Status.COMPLETED.value
            task.completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_tasks()
            
            print(f"🎉 Task '{task.title}' marked as completed!")
        except ValueError:
            print("❌ Please enter a valid task ID!")
        
        input("Press Enter to continue...")

    def delete_task(self) -> None:
        """Delete a task"""
        self.list_tasks()
        if not self.tasks:
            return

        try:
            task_id = int(input("\n🗑️  Enter task ID to delete: "))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if not task:
                print("❌ Task not found!")
                return

            confirm = input(f"Are you sure you want to delete '{task.title}'? (y/N): ")
            if confirm.lower() == 'y':
                self.tasks.remove(task)
                self.save_tasks()
                print(f"🗑️  Task '{task.title}' deleted successfully!")
            else:
                print("Operation cancelled.")
        except ValueError:
            print("❌ Please enter a valid task ID!")
        
        input("Press Enter to continue...")

    def edit_task(self) -> None:
        """Edit an existing task"""
        self.list_tasks()
        if not self.tasks:
            return

        try:
            task_id = int(input("\n✏️  Enter task ID to edit: "))
            task = next((t for t in self.tasks if t.id == task_id), None)
            
            if not task:
                print("❌ Task not found!")
                return

            print(f"\n📝 Editing: {task.title}")
            print("Press Enter to keep current value")
            
            new_title = input(f"Title ({task.title}): ").strip()
            if new_title:
                task.title = new_title

            new_description = input(f"Description ({task.description}): ").strip()
            if new_description:
                task.description = new_description

            print("\n📊 Priority levels:")
            for i, priority in enumerate(Priority, 1):
                current = "← Current" if priority.value == task.priority else ""
                print(f"  {i}. {priority.value} {current}")
            
            priority_input = input("Select priority (1-4): ").strip()
            if priority_input:
                try:
                    priority_choice = int(priority_input)
                    task.priority = list(Priority)[priority_choice - 1].value
                except (ValueError, IndexError):
                    pass

            new_category = input(f"Category ({task.category}): ").strip()
            if new_category:
                task.category = new_category

            self.save_tasks()
            print(f"✅ Task '{task.title}' updated successfully!")
        except ValueError:
            print("❌ Please enter a valid task ID!")
        
        input("Press Enter to continue...")

    def show_statistics(self) -> None:
        """Show task statistics"""
        if not self.tasks:
            print("\n📊 No tasks to analyze!")
            return

        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == Status.COMPLETED.value])
        pending = total - completed

        print("\n" + "="*50)
        print("📊 TASK STATISTICS")
        print("="*50)
        print(f"📈 Total Tasks: {total}")
        print(f"✅ Completed: {completed}")
        print(f"⏳ Pending: {pending}")
        print(f"📊 Completion Rate: {(completed/total*100):.1f}%")

        # Priority breakdown
        priority_counts = {}
        for task in self.tasks:
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1

        print("\n🎯 Priority Breakdown:")
        for priority, count in priority_counts.items():
            print(f"  {priority}: {count}")

        # Category breakdown
        category_counts = {}
        for task in self.tasks:
            category_counts[task.category] = category_counts.get(task.category, 0) + 1

        print("\n🏷️  Category Breakdown:")
        for category, count in category_counts.items():
            print(f"  {category}: {count}")

        input("\nPress Enter to continue...")

    def show_menu(self) -> None:
        """Display the main menu"""
        print("\n" + "="*60)
        print(" 🎯 BEAUTIFUL TO-DO LIST MANAGER 🎯")
        print("="*60)
        print("1. 📝 Add New Task")
        print("2. 📋 View All Tasks")
        print("3. ⏳ View Pending Tasks")
        print("4. ✅ View Completed Tasks")
        print("5. 🎯 Mark Task Complete")
        print("6. ✏️  Edit Task")
        print("7. 🗑️  Delete Task")
        print("8. 📊 Show Statistics")
        print("9. 🚪 Exit")
        print("="*60)

    def run(self) -> None:
        """Run the main application loop"""
        print("🎉 Welcome to your Beautiful To-Do List Manager!")
        
        while True:
            try:
                self.show_menu()
                choice = input("Choose an option (1-9): ").strip()

                if choice == '1':
                    self.add_task()
                elif choice == '2':
                    self.list_tasks()
                    input("\nPress Enter to continue...")
                elif choice == '3':
                    self.list_tasks(Status.PENDING.value)
                    input("\nPress Enter to continue...")
                elif choice == '4':
                    self.list_tasks(Status.COMPLETED.value)
                    input("\nPress Enter to continue...")
                elif choice == '5':
                    self.mark_complete()
                elif choice == '6':
                    self.edit_task()
                elif choice == '7':
                    self.delete_task()
                elif choice == '8':
                    self.show_statistics()
                elif choice == '9':
                    print("\n👋 Thank you for using Beautiful To-Do List Manager!")
                    print("🎯 Stay productive and organized!")
                    break
                else:
                    print("❌ Invalid choice! Please select 1-9.")
                    input("Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Beautiful To-Do List Manager!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("Press Enter to continue...")


if __name__ == "__main__":
    app = TodoApp()
    app.run()