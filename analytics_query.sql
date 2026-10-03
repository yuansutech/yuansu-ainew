CREATE TABLE customers (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    total DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT,
    product_name VARCHAR(200),
    quantity INT,
    unit_price DECIMAL(10, 2)
);
SELECT
    c.id,
    c.name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS lifetime_value,
    AVG(o.total) AS average_order
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name
HAVING COUNT(o.id) > 0
ORDER BY lifetime_value DESC
INSERT INTO customers (id, name, email)
VALUES (1, 'Alice', 'alice@example.com');
SELECT
    o.id AS order_id,
    c.name AS customer_name,
    SUM(oi.quantity * oi.unit_price) AS calculated_total
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, c.name
WHERE o.status = 'completed';
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        SUM(total) AS revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', created_at)
)
SELECT month, revenue
FROM monthly_revenue
WHERE revenue > (SELECT AVG(revenue) FROM monthly_revenue);
UPDATE customers
SET email = 'updated@example.com'
WHERE id = 1;
DELETE FROM orders
WHERE status = 'cancelled' AND created_at < NOW() - INTERVAL '30 days';
DROP TABLE customers
