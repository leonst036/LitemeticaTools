import numpy as np
from litemapy import Schematic, Region
import nbtlib

def get_material_list(file_path, file_format, filters=None):
    """
    Analysiert die Datei und gibt ein Dictionary mit {Block-ID: Anzahl} zurück.
    filters: Dictionary mit Bool-Werten (ignore_liquids, ignore_helpers)
    """
    if filters is None:
        filters = {}

    ignore_liquids = filters.get("ignore_liquids", False)
    ignore_helpers = filters.get("ignore_helpers", False)
    
    liquid_ids = ["minecraft:water", "minecraft:lava", "minecraft:bubble_column"]
    helper_ids = ["minecraft:dirt", "minecraft:grass_block", "minecraft:scaffolding", "minecraft:cobblestone"]

    if file_format == "litematica":
        sch = Schematic.load(file_path)
        material_counts = {}
        for region in sch.regions.values():
            unique, counts = np.unique(region._Region__blocks, return_counts=True)
            for idx, count in zip(unique, counts):
                block = region.palette[idx]
                name = block.id
                
                if name == "minecraft:air":
                    continue
                if ignore_liquids and name in liquid_ids:
                    continue
                if ignore_helpers and name in helper_ids:
                    continue

                if name in material_counts:
                    material_counts[name] += int(count)
                else:
                    material_counts[name] = int(count)
        return material_counts
        
    elif file_format == "schematica":
        nbt_data = nbtlib.load(file_path)
        region, _ = Region.from_sponge_nbt(nbt_data)
        material_counts = {}
        unique, counts = np.unique(region._Region__blocks, return_counts=True)
        for idx, count in zip(unique, counts):
            block = region.palette[idx]
            name = block.id
            
            if name == "minecraft:air":
                continue
            if ignore_liquids and name in liquid_ids:
                continue
            if ignore_helpers and name in helper_ids:
                continue

            if name in material_counts:
                material_counts[name] += int(count)
            else:
                material_counts[name] = int(count)
        return material_counts
        
    return {}

def format_quantity(amount):
    """
    Rechnet eine Menge in Shulkerkisten (SB), Stacks und Items um.
    """
    shulkers = amount // 1728
    remainder = amount % 1728
    stacks = remainder // 64
    items = remainder % 64
    
    parts = []
    if shulkers > 0:
        parts.append(f"{shulkers} SB")
    if stacks > 0:
        parts.append(f"{stacks} Stk")
    if items > 0 or amount == 0:
        parts.append(f"{items}")
        
    return " + ".join(parts)
