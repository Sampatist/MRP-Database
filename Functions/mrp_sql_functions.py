from Functions.sql_functions import *

# Update BOM levels in Item table
def sql_update_bom_levels():
  sql = '''
    WITH RECURSIVE level_zero_items(Item_ID) AS (
      SELECT Item_ID
      FROM Item
      WHERE Item_ID NOT IN (SELECT DISTINCT Component_ID FROM BOM)
    ),
    component_levels(Component_ID, Level) AS (
      SELECT Component_ID, 1
      FROM BOM
      WHERE Item_ID IN (SELECT Item_ID FROM level_zero_items)
      UNION ALL
      SELECT CHILD.Component_ID, Level + 1
      FROM component_levels AS PARENT, BOM AS CHILD
      WHERE PARENT.Component_ID = CHILD.Item_ID 
    ),
    item_levels(Item_ID, Level) AS (
      SELECT Item_ID, 0 AS Level
      FROM level_zero_items
      UNION
      SELECT Component_ID, MAX(Level) AS Level
      FROM component_levels
      GROUP BY Component_ID
    )
    UPDATE Item
      SET BOM_Level = item_levels.Level
      FROM item_levels
      WHERE Item.Item_ID = item_levels.Item_ID;
  '''
  sql_write(sql)

# Calculate planned order receipt for items in bom_level for period_ID
def sql_calc_mrp_planned_order_receipt(bom_level, period_ID):
    sql = f'''
    WITH level_i_items AS (
        SELECT Item_ID
        FROM Item
        WHERE BOM_Level = {bom_level}
    ), 
    t_Projected_Inventory_without_order AS (
        SELECT IP.Item_ID, IP.Period,
            (CASE WHEN IP.Period = 1
                THEN IP.Scheduled_Receipt - IP.Gross_Requirement + I.Current_Inventory
                ELSE IP.Scheduled_Receipt - IP.Gross_Requirement + (SELECT Projected_Inventory FROM Item_Period WHERE Item_ID = IP.Item_ID AND Period = IP.Period - 1)
            END) AS Projected_Inventory_without_order, 
            I.Lead_Time, I.Lot_Size
        FROM Item AS I
        JOIN Item_Period AS IP 
        ON I.Item_ID = IP.Item_ID
        WHERE I.Item_ID IN level_i_items AND IP.Period = {period_ID}
    ),
    t_Net_Requirement AS (
        SELECT Item_ID, Period, 
            Projected_Inventory_without_order,
            MAX(-Projected_Inventory_without_order,0) AS Net_Requirement,
            Lead_Time, Lot_Size
        FROM t_Projected_Inventory_without_order
    ),
    t_Planned_Order_Receipt AS (
        SELECT Item_ID, Period, 
            Projected_Inventory_without_order,
            Net_Requirement,
            (CASE WHEN Period - Lead_Time > 0 AND Net_Requirement > 0 
                THEN MAX(Lot_Size, Net_Requirement)
                ELSE 0
            END) AS Planned_Order_Receipt,
            Lead_Time, Lot_Size
    FROM t_Net_Requirement
    ),
    t_Projected_Inventory_after_order AS (
        SELECT Item_ID, Period,
            Projected_Inventory_without_order + Planned_Order_Receipt AS Projected_Inventory_after_order,
            Net_Requirement,
            Planned_Order_Receipt
        FROM t_Planned_Order_Receipt
    )
    UPDATE Item_Period AS IP
        SET Projected_Inventory = PIAO.Projected_Inventory_after_order,
            Net_Requirement = PIAO.Net_Requirement,
            Planned_Order_Receipt = PIAO.Planned_Order_Receipt
        FROM t_Projected_Inventory_after_order AS PIAO
        WHERE IP.Item_ID = PIAO.Item_ID AND IP.Period = PIAO.Period;
    '''
    sql_write(sql)


# Calculate planned order releases for all items in bom_level
def sql_calc_mrp_planned_order_releases(bom_level):
    sql=f'''
    WITH level_i_items AS (
        SELECT Item_ID
        FROM Item
        WHERE BOM_Level = {bom_level}
    ), 
    temp AS (
        SELECT I.Item_ID, IP.Period, IP.Planned_Order_Receipt, I.Lead_Time
        FROM Item AS I
        JOIN Item_Period AS IP
        ON I.Item_ID = IP.Item_ID
        WHERE I.Item_ID IN level_i_items
    )
    UPDATE Item_Period AS IP
        SET Planned_Order_Release = t.Planned_Order_Receipt 
        FROM temp AS t
        WHERE IP.Item_ID = t.Item_ID AND IP.Period = t.Period - t.Lead_Time;
    '''
    sql_write(sql)


# Calculate MRP for all items, periods in bom_level
def sql_calc_mrp(bom_level):
    sql = '''
    SELECT MAX(Period_ID) FROM Period;
    '''
    period_max = sql_read(sql)[0][0]

    for period in range(1, period_max + 1):
        sql_calc_mrp_planned_order_receipt(bom_level, period)

    sql_calc_mrp_planned_order_releases(bom_level)


# Calculate gross requirement for all components of items in bom_level  
# Add dependent demand to the existing independent demand
def sql_calc_component_gross_requirement(bom_level):
    sql = f'''
    WITH level_i_items AS (
        SELECT Item_ID
        FROM Item
        WHERE BOM_Level = {bom_level}
    )
    UPDATE Item_Period AS IP1
        SET Gross_Requirement = IP1.Gross_Requirement + COALESCE(IP0.Planned_Order_Release,0) * B.BOM_Multiplier
        FROM BOM AS B
        JOIN Item_Period AS IP0
        ON B.Item_ID = IP0.Item_ID
        WHERE IP1.Item_ID = B.Component_ID AND IP0.Period = IP1.Period AND B.Item_ID IN level_i_items;
    '''
    sql_write(sql)


# Perform all MRP calculations
def calc_all_mrp_table():
    sql = '''
    SELECT MAX(BOM_Level)
    FROM Item
    '''
    bom_level_max = sql_read(sql)[0][0]
    
    for bom_level in range(bom_level_max + 1):
        sql_calc_mrp(bom_level)
        sql_calc_component_gross_requirement(bom_level)