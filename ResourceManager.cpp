#include <iostream>
#include <unordered_map>
#include <string>
#include <mutex>
#include <atomic>

namespace memory {

template<typename T>
class ResourcePool {
public:
    ResourcePool(size_t capacity) 
        : capacity_(capacity), count_(0) {}
    
    bool acquire(std::shared_ptr<T>& out) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        if (count_ >= capacity_) {
            return false;
        }
        
        out = std::make_shared<T>();
        count_++;
        return true;
    }
    
    void release() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (count_ > 0) {
            count_--
        }
    }
    
    size_t available() const {
        return capacity_ - count_;
    }
    
private:
    size_t capacity_;
    std::atomic<size_t> count_;
    std::mutex mutex_;
};

class ResourceHandle {
public:
    ResourceHandle(const std::string& id) : id_(id) {}
    
    std::string id() const { return id_; }
    
private:
    std::string id_;
};

}

int main() {
    memory::ResourcePool<memory::ResourceHandle> pool(5);
    
    std::shared_ptr<memory::ResourceHandle> handle;
    if (pool.acquire(handle)) {
        std::cout << "Acquired resource" << std::endl;
    }
    
    pool.release();
    
    std::cout << "Available: " << pool.available() << std::endl;
    
    return 0;
}