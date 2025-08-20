#!/usr/bin/env python3
"""
Ultra-lightweight web server for Luanti server status
Serves markdown as HTML with auto-refresh
"""

import http.server
import socketserver
import subprocess
import datetime
import sqlite3
import os
from pathlib import Path

PORT = 8080
STATUS_FILE = "/home/tdeshane/luanti/server_status_report.md"
WORLD_PATH = "/var/games/minetest-server/.minetest/worlds/world"

class StatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Generate fresh status
            status_md = self.generate_status()
            
            # Convert markdown to simple HTML
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Luanti Server Status</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ 
            font-family: monospace; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }}
        h1, h2, h3 {{ color: #569cd6; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin: 20px 0;
        }}
        th, td {{ 
            border: 1px solid #444; 
            padding: 8px; 
            text-align: left; 
        }}
        th {{ background: #2d2d2d; }}
        tr:nth-child(even) {{ background: #252525; }}
        code {{ 
            background: #2d2d2d; 
            padding: 2px 4px; 
            border-radius: 3px; 
        }}
        pre {{ 
            background: #2d2d2d; 
            padding: 10px; 
            border-radius: 5px; 
            overflow-x: auto;
        }}
        .alert {{ color: #f48771; }}
        .success {{ color: #4ec9b0; }}
    </style>
</head>
<body>
    <pre>{status_md}</pre>
    <p style="text-align: center; color: #666;">Auto-refreshes every 30 seconds</p>
</body>
</html>"""
            self.wfile.write(html.encode())
        else:
            self.send_error(404)
    
    def generate_status(self):
        """Generate fresh status report"""
        try:
            # Get current time
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get server status
            server_status = "Running" if self.check_server_running() else "Stopped"
            
            # Get player data
            players = self.get_player_data()
            
            # Get world stats
            world_stats = self.get_world_stats()
            
            # Get additional data
            inventories = self.get_inventories()
            map_stats = self.get_map_stats()
            auth_data = self.get_auth_data()
            
            # Build markdown
            md = f"""# Luanti Server Status Report - Complete Database Analysis

**Generated**: {now}
**Server Address**: 192.168.68.145:30000

## 📊 Server Overview

| Metric | Value |
|--------|-------|
| **Server Status** | {server_status} |
| **Game Time** | {world_stats['game_time']:,} seconds |
| **Day Count** | {world_stats['day_count']} days |
| **Time of Day** | {world_stats['time_of_day']} |
| **World Size** | {world_stats['world_size']} MB |
| **Total Blocks** | {map_stats.get('total_blocks', 'Unknown'):,} |

## 👥 Player Statistics & Inventories

| Player | Health | Admin | Key Items |
|--------|--------|-------|-----------|"""
            
            for player in players:
                name = player['name']
                status = "⚠️" if player['hp'] < 10 else "✅"
                is_admin = "👑" if auth_data.get(name, False) else ""
                items = inventories.get(name, "None")
                md += f"\n| {name} {is_admin} | {player['hp']}/20 HP {status} | {is_admin} | {items} |"
            
            md += f"""

## 🗄️ Database Analysis

### players.sqlite ({self.get_file_size(f'{WORLD_PATH}/players.sqlite')} KB)
- 3 registered players with inventories
- Player positions and health tracked
- Custom skins: ToddLLM (character_200), Chelsea (player_cool_guy)

### map.sqlite ({world_stats['world_size']} MB) 
- {map_stats.get('total_blocks', 'Unknown'):,} world blocks
- Average block: {map_stats.get('avg_size', 0):.0f} bytes
- Largest block: {map_stats.get('max_size', 0):,} bytes

### auth.sqlite ({self.get_file_size(f'{WORLD_PATH}/auth.sqlite')} KB)
- Admin users: {', '.join([k for k,v in auth_data.items() if v])}
- Total privileges assigned: 57

## 🎮 Nullifier Adventure Mod

### Entities (60+ registered)
- Bosses: nullifier_enhanced, all_and_all, grimace
- Allies: arixous, arciledeus, friendly_knight
- Enemies: void_titan, skeleton_warrior, zombie_tank

### Items (25+ available)
- Power: admin_remote, jetpack, fire_staff, void_staff
- Materials: void_essence, dragon_heart, nullifier_core

## 🔧 Quick Commands

```bash
# Admin commands (in-game)
/grant <player> all
/giveme nullifier_adventure:admin_remote
/spawnentity nullifier_adventure:nullifier_enhanced
/teleport 0 100 0
```

## 🌐 Web Interfaces
- Basic status: http://{self.get_server_ip()}:8080/
- Management scripts in: /home/tdeshane/luanti/

---
*Auto-refreshes every 30 seconds*"""
            
            return md
            
        except Exception as e:
            return f"Error generating status: {str(e)}"
    
    def check_server_running(self):
        """Check if server is running"""
        try:
            result = subprocess.run(['systemctl', 'is-active', 'minetest-server'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False
    
    def get_player_data(self):
        """Get player data from database"""
        players = []
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/players.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT name, hp FROM player")
            for row in cursor.fetchall():
                players.append({'name': row[0], 'hp': row[1]})
            conn.close()
        except:
            pass
        return players
    
    def get_world_stats(self):
        """Get world statistics"""
        stats = {
            'game_time': 0,
            'day_count': 0,
            'time_of_day': 0,
            'world_size': 0
        }
        
        try:
            # Read env_meta.txt
            with open(f"{WORLD_PATH}/env_meta.txt", 'r') as f:
                for line in f:
                    if line.startswith('game_time'):
                        stats['game_time'] = int(line.split('=')[1].strip())
                    elif line.startswith('day_count'):
                        stats['day_count'] = int(line.split('=')[1].strip())
                    elif line.startswith('time_of_day'):
                        stats['time_of_day'] = int(line.split('=')[1].strip())
            
            # Get world size
            world_size = os.path.getsize(f"{WORLD_PATH}/map.sqlite") / (1024*1024)
            stats['world_size'] = f"{world_size:.1f}"
            
        except:
            pass
        
        return stats
    
    def get_server_ip(self):
        """Get server IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def get_file_size(self, path):
        """Get file size in KB"""
        try:
            return os.path.getsize(path) // 1024
        except:
            return 0
    
    def get_inventories(self):
        """Get player key items summary"""
        inv_summary = {}
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/players.sqlite")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, ii.item_string
                FROM player p
                JOIN player_inventories i ON p.id = i.player_id
                JOIN player_inventory_items ii ON i.id = ii.inventory_id
                WHERE i.type = 'main' AND ii.item_string != ''
            """)
            
            for name, item_string in cursor.fetchall():
                if name not in inv_summary:
                    inv_summary[name] = []
                item_name = item_string.split(' ')[0]
                if 'jetpack' in item_name or 'admin_remote' in item_name or 'staff' in item_name:
                    inv_summary[name].append(item_name.split(':')[-1])
            
            conn.close()
            
            # Format summary
            for name in inv_summary:
                items = inv_summary[name][:3]  # Top 3 items
                inv_summary[name] = ', '.join(items) if items else "Basic items"
                
        except:
            pass
        return inv_summary
    
    def get_map_stats(self):
        """Get map statistics"""
        stats = {}
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/map.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(LENGTH(data)), MAX(LENGTH(data)) FROM blocks")
            row = cursor.fetchone()
            if row:
                stats['total_blocks'] = row[0]
                stats['avg_size'] = row[1] or 0
                stats['max_size'] = row[2] or 0
            conn.close()
        except:
            pass
        return stats
    
    def get_auth_data(self):
        """Check if players are admins"""
        admins = {}
        try:
            conn = sqlite3.connect(f"{WORLD_PATH}/auth.sqlite")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.name 
                FROM auth a
                JOIN user_privileges p ON a.id = p.id
                WHERE p.privilege IN ('server', 'privs')
                GROUP BY a.name
            """)
            for row in cursor.fetchall():
                admins[row[0]] = True
            conn.close()
        except:
            pass
        return admins

def get_lan_ip():
    """Get server IP address (static method)"""
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
with socketserver.TCPServer(("", PORT), StatusHandler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}/")
    print(f"Access from LAN at http://{get_lan_ip()}:{PORT}/")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()