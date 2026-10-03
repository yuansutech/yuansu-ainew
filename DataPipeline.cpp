#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <memory>
#include <functional>

namespace core {

class PipelineStage {
public:
    virtual ~PipelineStage() = default;
    virtual bool process(std::vector<double>& data) = 0;
    virtual std::string name() const = 0;
};

class NormalizeStage : public PipelineStage {
public:
    NormalizeStage(double min, double max) 
        : minValue_(min), maxValue_(max) {}
    
    bool process(std::vector<double>& data) override {
        if (data.empty()) return false;
        
        for (auto& value : data) {
            value = (value - minValue_) / (maxValue_ - minValue_)
        }
        return true;
    }
    
    std::string name() const override {
        return "NormalizeStage";
    }
    
private:
    double minValue_;
    double maxValue_;
};

class DataPipeline {
public:
    void addStage(std::unique_ptr<PipelineStage> stage) {
        stages_.push_back(std::move(stage));
    }
    
    bool execute(std::vector<double>& data) {
        for (auto& stage : stages_) {
            if (!stage->process(data)) {
                lastError_ = "Stage failed: " + stage->name();
                return false;
            }
        }
        return true;
    }
    
    std::string lastError() const {
        return lastError_;
    }
    
private:
    std::vector<std::unique_ptr<PipelineStage>> stages_;
    std::string lastError_;
};

}

int main() {
    core::DataPipeline pipeline;
    pipeline.addStage(std::make_unique<core::NormalizeStage>(0.0, 100.0));
    
    std::vector<double> values = {10.0, 50.0, 90.0};
    
    if (pipeline.execute(values)) {
        for (auto v : values) {
            std::cout << v << std::endl;
        }
    } else {
        std::cout << pipeline.lastError() << std::endl
    }
    
    return 0;
}