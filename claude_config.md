# Configuración para Claude Desktop - MCP Partidos

Para usar este MCP server con Claude Desktop, agrega la siguiente configuración a tu archivo `claude_desktop_config.json`:

## Ubicación del archivo de configuración:

### Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux:
```
~/.config/Claude/claude_desktop_config.json
```

## Configuración JSON:

```json
{
  "mcpServers": {
    "mcp-partidos": {
      "command": "python",
      "args": [
        "C:\\Users\\davluque\\Documents\\Personales\\Proyectos\\mcp-partidos\\run_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\davluque\\Documents\\Personales\\Proyectos\\mcp-partidos\\src"
      }
    }
  }
}
```

## Para usar con uv (recomendado):

```json
{
  "mcpServers": {
    "mcp-partidos": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\davluque\\Documents\\Personales\\Proyectos\\mcp-partidos",
        "python",
        "run_server.py"
      ]
    }
  }
}
```

## Herramientas disponibles:

1. **obtener_partidos_hoy**: Obtiene todos los partidos programados para hoy
2. **obtener_partidos_fecha**: Obtiene partidos para una fecha específica (YYYY-MM-DD)
3. **listar_fuentes**: Lista todas las fuentes configuradas
4. **probar_fuente**: Prueba si una fuente específica funciona

## Ejemplos de uso en Claude:

```
"Obtén los partidos de fútbol de hoy y muéstrame los 5 más atractivos"

"¿Qué partidos hay el 2025-09-20? Ordénalos por importancia"

"Muéstrame las fuentes configuradas y prueba si ESPN funciona"

"Obtén partidos de hoy y agrúpalos por liga, mostrando horarios en UTC-5"
```