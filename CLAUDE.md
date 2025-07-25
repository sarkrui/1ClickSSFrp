# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker-based setup that combines Shadowsocks proxy with FRP (Fast Reverse Proxy) client to expose a Shadowsocks server through FRP tunneling. The project consists of minimal configuration files for a containerized deployment.

## Architecture

- **shadowsocks service**: Runs shadowsocks-libev container with chacha20-ietf-poly1305 encryption
- **frpc service**: FRP client that connects to an external FRP server and forwards the Shadowsocks port (both TCP and UDP)
- Both services use `network_mode: "host"` for direct host networking
- FRP client depends on shadowsocks service startup order

## Key Configuration Files

- `docker-compose.yml`: Defines both services with environment variables for FRP server connection and Shadowsocks password
- `frpc.toml`: FRP client configuration using Go template syntax with environment variables for server connection and dual proxy rules (TCP/UDP)

## Common Commands

**Start services:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**View specific service logs:**
```bash
docker-compose logs -f shadowsocks
docker-compose logs -f frpc
```

**Restart specific service:**
```bash
docker-compose restart shadowsocks
docker-compose restart frpc
```

## Environment Variables

Critical variables in `docker-compose.yml`:
- `FRP_SERVER_ADDR`: FRP server IP address (currently set to 100.0.0.0)
- `FRP_SERVER_PORT`: FRP server port (default: 7200)  
- `FRP_AUTH_TOKEN`: Authentication token for FRP server connection
- `PASSWORD`: Shadowsocks server password (currently: HELLOWORLD)
- `SS_LOCAL_PORT`: Local Shadowsocks port (default: 24000)
- `FRP_REMOTE_PORT`: Remote port exposed through FRP (default: 50009)

## Port Configuration

- Local Shadowsocks port: 24000 (configurable via SS_LOCAL_PORT)
- Remote exposed port through FRP: 50009 (configurable via FRP_REMOTE_PORT)
- FRP server connection port: 7200 (configurable via FRP_SERVER_PORT)

## FRP Configuration Details

The `frpc.toml` uses Go template syntax to inject environment variables:
- Creates two proxies: "shadowsocks-tcp" and "shadowsocks-udp"
- Both proxies forward from `127.0.0.1:SS_LOCAL_PORT` to `remotePort`
- Authentication via token-based method