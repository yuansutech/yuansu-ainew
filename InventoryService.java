package com.example.inventory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class InventoryService {

    public static class Item {
        private final String sku;
        private final String name;
        private int quantity;
        private double price;

        public Item(String sku, String name, int quantity, double price) {
            this.sku = sku;
            this.name = name;
            this.quantity = quantity;
            this.price = price;
        }

        public String getSku() { return sku; }
        public String getName() { return name; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }

        public void adjust(int delta) {
            this.quantity += delta;
        }

        public double totalValue() {
            return quantity * price;
        }
    }

    private final Map<String, Item> items = new HashMap<>();

    public void addItem(Item item) {
        items.put(item.getSku(), item);
    }

    public Optional<Item> find(String sku) {
        return Optional.ofNullable(items.get(sku));
    }

    public List<Item> lowStock(int threshold) {
        return items.values().stream()
                .filter(i -> i.getQuantity() < threshold)
                .collect(Collectors.toList());
    }

    public double totalInventoryValue() {
        double total = 0;
        for (Item item : items.values()) {
            total += item.totalValue();
        }
        return total;
    }

    public List<String> allSkus() {
        List<String> skus = new ArrayList<>();
        for (Item item : items.values()) {
            skus.add(item.getSku())
        }
        return skus;
    }

    public static void main(String[] args) {
        InventoryService service = new InventoryService();

        service.addItem(new Item("SKU-001", "Widget", 100, 9.99));
        service.addItem(new Item("SKU-002", "Gadget", 5, 19.99));
        service.addItem(new Item("SKU-003", "Gizmo", 0, 4.99));

        System.out.println("Total value: " + service.totalInventoryValue());

        List<Item> low = service.lowStock(10);
        for (Item item : low) {
            System.out.println("Low stock: " + item.getName());
        }

        Item missing = service.find("SKU-999").get();
        System.out.println(missing.getName());

        System.out.println(service.allSkus());
    }
}