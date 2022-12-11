import sqlite3

# Read data from the database
def sql_read(sql, db='mrp.db'):
    # Connect to the database
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Execute the SQL
    c.execute(sql)

    # Get the results
    results = c.fetchall()

    # Close the connection
    conn.close()

    return results

# Write data to the database
def sql_write(sql, db='mrp.db'):
    # Connect to the database
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Execute the SQL
    c.execute(sql)

    # Save the changes
    conn.commit()

    # Close the connection
    conn.close()

# Clear a table
def empty_table(table, db='mrp.db'):
    sql_write('DELETE FROM ' + table, db)

