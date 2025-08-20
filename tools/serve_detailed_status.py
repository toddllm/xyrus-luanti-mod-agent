#!/usr/bin/env python3
"""
Enhanced Luanti server status viewer with full database exploration
"""

import http.server
import socketserver
import subprocess
import datetime
import sqlite3
import os
import json
import base64
import struct

PORT = 8081
WORLD_PATH = "/var/games/minetest-server/.minetest/worlds/world"

class DetailedStatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self.generate_detailed_html()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)
    
    def generate_detailed_html(self):
        """Generate comprehensive HTML report"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Gather all data
        server_status = self.check_server_running()
        world_stats = self.get_world_stats()
        player_data = self.get_detailed_player_data()
        inventory_data = self.get_all_inventories()
        auth_data = self.get_auth_data()
        mod_storage = self.get_mod_storage()
        map_stats = self.get_map_statistics()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Luanti Server - Detailed Status</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="60">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #0f0f0f;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        h1 {{ color: #4fc3f7; border-bottom: 2px solid #4fc3f7; padding-bottom: 10px; }}
        h2 {{ color: #81c784; margin-top: 30px; }}
        h3 {{ color: #ffb74d; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 15px 0;
            background: #1a1a1a;
            border: 1px solid #333;
        }}
        th, td {{ 
            border: 1px solid #333; 
            padding: 10px; 
            text-align: left; 
        }}
        th {{ 
            background: #2a2a2a; 
            color: #4fc3f7;
            font-weight: 600;
        }}
        tr:nth-child(even) {{ background: #222; }}
        tr:hover {{ background: #2a2a2a; }}
        .stat-card {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .health-bar {{
            background: #333;
            border-radius: 4px;
            height: 20px;
            position: relative;
            overflow: hidden;
        }}
        .health-fill {{
            background: linear-gradient(90deg, #f44336, #ffeb3b, #4caf50);
            height: 100%;
            transition: width 0.3s;
        }}
        .item {{ 
            display: inline-block; 
            background: #2a2a2a; 
            padding: 4px 8px; 
            margin: 2px; 
            border-radius: 4px;
            border: 1px solid #444;
            font-size: 0.9em;
        }}
        .privilege {{
            display: inline-block;
            background: #1976d2;
            color: white;
            padding: 2px 6px;
            margin: 2px;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        .admin {{ background: #d32f2f; }}
        .status-online {{ color: #4caf50; font-weight: bold; }}
        .status-offline {{ color: #f44336; font-weight: bold; }}
        code {{ 
            background: #2a2a2a; 
            padding: 2px 6px; 
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .section {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>🎮 Luanti Server - Detailed Database Analysis</h1>
    
    <div class="section">
        <h2>📊 Server Overview</h2>
        <div class="grid">
            <div class="stat-card">
                <h3>Server Status</h3>
                <p class="{'status-online' if server_status else 'status-offline'}">
                    {'● ONLINE' if server_status else '○ OFFLINE'}
                </p>
                <p>Address: <code>192.168.68.145:30000</code></p>
            </div>
            <div class="stat-card">
                <h3>World Statistics</h3>
                <p>Game Time: <strong>{world_stats['game_time']:,}</strong> seconds</p>
                <p>Day Count: <strong>{world_stats['day_count']}</strong> days</p>
                <p>World Size: <strong>{world_stats['world_size']}</strong> MB</p>
            </div>
            <div class="stat-card">
                <h3>Map Database</h3>
                <p>Total Blocks: <strong>{map_stats['total_blocks']:,}</strong></p>
                <p>Avg Block Size: <strong>{map_stats['avg_size']:.1f}</strong> bytes</p>
                <p>Largest Block: <strong>{map_stats['max_size']:,}</strong> bytes</p>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>👥 Player Details</h2>
        {self.generate_player_html(player_data, inventory_data, auth_data)}
    </div>

    <div class="section">
        <h2>🎒 Complete Inventory Analysis</h2>
        {self.generate_inventory_html(inventory_data)}
    </div>

    <div class="section">
        <h2>🔐 Authentication & Privileges</h2>
        {self.generate_auth_html(auth_data)}
    </div>

    <div class="section">
        <h2>💾 Mod Storage Data</h2>
        {self.generate_mod_storage_html(mod_storage)}
    </div>

    <div class="section">
        <h2>🗺️ World Map Analysis</h2>
        {self.generate_map_analysis_html(map_stats)}
    </div>

    <footer style="text-align: center; color: #666; margin-top: 50px;">
        <p>Generated: {now} | Auto-refreshes every 60 seconds</p>
        <p>Luanti Server Database Explorer v2.0</p>
    </footer>
</body>
</html>"""
        return html
    
    def generate_player_html(self, players, inventories, auth):
        """Generate player details HTML"""
        html = "<div class='grid'>"
        
        for player in players:
            name = player['name']
            health_percent = (player['hp'] / 20) * 100
            
            # Get privileges for this player
            privs = auth.get(name, {}).get('privileges', [])
            is_admin = 'server' in privs or 'privs' in privs
            
            html += f"""
            <div class="stat-card">
                <h3>{name} {'👑' if is_admin else ''}</h3>
                <p>Health: {player['hp']}/20 HP</p>
                <div class="health-bar">
                    <div class="health-fill" style="width: {health_percent}%"></div>
                </div>
                <p>Position: ({player['posx']:.1f}, {player['posy']:.1f}, {player['posz']:.1f})</p>
                <p>Breath: {player['breath']}/10</p>
                <p>Last seen: {player.get('modification_date', 'Unknown')}</p>
            </div>
            """
        
        html += "</div>"
        return html
    
    def generate_inventory_html(self, inventories):
        """Generate inventory details HTML"""
        html = ""
        
        for player_name, inv_data in inventories.items():
            html += f"<h3>{player_name}'s Inventory</h3>"
            html += "<table><tr><th>Type</th><th>Slot</th><th>Item</th><th>Count</th><th>Wear</th></tr>"
            
            for item in inv_data:
                html += f"""<tr>
                    <td>{item['inv_type']}</td>
                    <td>{item['slot_id']}</td>
                    <td><span class='item'>{item['name']}</span></td>
                    <td>{item['count']}</td>
                    <td>{item['wear']}</td>
                </tr>"""
            
            html += "</table>"
        
        return html
    
    def generate_auth_html(self, auth_data):
        """Generate authentication HTML"""
        html = "<table><tr><th>Player</th><th>ID</th><th>Privileges</th><th>Admin</th></tr>"
        
        for name, data in auth_data.items():
            privs = data['privileges']
            is_admin = 'server' in privs or 'privs' in privs
            
            priv_html = ""
            for priv in sorted(privs):
                css_class = "privilege admin" if priv in ['server', 'privs', 'give', 'ban'] else "privilege"
                priv_html += f"<span class='{css_class}'>{priv}</span>"
            
            html += f"""<tr>
                <td><strong>{name}</strong></td>
                <td>{data['id']}</td>
                <td>{priv_html}</td>
                <td>{'✓' if is_admin else '✗'}</td>
            </tr>"""
        
        html += "</table>"
        return html
    
    def generate_mod_storage_html(self, storage):
        """Generate mod storage HTML"""
        if not storage:
            return "<p>No mod storage data found.</p>"
        
        html = "<table><tr><th>Mod</th><th>Key</th><th>Value</th></tr>"
        
        for item in storage:
            html += f"""<tr>
                <td>{item['modname']}</td>
                <td><code>{item['key']}</code></td>
                <td>{item['value'][:100]}{'...' if len(item['value']) > 100 else ''}</td>
            </tr>"""
        
        html += "</table>"
        return html
    
    def generate_map_analysis_html(self, map_stats):
        """Generate map analysis HTML"""
        html = f"""
        <div class="grid">
            <div class="stat-card">
                <h3>Block Statistics</h3>
                <p>Total Blocks: <strong>{map_stats['total_blocks']:,}</strong></p>
                <p>Total Data Size: <strong>{map_stats['total_size'] / 1024 / 1024:.1f} MB</strong></p>
                <p>Average Block: <strong>{map_stats['avg_size']:.1f} bytes</strong></p>
                <p>Smallest Block: <strong>{map_stats['min_size']} bytes</strong></p>
                <p>Largest Block: <strong>{map_stats['max_size']:,} bytes</strong></p>
            </div>
            <div class="stat-card">
                <h3>World Boundaries</h3>
                <p>X Range: {map_stats['x_range'][0]} to {map_stats['x_range'][1]}</p>
                <p>Y Range: {map_stats['y_range'][0]} to {map_stats['y_range'][1]}</p>
                <p>Z Range: {map_stats['z_range'][0]} to {map_stats['z_range'][1]}</p>
                <p>World Volume: {map_stats['volume']:,} blocks³</p>
            </div>
        </div>
        
        <h3>Largest Blocks (Likely Complex Areas)</h3>
        <table>
            <tr><th>Position</th><th>Coordinates</th><th>Size</th><th>Note</th></tr>
        """
        
        for block in map_stats['largest_blocks']:
            note = "Very complex" if block['size'] > 2000 else "Complex" if block['size'] > 1000 else "Normal"
            html += f"""<tr>
                <td><code>{block['pos']}</code></td>
                <td>({block['x']}, {block['y']}, {block['z']})</td>
                <td>{block['size']:,} bytes</td>
                <td>{note}</td>
            </tr>"""
        
        html += "</table>"
        return html
    
    # Database query methods
    def check_server_running(self):
        try:
            result = subprocess.run(['systemctl', 'is-active', 'minetest-server'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False
    
    def get_world_stats(self):
        stats = {
            'game_time': 0,
            'day_count': 0,
            'time_of_day': 0,
            'world_size': 0
        }
        
        try:
            with open(f"{WORLD_PATH}/env_meta.txt", 'r') as f:
                for line in f:
                    if line.startswith('game_time'):
                        stats['game_time'] = int(line.split('=')[1].strip())
                    elif line.startswith('day_count'):
                        stats['day_count'] = int(line.split('=')[1].strip())
                    elif line.startswith('time_of_day'):
                        stats['time_of_day'] = int(line.split('=')[1].strip())
            
            world_size = os.path.getsize(f"{WORLD_PATH}/map.sqlite") / (1024*1024)
            stats['world_size'] = f"{world_size:.1f}"
        except:
            pass
        
        return stats
    
    def get_detailed_player_data(self):
        players = []
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/players.sqlite")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, pitch, yaw, posx, posy, posz, 
                       hp, breath, creation_date, modification_date 
                FROM player
            """)
            for row in cursor.fetchall():
                players.append({
                    'name': row[0],
                    'pitch': row[1],
                    'yaw': row[2],
                    'posx': row[3],
                    'posy': row[4],
                    'posz': row[5],
                    'hp': row[6],
                    'breath': row[7],
                    'creation_date': row[8],
                    'modification_date': row[9]
                })
            conn.close()
        except Exception as e:
            print(f"Error getting player data: {e}")
        return players
    
    def get_all_inventories(self):
        inventories = {}
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/players.sqlite")
            cursor = conn.cursor()
            
            # Get all inventory items
            cursor.execute("""
                SELECT p.name, i.type, ii.slot_id, ii.item_string
                FROM player p
                JOIN player_inventories i ON p.id = i.player_id
                JOIN player_inventory_items ii ON i.id = ii.inventory_id
                ORDER BY p.name, i.type, ii.slot_id
            """)
            
            for row in cursor.fetchall():
                player_name = row[0]
                if player_name not in inventories:
                    inventories[player_name] = []
                
                # Parse item string
                item_parts = row[3].split(' ')
                item_name = item_parts[0] if item_parts else "empty"
                item_count = int(item_parts[1]) if len(item_parts) > 1 else 1
                item_wear = int(item_parts[2]) if len(item_parts) > 2 else 0
                
                if item_name and item_name != "":
                    inventories[player_name].append({
                        'inv_type': row[1],
                        'slot_id': row[2],
                        'name': item_name,
                        'count': item_count,
                        'wear': item_wear
                    })
            
            conn.close()
        except Exception as e:
            print(f"Error getting inventory data: {e}")
        return inventories
    
    def get_auth_data(self):
        auth_data = {}
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/auth.sqlite")
            cursor = conn.cursor()
            
            # Get all users
            cursor.execute("SELECT id, name FROM auth")
            users = cursor.fetchall()
            
            for user_id, name in users:
                auth_data[name] = {'id': user_id, 'privileges': []}
                
                # Get privileges
                cursor.execute("""
                    SELECT privilege FROM user_privileges 
                    WHERE id = ?
                """, (user_id,))
                
                for row in cursor.fetchall():
                    auth_data[name]['privileges'].append(row[0])
            
            conn.close()
        except Exception as e:
            print(f"Error getting auth data: {e}")
        return auth_data
    
    def get_mod_storage(self):
        storage = []
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/mod_storage.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT modname, key, value FROM entries")
            
            for row in cursor.fetchall():
                storage.append({
                    'modname': row[0],
                    'key': row[1],
                    'value': row[2]
                })
            
            conn.close()
        except Exception as e:
            print(f"Error getting mod storage: {e}")
        return storage
    
    def get_map_statistics(self):
        stats = {
            'total_blocks': 0,
            'total_size': 0,
            'min_size': float('inf'),
            'max_size': 0,
            'avg_size': 0,
            'largest_blocks': [],
            'x_range': [float('inf'), float('-inf')],
            'y_range': [float('inf'), float('-inf')],
            'z_range': [float('inf'), float('-inf')],
            'volume': 0
        }
        
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/map.sqlite")
            cursor = conn.cursor()
            
            # Get basic statistics
            cursor.execute("SELECT COUNT(*), SUM(LENGTH(data)), MIN(LENGTH(data)), MAX(LENGTH(data)), AVG(LENGTH(data)) FROM blocks")
            row = cursor.fetchone()
            if row:
                stats['total_blocks'] = row[0]
                stats['total_size'] = row[1] or 0
                stats['min_size'] = row[2] or 0
                stats['max_size'] = row[3] or 0
                stats['avg_size'] = row[4] or 0
            
            # Get largest blocks
            cursor.execute("SELECT pos, LENGTH(data) as size FROM blocks ORDER BY size DESC LIMIT 10")
            for row in cursor.fetchall():
                pos = row[0]
                # Decode position (simplified)
                x = (pos % 4096) - 2048
                y = ((pos // 4096) % 4096) - 2048
                z = (pos // (4096 * 4096)) - 2048
                
                stats['largest_blocks'].append({
                    'pos': pos,
                    'size': row[1],
                    'x': x * 16,
                    'y': y * 16,
                    'z': z * 16
                })
                
                # Update ranges
                stats['x_range'][0] = min(stats['x_range'][0], x * 16)
                stats['x_range'][1] = max(stats['x_range'][1], x * 16)
                stats['y_range'][0] = min(stats['y_range'][0], y * 16)
                stats['y_range'][1] = max(stats['y_range'][1], y * 16)
                stats['z_range'][0] = min(stats['z_range'][0], z * 16)
                stats['z_range'][1] = max(stats['z_range'][1], z * 16)
            
            # Calculate world volume
            if stats['x_range'][0] != float('inf'):
                x_size = stats['x_range'][1] - stats['x_range'][0]
                y_size = stats['y_range'][1] - stats['y_range'][0]
                z_size = stats['z_range'][1] - stats['z_range'][0]
                stats['volume'] = (x_size * y_size * z_size) // (16 * 16 * 16)
            
            conn.close()
        except Exception as e:
            print(f"Error getting map statistics: {e}")
        
        return stats

def get_lan_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# Start server
with socketserver.TCPServer(("", PORT), DetailedStatusHandler) as httpd:
    print(f"Enhanced Luanti Database Explorer running at:")
    print(f"  http://localhost:{PORT}/")
    print(f"  http://{get_lan_ip()}:{PORT}/")
    print("\nPress Ctrl+C to stop")
    httpd.serve_forever()