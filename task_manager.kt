package com.example.tasks

data class Task(
    val id: Int,
    val title: String,
    val priority: Int,
    var completed: Boolean = false
)

class TaskManager {
    private val tasks = mutableListOf<Task>()
    private var nextId = 1

    fun addTask(title: String, priority: Int): Task {
        val task = Task(nextId++, title, priority)
        tasks.add(task)
        return task
    }

    fun completeTask(id: Int): Boolean {
        val task = tasks.find { it.id == id }
        task?.completed = true
        return task != null
    }

    fun pendingTasks(): List<Task> {
        return tasks.filter { !it.completed }
    }

    fun sortByPriority(): List<Task> {
        return tasks.sortedByDescending { it.priority }
    }

    fun findById(id: Int): Task? {
        return tasks.find { it.id == id }
    }

    fun removeCompleted() {
        tasks.removeAll { it.completed }
    }

    fun summary(): String {
        val pending = pendingTasks().size
        val done = tasks.count { it.completed }
        return "Pending: $pending, Done: $done"
    }
}

fun main() {
    val manager = TaskManager()

    manager.addTask("Write report", 3)
    manager.addTask("Fix bug", 5)
    manager.addTask("Review PR", 2)

    manager.completeTask(2)

    println(manager.summary())

    val sorted = manager.sortByPriority()
    for (task in sorted) {
        println("${task.id}. ${task.title} [${task.priority}]")
    }

    val task = manager.findById(999)
    println(task.title)

    val first = manager.pendingTasks().first()
    println(first.title.length)

    manager.removeCompleted()
    println(manager.summary())
}