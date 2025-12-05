#!/usr/bin/env python3
"""
Merge MRT_amount.json with MRT_position.raw (CSV)
Output: JSON with 欄位名稱, 數值, 經緯度
"""
import json
import csv
from pathlib import Path
from io import StringIO

BASE = Path(__file__).parent / 'data'

# 1. Load MRT_amount.json - extract 欄位名稱 and 數值
print("Loading MRT_amount.json...")
mrt_amount_file = BASE / 'MRT_amount.json'
with mrt_amount_file.open('r', encoding='utf-8') as f:
    mrt_amount_data = json.load(f)

# Create a dict: 欄位名稱 -> 數值
amount_map = {}
for item in mrt_amount_data:
    station_name = item.get('欄位名稱', '')
    value = item.get('數值', '')
    if station_name:
        amount_map[station_name] = value

print(f"Loaded {len(amount_map)} stations from MRT_amount.json")

# 2. Load MRT_position.raw (CSV)
print("Loading MRT_position.raw (CSV)...")
mrt_position_file = BASE / 'MRT_position.raw'
with mrt_position_file.open('r', encoding='utf-8-sig') as f:
    csv_content = f.read()

# Parse CSV
csv_reader = csv.DictReader(StringIO(csv_content))
position_data = []
for row in csv_reader:
    position_data.append(row)

print(f"Loaded {len(position_data)} stations from MRT_position.raw")

# 3. Merge by station name (車站中文)
print("Merging data...")
merged_result = []

for pos_item in position_data:
    station_name = pos_item.get('車站中文', '')
    lat = pos_item.get('緯度', '')
    lon = pos_item.get('經度', '')
    
    # Find matching entry in MRT_amount
    # Try with "站" suffix first, then without
    value = amount_map.get(station_name + '站', '')
    if not value:
        value = amount_map.get(station_name, '')
    
    merged_obj = {
        '欄位名稱': station_name,
        '數值': value,
        '經緯度': f"{lat},{lon}"
    }
    merged_result.append(merged_obj)

print(f"Merged {len(merged_result)} records")

# 4. Save as JSON
output_file = BASE / 'MRT_merged.json'
with output_file.open('w', encoding='utf-8') as f:
    json.dump(merged_result, f, ensure_ascii=False, indent=2)

print(f"Saved to: {output_file}")
print(f"File size: {output_file.stat().st_size:,} bytes")

# Print sample
print("\nSample output:")
for item in merged_result[:3]:
    print(json.dumps(item, ensure_ascii=False))
