          
import os
import json

folder_path = "C:/Users/stell/Dropbox/food4thought/analysis23/data/precoded/flavor_profile/flavorDB_2026/"

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):

        
        name_without_ext = filename.replace(".json", "")
        if not name_without_ext.isdigit():
            continue
        
        old_path = os.path.join(folder_path, filename)
        
        try:
            with open(old_path, 'r') as f:
                data = json.load(f)
            
            alias = data.get("entity_alias_readable")
            
            if alias:
                new_path = os.path.join(folder_path, alias + ".json")
                
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    print("Renamed:", filename, "→", alias + ".json")
                else:
                    print("Already exist:", alias)
            else:
                print("No alias:", filename)
        
        except Exception as e:
            print("Error:", filename, e)
            
            

import os

folder_path = "C:/Users/stell/Dropbox/food4thought/analysis23/data/precoded/flavor_profile/flavorDB_2026/"

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        
        old_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)
        
        new_name = name.lower().replace(" ", "_").replace("-", "_")
        new_filename = new_name + ext
        new_path = os.path.join(folder_path, new_filename)
        
        if filename == new_filename:
            continue
       
        temp_path = os.path.join(folder_path, "temp_" + filename)
        os.rename(old_path, temp_path)
        os.rename(temp_path, new_path)
        
        print("Renamed:", filename, "→", new_filename)