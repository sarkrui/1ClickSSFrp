#!/usr/bin/env python3
"""
FRP Configuration Generator
Generates frpc configuration files and docker-compose services from frp-servers.json
"""

import json
import os
import sys
from pathlib import Path

def load_config(config_file="frp-servers.json"):
    """Load FRP servers configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {config_file} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing {config_file}: {e}")
        sys.exit(1)

def load_template(template_file="frpc_template.toml"):
    """Load frpc template from file"""
    try:
        with open(template_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {template_file} not found")
        sys.exit(1)

def generate_frpc_toml(server, shadowsocks_config, template):
    """Generate frpc.toml content for a server using template"""
    return template.replace("{LOCATION}", server['name'])

def generate_docker_service(server, docker_config, shadowsocks_config):
    """Generate docker-compose service configuration for a server"""
    service_name = f"frpc-{server['name']}" if server['name'] != 'default' else 'frpc'
    container_name = f"frpc-{server['name']}" if server['name'] != 'default' else 'frpc'
    config_file = f"frpc-{server['name']}.toml" if server['name'] != 'default' else 'frpc.toml'
    
    env_prefix = server['name'].upper() if server['name'] != 'default' else ''
    env_suffix = f"_{env_prefix}" if env_prefix else ''
    
    service = f'''  # {server.get('description', f'{server["name"]} FRP client')}
  {service_name}:
    image: {docker_config['frpc_image']}
    container_name: {container_name}
    restart: {docker_config['restart_policy']}
    network_mode: "{docker_config['network_mode']}"
    environment:
      - FRP_SERVER_ADDR=${{FRP{env_suffix}_SERVER_ADDR:-{server['addr']}}}
      - FRP_SERVER_PORT=${{FRP{env_suffix}_SERVER_PORT:-{server['port']}}}
      - FRP_AUTH_TOKEN=${{FRP{env_suffix}_AUTH_TOKEN:-{server['token']}}}
      - SERVER_PORT=${{SERVER_PORT:-{shadowsocks_config['local_port']}}}
      - FRP_REMOTE_PORT=${{FRP_REMOTE_PORT:-{shadowsocks_config['remote_port']}}}
    volumes:
      - ./{config_file}:/etc/frp/frpc.toml
    command: ["-c", "/etc/frp/frpc.toml"]
    depends_on:
      - shadowsocks
'''
    return service

def generate_env_template(servers, shadowsocks_config):
    """Generate environment variable template"""
    env_content = ["# FRP Multi-Location Environment Variables"]
    env_content.append("# Shadowsocks configuration")
    env_content.append(f"SERVER_PORT={shadowsocks_config['local_port']}")
    env_content.append(f"FRP_REMOTE_PORT={shadowsocks_config['remote_port']}")
    env_content.append("")
    
    for server in servers:
        if not server.get('enabled', True):
            continue
            
        if server['name'] == 'default':
            env_content.append(f"# {server.get('description', 'Default FRP server')}")
            env_content.append(f"# FRP_SERVER_ADDR={server['addr']}")
            env_content.append(f"# FRP_SERVER_PORT={server['port']}")
            env_content.append(f"# FRP_AUTH_TOKEN={server['token']}")
        else:
            env_prefix = server['name'].upper()
            env_content.append(f"# {server.get('description', server['name'] + ' FRP server')}")
            env_content.append(f"FRP_{env_prefix}_SERVER_ADDR={server['addr']}")
            env_content.append(f"FRP_{env_prefix}_SERVER_PORT={server['port']}")
            env_content.append(f"FRP_{env_prefix}_AUTH_TOKEN={server['token']}")
        env_content.append("")
    
    return "\n".join(env_content)

def main():
    print("🚀 Generating FRP configuration files...")
    
    # Load configuration and template
    config = load_config()
    template = load_template()
    servers = [s for s in config['servers'] if s.get('enabled', True)]
    shadowsocks_config = config['shadowsocks']
    docker_config = config['docker']
    
    print(f"📋 Found {len(servers)} enabled servers")
    
    # Generate frpc.toml files
    for server in servers:
        filename = f"frpc-{server['name']}.toml" if server['name'] != 'default' else 'frpc.toml'
        content = generate_frpc_toml(server, shadowsocks_config, template)
        
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✅ Generated {filename}")
    
    # Generate docker-compose.yml completely from config
    print("🔄 Generating docker-compose.yml...")
    
    # Start with shadowsocks service
    new_compose = """services:
  shadowsocks:
    image: shadowsocks/shadowsocks-libev
    container_name: shadowsocks-raw
    restart: always
    network_mode: "host"
    environment:
      - SERVER_PORT=${SERVER_PORT:-""" + str(shadowsocks_config['local_port']) + """}
      - SERVER_ADDR=127.0.0.1
      - METHOD=chacha20-ietf-poly1305
      - PASSWORD=HELLOWORLD

"""
    
    # Add FRP services for each enabled server
    for server in servers:
        service = generate_docker_service(server, docker_config, shadowsocks_config)
        new_compose += service + "\n"
    
    with open("docker-compose.yml", 'w') as f:
        f.write(new_compose)
    print("✅ Generated docker-compose.yml")
    
    # Generate environment template
    env_template = generate_env_template(servers, shadowsocks_config)
    with open(".env.example", 'w') as f:
        f.write(env_template)
    print("✅ Generated .env.example")
    
    print("\n🎉 Configuration generation complete!")
    print(f"\n📋 Generated services: shadowsocks + {len(servers)} FRP clients")
    for server in servers:
        service_name = f"frpc-{server['name']}" if server['name'] != 'default' else 'frpc'
        print(f"   - {service_name} ({server.get('description', server['name'])})")
    print("\n📝 Next steps:")
    print("1. Review and customize the generated files")
    print("2. Copy .env.example to .env and set your values")
    print("3. Run: docker compose up -d")

if __name__ == "__main__":
    main()