-- sales_db database aur tables
CREATE DATABASE IF NOT EXISTS sales_db;
USE sales_db;

-- Pipeline har run pe fresh data load karti hai
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id   VARCHAR(50)  PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category     VARCHAR(100) NOT NULL
);

-- Ek order me kai products ho sakte hain, isliye order_id primary key nahi hai
CREATE TABLE sales (
    sale_id    INT AUTO_INCREMENT PRIMARY KEY,
    order_id   VARCHAR(50)   NOT NULL,
    order_date DATE          NOT NULL,
    product_id VARCHAR(50)   NOT NULL,
    region     VARCHAR(50)   NOT NULL,
    quantity   INT           NOT NULL,
    price      DECIMAL(10,2) NOT NULL,
    revenue    DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order_date (order_date),
    INDEX idx_region (region)
);
