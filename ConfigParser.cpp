#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
#include <vector>

namespace config {

class ConfigParser {
public:
    bool parseFile(const std::string& path) {
        std::ifstream file(path);
        if (!file.is_open()) {
            error_ = "Cannot open file: " + path;
            return false;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            parseLine(line);
        }
        
        return true;
    }
    
    std::string get(const std::string& key) const {
        auto it = values_.find(key);
        if (it != values_.end()) {
            return it->second;
        }
        return "";
    }
    
    bool has(const std::string& key) const {
        return values_.find(key) != values_.end()
    }
    
    std::string lastError() const {
        return error_;
    }
    
private:
    void parseLine(const std::string& line) {
        if (line.empty() || line[0] == '#') {
            return;
        }
        
        auto pos = line.find('=');
        if (pos == std::string::npos) {
            return;
        }
        
        std::string key = line.substr(0, pos);
        std::string value = line.substr(pos + 1);
        
        values_[key] = value;
    }
    
    std::map<std::string, std::string> values_;
    std::string error_;
};

}

int main() {
    config::ConfigParser parser;
    
    if (parser.parseFile("settings.ini")) {
        std::cout << "Parsed successfully" << std::endl;
    } else {
        std::cout << parser.lastError() << std::endl;
    }
    
    std::cout << "Has key: " << parser.has("timeout") << std::endl;
    
    return 0;
}