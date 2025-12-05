import json
import re
import compas.geometry as cg
from compas_viewer import Viewer
from compas_viewer.scene import Tag

# ==================== COMPAS Geometry Visualization ====================
print("=== COMPAS Geometry Visualization ===", flush=True)

viewer = Viewer()

u = cg.Vector(4, 1, 0)
v = cg.Vector(2, 5, 0)

# Vector Addition and Cross Product
u_p_v = u + v
u_cp_v = u.cross(v)

# Visualize vectors and their operations
viewer.scene.add(u)
viewer.scene.add(v)
viewer.scene.add(u_p_v)
viewer.scene.add(u_cp_v)
viewer.scene.add(Tag("u", u))
viewer.scene.add(Tag("v", v))
viewer.scene.add(Tag("u + v", u_p_v))
viewer.scene.add(Tag("u x v", u_cp_v))

viewer.show()

# ==================== Taichung Road Network Visualization ====================
print("=== Taichung Road Network Visualization ===", flush=True)

try:
    import folium
    use_folium = True
except:
    use_folium = False

# Load taichung_road.json from parent directory
with open('../taichung_road.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def parse_linestring(geometry_str):
    """Parse WKT LINESTRING format"""
    match = re.search(r'\((.*?)\)', geometry_str)
    if not match:
        return None
    coord_str = match.group(1)
    coordinates = []
    for pair in coord_str.split(','):
        lon, lat = pair.strip().split()
        coordinates.append([float(lat), float(lon)])  # folium uses lat,lon
    return coordinates

linestrings = []
for section in data['SectionShapes']:
    coords = parse_linestring(section['Geometry'])
    if coords:
        linestrings.append(coords)

print(f"Loaded {len(linestrings)} road segments", flush=True)

if use_folium:
    # Calculate center for map
    all_lats = []
    all_lons = []
    for coords in linestrings:
        for lat, lon in coords:
            all_lats.append(lat)
            all_lons.append(lon)
    
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    print(f"Creating interactive map centered at ({center_lat}, {center_lon})", flush=True)
    
    # Create folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add all road segments to the map
    for coords in linestrings:
        folium.PolyLine(coords, color='blue', weight=2, opacity=0.7).add_to(m)
    
    # Save interactive map
    output_path = '../assets/taichung_road_map.html'
    print(f"Saving interactive map to {output_path}", flush=True)
    m.save(output_path)
    print(f"✓ Interactive map saved to {output_path}", flush=True)
else:
    # Fallback to matplotlib if folium unavailable
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig = plt.figure(figsize=(14, 12))
    for coords in linestrings:
        lons = [c[1] for c in coords]  # Extract lon
        lats = [c[0] for c in coords]  # Extract lat
        plt.plot(lons, lats, linewidth=1.5, alpha=0.7, color='blue')
    
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    plt.title('Taichung Road Network', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = '../assets/taichung_road_visualization.png'
    print(f"Saving figure to {output_path}", flush=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Static visualization saved to {output_path}", flush=True)
    plt.close()

print("Visualization completed successfully!", flush=True)