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
