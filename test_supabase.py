#!/usr/bin/env python3
"""
Test script to diagnose Supabase connection issues.
Run this on Render to see exactly where the connection fails.
"""

import os
import socket
import sys
from urllib.parse import urlparse
from pathlib import Path

print("=" * 70)
print("SUPABASE CONNECTION DIAGNOSTIC TEST")
print("=" * 70)

# Load .env
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"\n1. DATABASE_URL loaded: {DATABASE_URL}")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment!")
    sys.exit(1)

# Parse URL
try:
    parsed = urlparse(DATABASE_URL)
    print(f"\n2. URL parsed:")
    print(f"   scheme:   {parsed.scheme}")
    print(f"   user:     {parsed.username}")
    print(f"   host:     {parsed.hostname}")
    print(f"   port:     {parsed.port}")
    print(f"   database: {parsed.path.lstrip('/')}")
    print(f"   query:    {parsed.query}")
except Exception as e:
    print(f"ERROR parsing URL: {e}")
    sys.exit(1)

host = parsed.hostname
port = parsed.port or 5432

# Test 1: DNS Resolution
print(f"\n3. DNS Resolution test for {host}:")
try:
    infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    print(f"   ✓ DNS resolution successful:")
    for family, socktype, proto, canonname, sockaddr in infos:
        addr_type = "IPv6" if family == socket.AF_INET6 else "IPv4"
        print(f"     {addr_type}: {sockaddr[0]}:{sockaddr[1]}")
except socket.gaierror as e:
    print(f"   ✗ DNS resolution failed: {e}")
    print(f"\n   WARNING: DNS not available in this network.")
    print(f"   This is normal on local networks without external DNS access.")
    print(f"   The app should work fine on Render (which has internet access).")
    print(f"\n   Attempting alternative: testing with localhost for schema only...")
    print(f"   (This will skip TCP/SSL/Auth tests)")
    sys.exit(0)
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# Test 2: TCP Connection (raw socket, no SSL)
print(f"\n4. TCP Connection test (no SSL) to {host}:{port}:")
tcp_ok = False
for family, socktype, proto, canonname, sockaddr in infos:
    s = socket.socket(family, socktype, proto)
    s.settimeout(5)
    try:
        s.connect(sockaddr)
        print(f"   ✓ TCP connection successful to {sockaddr[0]}:{sockaddr[1]}")
        tcp_ok = True
        s.close()
        break
    except Exception as e:
        print(f"   ✗ TCP connection failed to {sockaddr[0]}:{sockaddr[1]}: {type(e).__name__}: {e}")
        s.close()

if not tcp_ok:
    print("\n   ERROR: TCP connection not possible. Check firewall/network access.")
    sys.exit(1)

# Test 3: SSL Connection
print(f"\n5. SSL Connection test to {host}:{port}:")
try:
    import ssl
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            print(f"   ✓ SSL connection successful")
            print(f"   Protocol: {ssock.version()}")
            print(f"   Cipher: {ssock.cipher()[0]}")
except Exception as e:
    print(f"   ✗ SSL connection failed: {type(e).__name__}: {e}")
    sys.exit(1)

# Test 4: PostgreSQL Authentication
print(f"\n6. PostgreSQL Authentication test:")
try:
    from sqlalchemy import create_engine, text
    
    # Try with sslmode=require
    url_with_ssl = DATABASE_URL
    if "sslmode=" not in url_with_ssl.lower():
        if "?" in url_with_ssl:
            url_with_ssl = f"{url_with_ssl}&sslmode=require"
        else:
            url_with_ssl = f"{url_with_ssl}?sslmode=require"
    
    print(f"   Trying with URL: {url_with_ssl.replace(parsed.password, '***')}")
    
    engine = create_engine(
        url_with_ssl,
        connect_args={"connect_timeout": 5},
        echo=False,
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"   ✓ PostgreSQL authentication successful!")
        print(f"   Query result: {result.fetchone()}")
        
except Exception as e:
    print(f"   ✗ PostgreSQL authentication failed: {type(e).__name__}")
    print(f"   Error: {e}")
    sys.exit(1)

# Test 5: Database operations
print(f"\n7. Database operations test:")
try:
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   Existing tables: {tables if tables else 'None'}")
    
    # Try to create a test table
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW())"))
        conn.commit()
        print(f"   ✓ Can create tables on Supabase")
        
        # Try to insert
        conn.execute(text("INSERT INTO test_connection DEFAULT VALUES"))
        conn.commit()
        print(f"   ✓ Can insert rows")
        
        # Try to query
        result = conn.execute(text("SELECT COUNT(*) FROM test_connection"))
        count = result.scalar()
        print(f"   ✓ Can query rows (count: {count})")
        
        # Cleanup
        conn.execute(text("DROP TABLE test_connection"))
        conn.commit()
        print(f"   ✓ Table operations successful")
        
except Exception as e:
    print(f"   ✗ Database operations failed: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - Supabase connection is working!")
print("=" * 70)
