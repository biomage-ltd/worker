def get_all_cell_ids_in(cell_set):
    cell_ids = cell_set["cellIds"]

    children = cell_set.get("children", None)
    if children:
        for child in children:
            cell_ids += all_cell_ids_in(child)

    return cell_ids

def get_all_cell_ids_on_current_level(cell_sets, ignoring_set_id=None):
    cell_sets_to_return = []
  
    for cell_set in cell_sets:
        if ignoring_set_id and cell_set["key"] == ignoring_set_id:
            continue

        # cell_sets_to_return.append(cell_set["key"])
        cell_sets_to_return += get_all_cell_ids_in(cell_set)

    return cell_sets_to_return

# returns a list with 
def find_cell_ids_in_same_hierarchy(key, cell_sets):
    for cell_set in cell_sets:
        if cell_set["key"] == key:
            return get_all_cell_ids_on_current_level(cell_sets, ignoring_set_id=key)
        
        if cell_set.get("children", None):
            result = find_cell_ids_in_same_hierarchy(key, cell_set["children"])

            if result:
                return result

    return []
