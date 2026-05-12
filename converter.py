import os
import nbtlib
import numpy as np
from litemapy import Schematic, Region, BlockState

def convert_litematica_to_schematica(input_path, output_path, block_mapping=None):
    sch = Schematic.load(input_path)
    if not sch.regions:
        raise ValueError("Keine Regionen in der Litematica-Datei gefunden.")
    
    # 1. Bounding Box finden (immer, auch bei einer Region, um Mapping einfacher zu machen oder falls Offset nötig)
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for r in sch.regions.values():
        rx, ry, rz = r.x, r.y, r.z
        rw, rh, rl = r.width, r.height, r.length
        if rw < 0: rx += rw; rw = abs(rw)
        if rh < 0: ry += rh; rh = abs(rh)
        if rl < 0: rz += rl; rl = abs(rl)
        min_x = min(min_x, rx); min_y = min(min_y, ry); min_z = min(min_z, rz)
        max_x = max(max_x, rx + rw); max_y = max(max_y, ry + rh); max_z = max(max_z, rz + rl)
        
    width, height, length = int(max_x - min_x), int(max_y - min_y), int(max_z - min_z)
    merged_region = Region(int(min_x), int(min_y), int(min_z), width, height, length)
    
    for r in sch.regions.values():
        rx, ry, rz = r.x, r.y, r.z
        rw, rh, rl = r.width, r.height, r.length
        ox, oy, oz = int(rx - min_x), int(ry - min_y), int(rz - min_z)
        
        for x in range(abs(rw)):
            for y in range(abs(rh)):
                for z in range(abs(rl)):
                    block = r.getblock(x if rw > 0 else -x, y if rh > 0 else -y, z if rl > 0 else -z)
                    if block.id != "minecraft:air":
                        # Block Replacement
                        if block_mapping and block.id in block_mapping:
                            new_block = BlockState(block_mapping[block.id])
                            merged_region.setblock(ox + x, oy + y, oz + z, new_block)
                        else:
                            merged_region.setblock(ox + x, oy + y, oz + z, block)
    
    sponge_nbt = merged_region.to_sponge_nbt()
    sponge_nbt.save(output_path, gzipped=True, byteorder="big")

def convert_schematica_to_litematica(input_path, output_path, block_mapping=None):
    nbt_data = nbtlib.load(input_path)
    region, version = Region.from_sponge_nbt(nbt_data)
    
    if block_mapping:
        # Erstelle eine Kopie der Region mit ersetzten Blöcken
        new_region = Region(region.x, region.y, region.z, region.width, region.height, region.length)
        for x in range(abs(region.width)):
            for y in range(abs(region.height)):
                for z in range(abs(region.length)):
                    block = region.getblock(x, y, z)
                    if block.id != "minecraft:air":
                        if block.id in block_mapping:
                            new_region.setblock(x, y, z, BlockState(block_mapping[block.id]))
                        else:
                            new_region.setblock(x, y, z, block)
        region = new_region

    sch_name = os.path.basename(output_path)
    sch = region.as_schematic(name=sch_name, author="ConverterGUI")
    sch.save(output_path)

def get_schematic_info(file_path, file_format):
    """Gibt Informationen über die Schematic zurück (Dimensionen, Regionen)."""
    try:
        if file_format == "litematica":
            sch = Schematic.load(file_path)
            regions_count = len(sch.regions)
            # Berechne Gesamt-Dimensionen über alle Regionen
            if regions_count == 0:
                return "Keine Regionen", "0"
            
            # Da Litematica Regionen an beliebigen Offsets haben kann, 
            # ist die "Größe" oft die Box, die alle Regionen umschließt.
            return f"{regions_count} Region(en)", "Variable"
            
        elif file_format == "schematica":
            nbt_data = nbtlib.load(file_path)
            # Sponge Schematics haben Width, Height, Length im Root
            width = nbt_data.get('Width', 0)
            height = nbt_data.get('Height', 0)
            length = nbt_data.get('Length', 0)
            return "1 Region (Sponge)", f"{width}x{height}x{length}"
    except:
        return "Unbekannt", "Unbekannt"
    return "Unbekannt", "Unbekannt"
