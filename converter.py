import os
import nbtlib
from litemapy import Schematic, Region

def convert_litematica_to_schematica(input_path, output_path):
    sch = Schematic.load(input_path)
    if not sch.regions:
        raise ValueError("Keine Regionen in der Litematica-Datei gefunden.")
    
    # Wir konvertieren aktuell nur die erste Region, 
    # da Sponge Schematics standardmäßig nicht multi-regionfähig sind.
    region_name = list(sch.regions.keys())[0]
    region = sch.regions[region_name]
    
    sponge_nbt = region.to_sponge_nbt()
    sponge_nbt.save(output_path, gzipped=True, byteorder="big")

def convert_schematica_to_litematica(input_path, output_path):
    nbt_data = nbtlib.load(input_path)
    
    # from_sponge_nbt gibt ein Tuple (Region, version) zurück
    region, version = Region.from_sponge_nbt(nbt_data)
    
    sch_name = os.path.basename(output_path)
    # Erstelle ein Schematic-Objekt aus der Region
    sch = region.as_schematic(name=sch_name, author="ConverterGUI")
    sch.save(output_path)
