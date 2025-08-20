# Xyrus Standalone Deployment

## Repository Structure

This is the standalone Xyrus Mod Agent repository, separated from the main Luanti monorepo.

### Directory Layout
```
xyrus-standalone/
├── app.py              # Main FastAPI application
├── ollama_client.py    # Ollama integration for AI
├── deployer.py         # Mod deployment utilities
├── start_xyrus.sh      # Startup script
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── .gitignore         # Git exclusions
├── static/            # Web interface files
│   ├── index.html     # Main page
│   └── admin.html     # Admin panel
├── forms/             # Xyrus form images and metadata
├── images/            # Additional images
├── history/           # Mod generation history
├── mod_meta/          # Mod metadata
├── trash_mods/        # Deleted mods
└── backups/           # Code backup files
```

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd xyrus-standalone
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama models:**
   ```bash
   ollama pull gpt-oss:20b
   ollama pull gpt-oss:120b  # Optional, for stronger model
   ```

5. **Start Xyrus:**
   ```bash
   ./start_xyrus.sh
   ```

6. **Access the interface:**
   - Main: http://localhost:8088
   - Admin: http://localhost:8088/admin

## Configuration

The application runs on port 8088 by default. You can change this by setting environment variables:

```bash
export PORT=8089
export HOST=127.0.0.1
./start_xyrus.sh
```

## Integration with Luanti/Minetest

If you want to deploy mods to a Luanti/Minetest server, ensure:
1. The server mods directory is accessible
2. Update the paths in `app.py` if needed:
   - `SERVER_MODS_DIR`
   - `WORLD_MT`
   - `MINETEST_LOG`

## Features

- **8 Xyrus Forms**: Dynamic form transformation display
- **Admin Panel**: Complete form management interface
- **Self-Modifying Code**: Xyrus can modify its own code with verification
- **Mod Generation**: Create Luanti/Minetest mods using AI
- **Xyrus TM Laws**: Enforces the ancient laws of Xyrus

## Development

The application uses:
- FastAPI for the backend
- Ollama for AI integration
- Hot-reload enabled in development mode

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security Note

The admin panel is currently not protected by authentication. In production:
1. Add authentication middleware
2. Use HTTPS
3. Restrict access to trusted networks

## License

This project contains the power of Xyrus and is bound by the Xyrus TM Laws.