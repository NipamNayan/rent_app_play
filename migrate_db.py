import os
import sqlite3

# Path to the database file
db_path = 'instance/rentals.db'

def migrate_database():
    """Add price_type column to the listing table if it doesn't exist"""
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if price_type column exists
    cursor.execute("PRAGMA table_info(listing)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'price_type' not in column_names:
        print("Adding price_type column to listing table...")
        
        # Add the price_type column with default value 'month'
        cursor.execute("ALTER TABLE listing ADD COLUMN price_type VARCHAR(10) DEFAULT 'month'")
        
        # Set price_type to 'day' for Car listings
        cursor.execute("UPDATE listing SET price_type = 'day' WHERE type = 'Car'")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully.")
    else:
        print("price_type column already exists. No migration needed.")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    migrate_database() 