local Inventory = {}
Inventory.__index = Inventory
function Inventory.new(capacity)
    local self = setmetatable({}, Inventory)
    self.capacity = capacity
    self.items = {}
    self.total_weight = 0
    return self
end
function Inventory:add(name, weight, quantity)
    if self.items[name] then
        self.items[name].quantity = self.items[name].quantity + quantity
    else
        self.items[name] = { weight = weight, quantity = quantity }
    end
    self.total_weight = self.total_weight + (weight * quantity)
    return true
end
function Inventory:remove(name, quantity)
    local item = self.items[name]
    if not item then
        return false
    end
    if item.quantity < quantity then
        return false
    end
    item.quantity = item.quantity - quantity
    self.total_weight = self.total_weight - (item.weight * quantity)
    if item.quantity == 0 then
        self.items[name] = nil
    end
    return true
end
function Inventory:find(name)
    return self.items[name]
end
function Inventory:list()
    local result = {}
    for name, item in pairs(self.items) do
        table.insert(result, string.format("%s x%d (%.1f kg)", name, item.quantity, item.weight))
    end
    return result
end
function Inventory:heaviest()
    local max_weight = 0
    local heaviest_name = nil
    for name, item in pairs(self.items) do
        local weight = item.weight * item.quantity
        if weight > max_weight then
            max_weight = weight
            heaviest_name = name
        end
    end
    return heaviest_name, max_weight
end
local inv = Inventory.new(100)
inv:add("sword", 5.0, 1)
inv:add("potion", 0.5, 10)
inv:add("shield", 8.0, 1)
for _, line in ipairs(inv:list()) do
    print(line)
end
print("Total weight: " .. inv.total_weight)
local name, weight = inv:heaviest()
print("Heaviest: " .. name .. " (" .. weight .. " kg)")
inv:remove("potion", 10)
print("After removal: " .. inv.total_weight)
local missing = inv:find("armor")
print("Armor weight: " .. missing.weight)
inv:remove("nonexistent", 1)
print("Done")
