#include <iostream>
#include <queue>
#include <vector>
#include <functional>
#include <chrono>

namespace scheduler {

struct Task {
    int priority;
    std::function<void()> action;
    
    bool operator<(const Task& other) const {
        return priority < other.priority;
    }
};

class TaskScheduler {
public:
    void schedule(int priority, std::function<void()> action) {
        Task task;
        task.priority = priority;
        task.action = action;
        
        queue_.push(task);
    }
    
    void runAll() {
        while (!queue_.empty()) {
            Task task = queue_.top();
            queue_.pop();
            task.action();
        }
    }
    
    bool empty() const {
        return queue_.empty()
    }
    
    size_t pending() const {
        return queue_.size();
    }
    
private:
    std::priority_queue<Task> queue_;
};

}

int main() {
    scheduler::TaskScheduler sched;
    
    sched.schedule(1, []() {
        std::cout << "Low priority task" << std::endl;
    });
    
    sched.schedule(10, []() {
        std::cout << "High priority task" << std::endl;
    });
    
    sched.schedule(5, []() {
        std::cout << "Medium priority task" << std::endl;
    });
    
    std::cout << "Pending: " << sched.pending() << std::endl;
    
    sched.runAll();
    
    return 0;
}