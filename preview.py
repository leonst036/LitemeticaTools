import os
import json
import tempfile
import webbrowser
from litemapy import Schematic, Region
import nbtlib

def export_3d_preview(file_path, file_format):
    blocks_by_id = {}
    
    def add_block(x, y, z, block_id):
        if block_id not in blocks_by_id:
            blocks_by_id[block_id] = []
        blocks_by_id[block_id].append([x, y, z])

    if file_format == "litematica":
        sch = Schematic.load(file_path)
        for r in sch.regions.values():
            rx, ry, rz = r.x, r.y, r.z
            rw, rh, rl = r.width, r.height, r.length
            ox, oy, oz = rx, ry, rz
            
            for x in range(abs(rw)):
                for y in range(abs(rh)):
                    for z in range(abs(rl)):
                        b = r.getblock(x if rw > 0 else -x, y if rh > 0 else -y, z if rl > 0 else -z)
                        if b.id != "minecraft:air":
                            add_block(ox+x, oy+y, oz+z, b.id)
    elif file_format == "schematica":
        nbt_data = nbtlib.load(file_path)
        region, _ = Region.from_sponge_nbt(nbt_data)
        rx, ry, rz = region.x, region.y, region.z
        for x in range(abs(region.width)):
            for y in range(abs(region.height)):
                for z in range(abs(region.length)):
                    b = region.getblock(x, y, z)
                    if b.id != "minecraft:air":
                        add_block(rx+x, ry+y, rz+z, b.id)
                        
    total_blocks = sum(len(positions) for positions in blocks_by_id.values())
                        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>3D Vorschau: {os.path.basename(file_path)}</title>
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #87CEEB; font-family: sans-serif; }}
            #info {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <div id="info">
            <b>{os.path.basename(file_path)}</b><br>
            Blöcke: {total_blocks}<br>
            Steuerung: Linksklick (Drehen), Rechtsklick (Verschieben), Scrollrad (Zoom)<br>
            <i>Hinweis: Texturen werden aus dem Internet geladen.</i>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const blockData = {json.dumps(blocks_by_id)};
            const baseUrl = "https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/1.19.2/assets/minecraft/textures/block/";
            
            const scene = new THREE.Scene();
            scene.background = new THREE.Color('#87CEEB');
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambientLight);
            
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);
            
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const textureLoader = new THREE.TextureLoader();
            
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
            
            const dummy = new THREE.Object3D();
            
            Object.keys(blockData).forEach(blockId => {{
                const positions = blockData[blockId];
                
                let name = blockId.replace("minecraft:", "");
                
                // Exakte Textur-Mappings für komplexe Blöcke
                const exact = {{
                    "grass_block": "grass_block_side",
                    "podzol": "podzol_side",
                    "mycelium": "mycelium_side",
                    "snow": "snow",
                    "dirt_path": "dirt_path_side",
                    "water": "water_still",
                    "lava": "lava_still",
                    "fire": "fire_0",
                    "chest": "oak_planks",
                    "trapped_chest": "oak_planks",
                    "ender_chest": "obsidian",
                    "furnace": "furnace_front",
                    "crafting_table": "crafting_table_front",
                    "dispenser": "dispenser_front",
                    "dropper": "dropper_front",
                    "observer": "observer_front",
                    "piston": "piston_side",
                    "sticky_piston": "piston_side",
                    "pumpkin": "pumpkin_side",
                    "carved_pumpkin": "pumpkin_side",
                    "jack_o_lantern": "jack_o_lantern",
                    "melon": "melon_side",
                    "hay_block": "hay_block_side",
                    "bookshelf": "bookshelf",
                    "loom": "loom_side",
                    "composter": "composter_side",
                    "barrel": "barrel_side",
                    "smoker": "smoker_front",
                    "blast_furnace": "blast_furnace_front",
                    "cartography_table": "cartography_table_side2",
                    "fletching_table": "fletching_table_side",
                    "smithing_table": "smithing_table_side",
                    "grindstone": "stone", 
                    "lectern": "lectern_side",
                    "stonecutter": "stonecutter_side",
                    "campfire": "campfire_log_lit",
                    "soul_campfire": "campfire_log_lit",
                    "bee_nest": "bee_nest_side",
                    "beehive": "beehive_side",
                    "wall_torch": "torch",
                    "soul_wall_torch": "soul_torch",
                    "redstone_wall_torch": "redstone_torch",
                    "redstone_wire": "redstone_dust_dot",
                    "glass_pane": "glass",
                    "tall_grass": "tall_grass_top",
                    "seagrass": "seagrass",
                    "tall_seagrass": "tall_seagrass_top",
                    "cake": "cake_side",
                    "iron_door": "iron_block",
                    "iron_trapdoor": "iron_block"
                }};

                if (exact[name]) {{
                    name = exact[name];
                }} else {{
                    // Regex Heuristiken für Treppen, Stufen, Zäune, etc.
                    name = name.replace("wall_banner", "banner")
                               .replace("wall_sign", "sign")
                               .replace(/_pane$/, "")
                               .replace(/_bed$/, "_wool")
                               .replace(/_stairs$/, "")
                               .replace(/_slab$/, "")
                               .replace(/_fence_gate$/, "")
                               .replace(/_fence$/, "")
                               .replace(/_wall$/, "")
                               .replace(/^potted_/, "")
                               .replace(/_door$/, "_planks")
                               .replace(/_trapdoor$/, "_planks")
                               .replace(/_button$/, "_planks")
                               .replace(/_pressure_plate$/, "");
                }}
                
                // Holzarten zu Planken weiterleiten (da "oak" keine Textur ist, sondern "oak_planks")
                const woods = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "crimson", "warped"];
                if (woods.includes(name)) name += "_planks";
                if (name === "stone_brick") name = "stone_bricks";
                if (name === "red_nether_brick") name = "red_nether_bricks";
                if (name === "mossy_stone_brick") name = "mossy_stone_bricks";
                
                const material = new THREE.MeshLambertMaterial({{ 
                    color: 0xffffff,
                    transparent: true,
                    alphaTest: 0.1 
                }});
                
                const textureUrl = baseUrl + name + ".png";
                
                textureLoader.load(
                    textureUrl,
                    function (texture) {{
                        texture.magFilter = THREE.NearestFilter;
                        texture.minFilter = THREE.NearestFilter;
                        material.map = texture;
                        material.needsUpdate = true;
                    }},
                    undefined,
                    function (err) {{
                        // Besserer Fallback: Eindeutige Farbe berechnen
                        let hash = 0;
                        for (let i = 0; i < blockId.length; i++) hash = blockId.charCodeAt(i) + ((hash << 5) - hash);
                        hash = Math.abs(hash);
                        const r = (hash & 0xFF0000) >> 16;
                        const g = (hash & 0x00FF00) >> 8;
                        const b = hash & 0x0000FF;
                        material.color.setRGB(
                            Math.max(50, Math.min(200, r)) / 255,
                            Math.max(50, Math.min(200, g)) / 255,
                            Math.max(50, Math.min(200, b)) / 255
                        );
                        material.map = null;
                        material.needsUpdate = true;
                    }}
                );
                
                const instancedMesh = new THREE.InstancedMesh(geometry, material, positions.length);
                for (let i = 0; i < positions.length; i++) {{
                    const [x, y, z] = positions[i];
                    minX = Math.min(minX, x); minY = Math.min(minY, y); minZ = Math.min(minZ, z);
                    maxX = Math.max(maxX, x); maxY = Math.max(maxY, y); maxZ = Math.max(maxZ, z);
                    
                    dummy.position.set(x, y, z);
                    dummy.updateMatrix();
                    instancedMesh.setMatrixAt(i, dummy.matrix);
                }}
                scene.add(instancedMesh);
            }});
            
            if (minX !== Infinity) {{
                const centerX = (minX + maxX) / 2;
                const centerY = (minY + maxY) / 2;
                const centerZ = (minZ + maxZ) / 2;
                
                controls.target.set(centerX, centerY, centerZ);
                camera.position.set(centerX + (maxX - minX) * 0.8, centerY + (maxY - minY) * 0.8 + 10, centerZ + (maxZ - minZ) * 0.8);
                controls.update();
            }}
            
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
            
            function animate() {{
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
            }}
            
            animate();
        </script>
    </body>
    </html>
    """
    
    fd, path = tempfile.mkstemp(suffix=".html", prefix="schematic_preview_")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    webbrowser.open('file://' + os.path.realpath(path))
