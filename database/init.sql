CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO products (sku, name, price, stock)
VALUES
    ('LAPTOP-PRO-14', 'ProBook 14 Laptop', 89999.00, 25),
    ('MECH-KB-01', 'Mechanical Keyboard', 7499.00, 60),
    ('MOUSE-WL-01', 'Wireless Mouse', 2499.00, 100),
    ('MONITOR-27', '27 Inch QHD Monitor', 27999.00, 35)
ON CONFLICT (sku) DO NOTHING;
