from models import create_db_and_tables

# This tries to connect to Postgres and create the table.
# If it runs without error, you are successful!
if __name__ == "__main__":
    try:
        create_db_and_tables()
        print("Success! Table created.")
    except Exception as e:
        print(f"Error: {e}")