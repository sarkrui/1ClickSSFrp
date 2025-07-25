# 1ClickSSFrp - Shadowsocks + FRP Docker Setup

This setup combines Shadowsocks proxy with FRP client to expose your Shadowsocks server through FRP tunneling using Docker containers.

## Quick Start

1. **Configure FRP server connection**:
   Edit `docker compose.yml` and update the environment variables:
   - `FRP_SERVER_ADDR`: Your FRP server IP address (currently: 100.0.0.0)
   - `FRP_SERVER_PORT`: Your FRP server port (default: 7200)
   - `FRP_AUTH_TOKEN`: Your FRP server authentication token
   - `FRP_REMOTE_PORT`: Remote port to expose (default: 50000)

2. **Set Shadowsocks password**:
   Edit `docker compose.yml` and change `PASSWORD=HELLOWORLD` to a secure password.

3. **Start the services**:
   ```bash
   docker compose up -d
   ```

## Architecture

- **shadowsocks service**: Runs shadowsocks-libev with chacha20-ietf-poly1305 encryption
- **frpc service**: FRP client that creates dual TCP/UDP proxies to forward Shadowsocks traffic
- Both services use host networking mode for optimal performance
- FRP client depends on Shadowsocks service for proper startup order

## Configuration Files

### docker compose.yml
- **shadowsocks**: Runs shadowsocks-libev on configurable port (default: 24000)
- **frpc**: Connects to FRP server and exposes shadowsocks port through both TCP and UDP proxies

### frpc.toml
- Uses Go template syntax to inject environment variables
- Creates two proxies: "shadowsocks-tcp" and "shadowsocks-udp"
- Forwards from `127.0.0.1:SS_LOCAL_PORT` to remote port via FRP server
- Uses token-based authentication

## Environment Variables

Configure these in `docker compose.yml`:
- `FRP_SERVER_ADDR`: FRP server IP address
- `FRP_SERVER_PORT`: FRP server port (default: 7200)
- `FRP_AUTH_TOKEN`: Authentication token for FRP server
- `PASSWORD`: Shadowsocks server password
- `SS_LOCAL_PORT`: Local Shadowsocks port (default: 24000)
- `FRP_REMOTE_PORT`: Remote port exposed through FRP (default: 50000)

## Usage

1. Make sure your FRP server is running and accessible
2. Update the environment variables in `docker compose.yml`
3. Run `docker compose up -d` to start both services
4. Connect Shadowsocks clients to `YOUR_FRP_SERVER:FRP_REMOTE_PORT`

## Management Commands

**Start services:**
```bash
docker compose up -d
```

**Stop services:**
```bash
docker compose down
```

**Restart specific service:**
```bash
docker compose restart shadowsocks
docker compose restart frpc
```

**View logs:**
```bash
docker compose logs -f
```

**View specific service logs:**
```bash
docker compose logs -f shadowsocks
docker compose logs -f frpc
```