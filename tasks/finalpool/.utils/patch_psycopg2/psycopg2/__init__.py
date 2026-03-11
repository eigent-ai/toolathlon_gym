
import os
import sys

# Use an environment variable as a global re-entrancy flag
# This works across multiple module loads in the same process
REENTRANCY_VAR = "_PSYCOPG2_PATCH_ACTIVE"

# Get the directory where THIS patched __init__.py lives
PATCH_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Temporarily remove PATCH_ROOT from sys.path to import the REAL psycopg2
original_path = sys.path[:]
if PATCH_ROOT in sys.path:
    sys.path.remove(PATCH_ROOT)

try:
    import psycopg2 as real_psycopg2
finally:
    # Restore original path
    sys.path = original_path

# Override the connect function
def connect(*args, **kwargs):
    if os.environ.get(REENTRANCY_VAR) == "1":
        return real_psycopg2.connect(*args, **kwargs)
    
    os.environ[REENTRANCY_VAR] = "1"
    try:
        # Override with environment variables if present
        if "dbname" in kwargs:
            kwargs["dbname"] = os.environ.get("PGDATABASE", kwargs["dbname"])
        if "host" in kwargs:
            kwargs["host"] = os.environ.get("PGHOST", kwargs["host"])
        if "port" in kwargs:
            env_port = os.environ.get("PGPORT")
            if env_port:
                kwargs["port"] = int(env_port)
        if "user" in kwargs:
            kwargs["user"] = os.environ.get("PGUSER", kwargs["user"])
        if "password" in kwargs:
            kwargs["password"] = os.environ.get("PGPASSWORD", kwargs["password"])
        
        return real_psycopg2.connect(*args, **kwargs)
    finally:
        del os.environ[REENTRANCY_VAR]

# Proxy everything else
for attr in dir(real_psycopg2):
    if not attr.startswith('__'):
        globals()[attr] = getattr(real_psycopg2, attr)

# Ensure our connect is the one being used
globals()['connect'] = connect
