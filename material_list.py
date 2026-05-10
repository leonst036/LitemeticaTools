import numpy as np
from litemapy import Schematic, Region
import nbtlib

def get_material_list(file_path, file_format):
    """
    Analysiert die Datei und gibt ein Dictionary mit {Block-ID: Anzahl} zurück.
    """
    if file_format == "litematica":
        sch = Schematic.load(file_path)
        material_counts = {}
        for region in sch.regions.values():
            unique, counts = np.unique(region._Region__blocks, return_counts=True)
            for idx, count in zip(unique, counts):
                block = region.palette[idx]
                if block.id == "minecraft:air":
                    continue
                name = block.id
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
            if block.id == "minecraft:air":
                continue
            name = block.id
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
