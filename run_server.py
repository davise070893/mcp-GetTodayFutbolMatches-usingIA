"""
Script principal para ejecutar el servidor MCP de partidos
"""

import sys
import asyncio
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_partidos.server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Servidor MCP detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando el servidor MCP: {e}")
        sys.exit(1)