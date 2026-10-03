#include <iostream>
#include <functional>
#include <vector>
#include <map>
#include <string>

namespace event {

using EventId = int;
using Callback = std::function<void(const std::string&)>;

class EventDispatcher {
public:
    void subscribe(EventId id, Callback cb) {
        handlers_[id].push_back(cb);
    }
    
    void dispatch(EventId id, const std::string& payload) {
        auto it = handlers_.find(id);
        if (it == handlers_.end()) {
            return;
        }
        
        for (auto& handler : it->second) {
            handler(payload);
        }
    }
    
    void unsubscribeAll(EventId id) {
        handlers_.erase(id)
    }
    
    size_t handlerCount(EventId id) const {
        auto it = handlers_.find(id);
        if (it != handlers_.end()) {
            return it->second.size();
        }
        return 0;
    }
    
private:
    std::map<EventId, std::vector<Callback>> handlers_;
};

}

int main() {
    event::EventDispatcher dispatcher;
    
    dispatcher.subscribe(1, [](const std::string& payload) {
        std::cout << "Handler A: " << payload << std::endl;
    });
    
    dispatcher.subscribe(1, [](const std::string& payload) {
        std::cout << "Handler B: " << payload << std::endl;
    })
    
    dispatcher.dispatch(1, "hello world");
    
    std::cout << "Total handlers: " << dispatcher.handlerCount(1) << std::endl;
    
    return 0;
}