# MCP Partidos de Fútbol ⚽

Un servidor MCP (Model Context Protocol) en Python para obtener datos de partidos de fútbol mediante web scraping inteligente desde múltiples fuentes.

## 🌟 Características

- 🏈 **Múltiples fuentes**: Extrae datos de ESPN, Goal.com, BBC Sport, Marca, AS y más
- 🔄 **URLs configurables**: Fácil modificación y adición de nuevas fuentes
- 📊 **Salida JSON estructurada**: Formato optimizado para procesamiento por IA
- 🚀 **Compatible con MCP**: Integración directa con Claude y otros sistemas de IA
- ⚡ **Scraping asíncrono**: Rendimiento optimizado con requests paralelos
- 🏆 **Detección inteligente**: Identifica automáticamente partidos "atractivos" y equipos grandes
- 🎯 **Filtrado avanzado**: Sistema de scoring para priorizar partidos importantes
- 💾 **Sistema de caché**: Evita requests innecesarios

## 📊 Datos que extrae

- **Equipos**: Nombres completos de equipos locales y visitantes
- **Horarios**: Fecha y hora exacta de los partidos
- **Ligas**: Competición, torneo o liga (Champions, Premier League, etc.)
- **Canales**: Canales de TV/streaming donde se transmite
- **Estadios**: Lugar donde se juega (cuando está disponible)
- **Estado**: Programado, en vivo, finalizado
- **Marcadores**: Resultados en tiempo real (cuando disponible)
- **Nivel de atractivo**: Score 1-5 basado en importancia de equipos y liga

## 🚀 Instalación rápida

### Opción 1: Con uv (recomendado)
```bash
# Instalar uv si no lo tienes
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clonar e instalar
git clone <repo-url>
cd mcp-partidos
uv venv
uv pip install -r requirements.txt
```

### Opción 2: Con pip tradicional
```bash
git clone <repo-url>
cd mcp-partidos
pip install -r requirements.txt
```

## ⚙️ Configuración

### 1. Configurar fuentes
Edita `src/mcp_partidos/config.py` para agregar o modificar fuentes:

```python
FUENTES_PARTIDOS = [
    "https://www.espn.com/soccer/fixtures",
    "https://www.goal.com/fixtures", 
    "https://www.bbc.com/sport/football/fixtures",
    "https://www.marca.com/futbol/fixture.html",
    # Agrega más fuentes aquí
]
```

### 2. Configurar equipos importantes
Personaliza la lista de equipos "grandes" para el sistema de scoring:

```python
EQUIPOS_GRANDES = [
    "Real Madrid", "Barcelona", "Manchester United", 
    "Liverpool", "Bayern Munich", "PSG",
    # Agrega más equipos aquí
]
```

## 🎮 Uso

### Como servidor MCP (con Claude)
1. Configurar en `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-partidos": {
      "command": "uv",
      "args": ["run", "--directory", "/ruta/a/mcp-partidos", "python", "run_server.py"]
    }
  }
}
```

2. En Claude:
```
"Obtén los partidos de fútbol de hoy y muéstrame los 5 más atractivos ordenados por importancia"
```

### Como script independiente
```bash
# Ejecutar servidor MCP
python run_server.py

# Probar el scraper con todas las fuentes
python test_scraper.py

# Probar una fuente específica
python test_scraper.py "https://www.espn.com/soccer/fixtures"

# Menú interactivo para probar fuentes (recomendado)
python probar_nueva_fuente.py
```

## 🛠️ Herramientas MCP disponibles

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `obtener_partidos_hoy` | Obtiene partidos programados para hoy | `incluir_fuentes` (bool) |
| `obtener_partidos_fecha` | Obtiene partidos para fecha específica | `fecha` (YYYY-MM-DD), `incluir_fuentes` (bool) |
| `listar_fuentes` | Lista todas las fuentes configuradas | - |
| `probar_fuente` | Verifica si una fuente funciona | `url` (string) |

## 📋 Formato de salida JSON

```json
{
  "partidos": [
    {
      "equipo_local": "Barcelona",
      "equipo_visitante": "Real Madrid", 
      "fecha": "2025-09-19",
      "hora": "15:00",
      "liga": "La Liga",
      "canales": ["ESPN", "Movistar+"],
      "estadio": "Camp Nou",
      "estado": "programado",
      "fuente": {
        "nombre": "espn.com",
        "url": "https://www.espn.com/soccer/fixtures"
      },
      "metadatos": {
        "es_partido_importante": true,
        "nivel_atractivo": 5,
        "fecha_extraccion": "2025-09-19T10:30:00Z"
      }
    }
  ],
  "fecha_consulta": "2025-09-19",
  "total_partidos": 15,
  "fuentes_consultadas": 6,
  "timestamp": "2025-09-19T10:30:00Z",
  "estadisticas": {
    "por_liga": {
      "Champions League": 4,
      "Premier League": 6,
      "La Liga": 5
    },
    "partidos_importantes": 8,
    "nivel_atractivo_promedio": 3.2
  }
}
```

## 🎯 Ejemplos de uso con Claude

```
# Partidos de hoy con análisis
"Obtén los partidos de fútbol de hoy, ordénalos por atractivo y dime cuáles son los 3 mejores para ver"

# Partidos por fecha
"¿Qué partidos hay el 2025-12-25? Muéstrame solo los de ligas europeas importantes"

# Análisis de fuentes
"Lista las fuentes configuradas y prueba ESPN para ver si funciona bien"

# Partidos por horario
"Obtén partidos de hoy y agrúpalos por franja horaria, mostrando horarios en UTC-5"

# Análisis por liga
"Dame partidos de hoy y dime cuántos hay por liga, priorizando Champions League"
```

## 🔧 Desarrollo y testing

```bash
# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"

# Formatear código
uv run black src/

# Verificar tipos con mypy
uv run mypy src/

# Probar scraper completo (todas las fuentes)
uv run python test_scraper.py

# Probar fuente específica
uv run python test_scraper.py "https://www.espn.com/soccer/fixtures"

# Menú interactivo para probar fuentes
uv run python probar_nueva_fuente.py

# Ejecutar servidor MCP
uv run python run_server.py
```

## 📁 Estructura del proyecto

```
mcp-partidos/
├── src/
│   └── mcp_partidos/
│       ├── __init__.py
│       ├── server.py          # Servidor MCP principal
│       ├── scraper.py         # Lógica de web scraping
│       ├── config.py          # Configuración de URLs y equipos
│       └── models.py          # Modelos de datos (Partido, etc.)
├── run_server.py              # Script para ejecutar el servidor
├── test_scraper.py            # Script de prueba del scraper
├── claude_config.md           # Guía de configuración para Claude
├── install.sh                 # Script de instalación con uv
├── pyproject.toml             # Configuración del proyecto
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## 🌐 Fuentes soportadas

### Fuentes Activas
- **La Pelotona** - Partidos con horarios y canales de TV en español
- **ESPN Deportes** - Calendario completo de fútbol internacional
- **FlashScore** - Resultados y fixtures en vivo de todas las ligas
- **SofaScore** - Estadísticas detalladas y partidos en tiempo real
- **LiveScore** - Resultados en vivo y fixtures actualizados
- **FotMob** - Partidos, noticias y análisis de fútbol

### Fuentes Configuradas (disponibles para activar)
- **ESPN** - Cobertura internacional completa
- **Goal.com** - Noticias y fixtures globales  
- **BBC Sport** - Deportes británicos y europeos
- **Marca** - Enfoque en fútbol español y europeo
- **AS** - Deportes en español
- **Sky Sports** - Premier League y fútbol europeo
- **UEFA** - Competiciones europeas oficiales

*Fácilmente expandible agregando URLs en `config.py`*

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-fuente`
3. Agrega la nueva fuente en `config.py`
4. Prueba con `python test_scraper.py`
5. Commit y push: `git commit -am 'Agregar fuente XYZ'`
6. Crea un Pull Request

## 📄 Licencia

MIT License - Usa libremente para proyectos personales y comerciales.

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa las fuentes**: Las páginas web cambian frecuentemente
2. **Prueba fuentes individuales**: `python test_scraper.py <URL>`
3. **Verifica conectividad**: Algunas fuentes pueden bloquear ciertos IPs
4. **Actualiza selectores**: Modifica `config.py` si una fuente cambió su estructura

---

⭐ **¡Dale una estrella si te resulta útil!** ⭐
