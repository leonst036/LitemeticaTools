import os
import json
import tempfile
import webbrowser
from litemapy import Schematic, Region
import nbtlib

BLOCK_COLORS = {
    "minecraft:stone": "#7d7d7d",
    "minecraft:dirt": "#866043",
    "minecraft:grass_block": "#5e8a39",
    "minecraft:oak_log": "#5c4a21",
    "minecraft:spruce_log": "#3c2a11",
    "minecraft:birch_log": "#dbce9d",
    "minecraft:oak_planks": "#b8945f",
    "minecraft:leaves": "#32591d",
    "minecraft:water": "#2b3bf6",
    "minecraft:lava": "#d65108",
    "minecraft:glass": "#a2c6ce",
    "minecraft:sand": "#dbd3a0",
    "minecraft:cobblestone": "#666666",
    "minecraft:bedrock": "#555555",
    "minecraft:iron_ore": "#888888",
    "minecraft:gold_ore": "#888888",
    "minecraft:diamond_ore": "#888888",
}

def get_block_color(block_id):
    # Einfaches Matching
    for key, color in BLOCK_COLORS.items():
        if key in block_id:
            return color
    
    # Heuristik für bestimmte Kategorien
    if "log" in block_id or "wood" in block_id:
        return "#5c4a21"
    if "planks" in block_id:
        return "#b8945f"
    if "leaves" in block_id:
        return "#32591d"
    if "glass" in block_id:
        return "#a2c6ce"
    if "stone" in block_id or "andesite" in block_id or "diorite" in block_id or "granite" in block_id:
        return "#7d7d7d"
    if "sand" in block_id:
        return "#dbd3a0"
    if "terracotta" in block_id or "concrete" in block_id:
        return "#9e624c"
    
    # Generischer Hash für alle anderen Blöcke
    hash_val = hash(block_id)
    r = (hash_val & 0xFF0000) >> 16
    g = (hash_val & 0x00FF00) >> 8
    b = hash_val & 0x0000FF
    
    # Vermeide zu dunkle/helle Farben
    r = min(max(r, 50), 200)
    g = min(max(g, 50), 200)
    b = min(max(b, 50), 200)
    
    return f"#{r:02x}{g:02x}{b:02x}"

def export_3d_preview(file_path, file_format):
    blocks_data = [] # [x, y, z, color]
    
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
                            blocks_data.append([ox+x, oy+y, oz+z, get_block_color(b.id)])
    elif file_format == "schematica":
        nbt_data = nbtlib.load(file_path)
        region, _ = Region.from_sponge_nbt(nbt_data)
        rx, ry, rz = region.x, region.y, region.z
        for x in range(abs(region.width)):
            for y in range(abs(region.height)):
                for z in range(abs(region.length)):
                    b = region.getblock(x, y, z)
                    if b.id != "minecraft:air":
                        blocks_data.append([rx+x, ry+y, rz+z, get_block_color(b.id)])
                        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>3D Vorschau: {os.path.basename(file_path)}</title>
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #1a1a1a; font-family: sans-serif; }}
            #info {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <div id="info">
            <b>{os.path.basename(file_path)}</b><br>
            Blöcke: {len(blocks_data)}<br>
            Steuerung: Linksklick (Drehen), Rechtsklick (Verschieben), Scrollrad (Zoom)
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const blockData = {json.dumps(blocks_data)};
            
            const scene = new THREE.Scene();
            scene.background = new THREE.Color('#1a1a1a');
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            
            // Licht
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);
            
            // InstancedMesh für Performance
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const material = new THREE.MeshLambertMaterial({{ color: 0xffffff }});
            const instancedMesh = new THREE.InstancedMesh(geometry, material, blockData.length);
            
            // Um das Zentrum zu berechnen
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
            
            const dummy = new THREE.Object3D();
            const color = new THREE.Color();
            
            for (let i = 0; i < blockData.length; i++) {{
                const [x, y, z, hex] = blockData[i];
                
                minX = Math.min(minX, x); minY = Math.min(minY, y); minZ = Math.min(minZ, z);
                maxX = Math.max(maxX, x); maxY = Math.max(maxY, y); maxZ = Math.max(maxZ, z);
                
                dummy.position.set(x, y, z);
                dummy.updateMatrix();
                
                instancedMesh.setMatrixAt(i, dummy.matrix);
                color.set(hex);
                instancedMesh.setColorAt(i, color);
            }}
            
            scene.add(instancedMesh);
            
            // Camera und Controls zentrieren
            const centerX = (minX + maxX) / 2;
            const centerY = (minY + maxY) / 2;
            const centerZ = (minZ + maxZ) / 2;
            
            controls.target.set(centerX, centerY, centerZ);
            camera.position.set(centerX + (maxX - minX) * 0.8, centerY + (maxY - minY) * 0.8 + 10, centerZ + (maxZ - minZ) * 0.8);
            controls.update();
            
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
