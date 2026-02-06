"""
=============================================================================
SAMPLE DATABASE CREATOR
=============================================================================
Creates sample source and target databases for testing the migration platform.
This simulates a real-world scenario: Legacy CRM → Modern CRM migration.
=============================================================================
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random


def create_sample_databases():
    """
    Create two SQLite databases:
    1. source_legacy_crm.db - Old system with abbreviated column names
    2. target_modern_crm.db - New system with clean column names
    """
    
    os.makedirs("data", exist_ok=True)
    
    # =========================================================================
    # SOURCE DATABASE (Legacy CRM)
    # Uses abbreviations, old conventions
    # =========================================================================
    source_path = "data/source_legacy_crm.db"
    
    if os.path.exists(source_path):
        os.remove(source_path)
    
    source_conn = sqlite3.connect(source_path)
    source_cursor = source_conn.cursor()
    
    # Customers table (legacy naming)
    source_cursor.execute("""
        CREATE TABLE cust (
            cust_id INTEGER PRIMARY KEY,
            cust_fname VARCHAR(50),
            cust_lname VARCHAR(50),
            cust_email VARCHAR(100),
            cust_ph VARCHAR(20),
            cust_addr TEXT,
            cust_city VARCHAR(50),
            cust_state VARCHAR(2),
            cust_zip VARCHAR(10),
            cust_type VARCHAR(20),
            cust_status INTEGER,
            created_dt DATETIME,
            modified_dt DATETIME
        )
    """)
    
    # Products table
    source_cursor.execute("""
        CREATE TABLE prod (
            prod_id INTEGER PRIMARY KEY,
            prod_name VARCHAR(100),
            prod_desc TEXT,
            prod_cat VARCHAR(50),
            prod_price FLOAT,
            prod_qty INTEGER,
            prod_status INTEGER,
            created_dt DATETIME
        )
    """)
    
    # Orders table
    source_cursor.execute("""
        CREATE TABLE ord (
            ord_id INTEGER PRIMARY KEY,
            cust_id INTEGER,
            ord_dt DATETIME,
            ord_status VARCHAR(20),
            ord_total FLOAT,
            ship_addr TEXT,
            ship_city VARCHAR(50),
            ship_state VARCHAR(2),
            ship_zip VARCHAR(10),
            created_dt DATETIME,
            FOREIGN KEY (cust_id) REFERENCES cust(cust_id)
        )
    """)
    
    # Order items
    source_cursor.execute("""
        CREATE TABLE ord_items (
            item_id INTEGER PRIMARY KEY,
            ord_id INTEGER,
            prod_id INTEGER,
            item_qty INTEGER,
            item_price FLOAT,
            item_total FLOAT,
            FOREIGN KEY (ord_id) REFERENCES ord(ord_id),
            FOREIGN KEY (prod_id) REFERENCES prod(prod_id)
        )
    """)
    
    # Insert sample data
    customers = [
        (1, "John", "Smith", "john.smith@email.com", "555-0101", "123 Main St", "Austin", "TX", "78701", "premium", 1, "2023-01-15", "2024-01-01"),
        (2, "Jane", "Doe", "jane.doe@email.com", "555-0102", "456 Oak Ave", "Dallas", "TX", "75201", "regular", 1, "2023-02-20", "2024-01-05"),
        (3, "Bob", "Johnson", "bob.j@email.com", "555-0103", "789 Pine Rd", "Houston", "TX", "77001", "premium", 1, "2023-03-10", "2024-01-10"),
        (4, "Alice", "Williams", "alice.w@email.com", "555-0104", "321 Elm St", "San Antonio", "TX", "78201", "regular", 0, "2023-04-05", "2024-01-15"),
        (5, "Charlie", "Brown", "charlie.b@email.com", "555-0105", "654 Maple Dr", "Austin", "TX", "78702", "premium", 1, "2023-05-25", "2024-01-20"),
    ]
    
    source_cursor.executemany(
        "INSERT INTO cust VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        customers
    )
    
    products = [
        (1, "Laptop Pro 15", "High-performance laptop", "Electronics", 1299.99, 50, 1, "2023-01-01"),
        (2, "Wireless Mouse", "Ergonomic wireless mouse", "Electronics", 49.99, 200, 1, "2023-01-01"),
        (3, "USB-C Hub", "7-port USB-C hub", "Electronics", 79.99, 100, 1, "2023-01-01"),
        (4, "Monitor 27inch", "4K UHD Monitor", "Electronics", 399.99, 30, 1, "2023-02-01"),
        (5, "Keyboard Mech", "Mechanical keyboard RGB", "Electronics", 129.99, 75, 1, "2023-02-01"),
    ]
    
    source_cursor.executemany(
        "INSERT INTO prod VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        products
    )
    
    orders = [
        (1, 1, "2024-01-10", "completed", 1349.98, "123 Main St", "Austin", "TX", "78701", "2024-01-10"),
        (2, 2, "2024-01-12", "completed", 129.98, "456 Oak Ave", "Dallas", "TX", "75201", "2024-01-12"),
        (3, 3, "2024-01-15", "shipped", 479.98, "789 Pine Rd", "Houston", "TX", "77001", "2024-01-15"),
        (4, 1, "2024-01-18", "processing", 399.99, "123 Main St", "Austin", "TX", "78701", "2024-01-18"),
        (5, 5, "2024-01-20", "pending", 1429.98, "654 Maple Dr", "Austin", "TX", "78702", "2024-01-20"),
    ]
    
    source_cursor.executemany(
        "INSERT INTO ord VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        orders
    )
    
    order_items = [
        (1, 1, 1, 1, 1299.99, 1299.99),
        (2, 1, 2, 1, 49.99, 49.99),
        (3, 2, 2, 1, 49.99, 49.99),
        (4, 2, 3, 1, 79.99, 79.99),
        (5, 3, 4, 1, 399.99, 399.99),
        (6, 3, 3, 1, 79.99, 79.99),
        (7, 4, 4, 1, 399.99, 399.99),
        (8, 5, 1, 1, 1299.99, 1299.99),
        (9, 5, 5, 1, 129.99, 129.99),
    ]
    
    source_cursor.executemany(
        "INSERT INTO ord_items VALUES (?, ?, ?, ?, ?, ?)",
        order_items
    )
    
    source_conn.commit()
    source_conn.close()
    print(f"✅ Created source database: {source_path}")
    
    # =========================================================================
    # TARGET DATABASE (Modern CRM)
    # Uses full names, modern conventions
    # =========================================================================
    target_path = "data/target_modern_crm.db"
    
    if os.path.exists(target_path):
        os.remove(target_path)
    
    target_conn = sqlite3.connect(target_path)
    target_cursor = target_conn.cursor()
    
    # Customers table (modern naming)
    target_cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email_address VARCHAR(255),
            phone_number VARCHAR(30),
            street_address TEXT,
            city VARCHAR(100),
            state_code VARCHAR(10),
            postal_code VARCHAR(20),
            customer_type VARCHAR(50),
            is_active BOOLEAN,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Products table
    target_cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name VARCHAR(200),
            description TEXT,
            category VARCHAR(100),
            unit_price DECIMAL(10,2),
            stock_quantity INTEGER,
            is_available BOOLEAN,
            created_at TIMESTAMP
        )
    """)
    
    # Orders table
    target_cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TIMESTAMP,
            order_status VARCHAR(50),
            total_amount DECIMAL(10,2),
            shipping_address TEXT,
            shipping_city VARCHAR(100),
            shipping_state VARCHAR(10),
            shipping_postal_code VARCHAR(20),
            created_at TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Order line items
    target_cursor.execute("""
        CREATE TABLE order_line_items (
            line_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            line_total DECIMAL(10,2),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    target_conn.commit()
    target_conn.close()
    print(f"✅ Created target database: {target_path}")
    
    return source_path, target_path


def print_schema_info(db_path: str, db_name: str):
    """Print schema information for a database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n{'='*60}")
    print(f"Schema: {db_name}")
    print('='*60)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        
        print(f"\n📋 Table: {table} ({row_count} rows)")
        print("-" * 40)
        for col in columns:
            pk = "🔑 " if col[5] else "   "
            nullable = "" if col[3] else " NOT NULL"
            print(f"  {pk}{col[1]}: {col[2]}{nullable}")
    
    conn.close()


if __name__ == "__main__":
    print("Creating sample databases...\n")
    source, target = create_sample_databases()
    
    print_schema_info(source, "Source (Legacy CRM)")
    print_schema_info(target, "Target (Modern CRM)")
    
    print("\n" + "="*60)
    print("Sample databases created successfully!")
    print("="*60)
    print("\nNow run:")
    print("  python main.py data/source_legacy_crm.db data/target_modern_crm.db")
    print("\nOr launch the Streamlit UI:")
    print("  streamlit run app.py")
