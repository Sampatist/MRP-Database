from Functions.sql_functions import *
import pandas as pd

# Multiple Row manipulation function, requires reading the excel data into ram before inserting to database
# Read excel and write to a table in database
def excel_to_table(ref, table, db='MRP.db'):
    df = pd.read_excel(ref)
    
    conn = sqlite3.connect(db)
    c = conn.cursor()

    df.to_sql(table, conn, if_exists='append', index=False)

    conn.close()



# Single Row manipulation functions, not used in the project. (was used for debug purposes)

# Count the number of rows with given key in a table
def count_key(table, key1, key_val1, key2=None, key_val2=None, db='mrp.db'):
    if key2 is None:
        sql = f'''
          SELECT COUNT(1)
          FROM {table}
          WHERE {key1} = {key_val1}
        '''
    else:
        sql = f'''
        SELECT COUNT(1)
        FROM {table}
        WHERE {key1} = {key_val1} AND {key2} = {key_val2}
        '''
    results = sql_read(sql, db)
    return results[0][0]

# Insert a new record into the Item table
def insert_item(Item_ID, Item_Name, Lot_Size, Lead_Time, Current_Inventory, Bom_Level=0):
  if count_key('Item', 'Item_ID', Item_ID) == 0:
    print('Item already exists')
  else:
    sql = f'''
      INSERT INTO Item
      VALUES ({Item_ID}, '{Item_Name}', {Lot_Size}, {Lead_Time}, {Current_Inventory}, {Bom_Level});
    '''
    sql_write(sql)

# Delete a record from the Item table
def delete_item(Item_ID):
  if count_key('Item', 'Item_ID', Item_ID) == 0:
    print('Item does not exist')
  else:
    sql = f'''
      DELETE FROM Item
      WHERE Item_ID = {Item_ID};
    '''
    sql_write(sql)

# Insert a new record into the BOM table
def insert_bom(Item_ID, Component_ID, BOM_Multiplier):
  if count_key('BOM', 'Item_ID', Item_ID, 'Component_ID', Component_ID) == 0:
    print('BOM already exists')
  else:
    sql = f'''
      INSERT INTO BOM
      VALUES ({Item_ID}, {Component_ID}, {BOM_Multiplier});
    '''
    sql_write(sql)

# Delete a record from the BOM table
def delete_bom(Item_ID, Component_ID):
  if count_key('BOM', 'Item_ID', Item_ID, 'Component_ID', Component_ID) == 0:
    print('BOM does not exist')
  else:
    sql = f'''
      DELETE FROM BOM
      WHERE Item_ID = {Item_ID} AND Component_ID = {Component_ID};
    '''
    sql_write(sql)

# Insert a new record into the Period table
def insert_period(Period_ID, Date):
  if count_key('Period', 'Period_ID', Period_ID) == 0:
    print('Period already exists')
  else:
    sql = f'''
      INSERT INTO Period
      VALUES ({Period_ID}, '{Date}');
    '''
    sql_write(sql)

# Delete a record from the Period table
def delete_period(Period_ID):
  if count_key('Period', 'Period_ID', Period_ID) == 0:
    print('Period does not exist')
  else:
    sql = f'''
      DELETE FROM Period
      WHERE Period_ID = {Period_ID};
    '''
    sql_write(sql)

# Insert a new record into the item-period table
def insert_item_period(Item_ID, Period_ID, Gross_Requirement, Scheduled_Receipt, Projected_Inventory, Net_Requirement, Planned_Order_Receipt, Planned_Order_Release):
  if count_key('Item_Period', 'Item_ID', Item_ID, 'Period_ID', Period_ID) == 0:
    print('Item_Period already exists')
  else:
    sql = f'''
      INSERT INTO Item_Period
      VALUES ({Item_ID}, {Period_ID}, {Gross_Requirement}, {Scheduled_Receipt}, {Projected_Inventory}, {Net_Requirement}, {Planned_Order_Receipt}, {Planned_Order_Release});
    '''
    sql_write(sql)

# Delete a record from the item-period table
def delete_item_period(Item_ID, Period):
  if count_key('Item_Period', 'Item_ID', Item_ID, 'Period_ID', Period_ID) == 0:
    print('Item_Period does not exist')
  else:
    sql = f'''
      DELETE FROM Item_Period
      WHERE Item_ID = {Item_ID} AND Period_ID = {Period_ID};
    '''
    sql_write(sql)
