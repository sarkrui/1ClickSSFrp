# 1ClickSSFrp - Dynamic Multi-Location Shadowsocks + FRP

Dynamic Docker setup that exposes Shadowsocks through multiple FRP servers using JSON configuration.

## Quick Start

1. **Configure servers**:
   Edit `frp-servers.json` to add/remove FRP servers:
   ```json
   {
     "servers": [
       {
         "name": "jp",
         "addr": "your-jp-server.com",
         "port": 7200,
         "token": "your-token",
         "enabled": true,
         "description": "JP FRP server"
       }
     ]
   }
   ```

2. **Generate configuration**:
   ```bash
   python3 generate.py
   ```

3. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual server addresses and tokens
   ```

4. **Start services**:
   ```bash
   docker compose up -d
   ```

## Architecture

- **shadowsocks**: Runs shadowsocks-libev with chacha20-ietf-poly1305 encryption
- **frpc-[location]**: Multiple FRP clients, one per enabled server location
- All services use host networking
- FRP clients expose the same Shadowsocks port through different servers

## Configuration Management

### Core Files
- `frp-servers.json`: Server definitions and settings
- `frpc_template.toml`: Template for generating FRP client configs
- `generate-frp-config.py`: Script that generates all configuration files

### Generated Files
- `frpc-[location].toml`: FRP client configurations
- `docker-compose.yml`: Complete service definitions
- `.env.example`: Environment variable template

## Environment Variables

Set in `.env` file:
- `SERVER_PORT`: Shadowsocks port (default: 24000)
- `FRP_REMOTE_PORT`: Remote port exposed through FRP (default: 50000)
- `FRP_[LOCATION]_SERVER_ADDR`: FRP server address per location
- `FRP_[LOCATION]_SERVER_PORT`: FRP server port per location  
- `FRP_[LOCATION]_AUTH_TOKEN`: Authentication token per location

## Management

**Add/remove servers:**
Edit `frp-servers.json`, then run `python3 generate.py`

**Start all services:**
```bash
docker compose up -d
```

**Start specific location:**
```bash
docker compose up -d frpc-jp
```

**View logs:**
```bash
docker compose logs -f frpc-jp
```

## Usage

Connect Shadowsocks clients to any enabled FRP server:
- JP server: `your-jp-server.com:50000`
- HK server: `your-hk-server.com:50000`