# Nuevas Fuentes Agregadas - Soccer Match Sources

Este documento describe las nuevas fuentes de partidos de fútbol que se han agregado al proyecto.

## 🎯 Resumen de Cambios

Se han agregado **5 nuevas fuentes** para obtener información de partidos de fútbol, aumentando de 1 a 6 fuentes totales configuradas en el sistema.

## 📋 Fuentes Agregadas

### 1. ESPN Deportes
- **URL**: `https://www.espndeportes.espn.com/futbol/calendario`
- **Descripción**: Versión en español de ESPN con calendario completo de fútbol internacional
- **Ventajas**: 
  - Cobertura completa de ligas internacionales
  - Información confiable y actualizada
  - Incluye horarios y ligas

### 2. FlashScore
- **URL**: `https://www.flashscore.com/football/`
- **Descripción**: Plataforma de resultados y fixtures en vivo
- **Ventajas**:
  - Resultados en tiempo real
  - Cobertura de todas las ligas principales
  - Información de partidos actualizada constantemente

### 3. SofaScore
- **URL**: `https://www.sofascore.com/football`
- **Descripción**: Estadísticas detalladas y partidos en tiempo real
- **Ventajas**:
  - Estadísticas avanzadas
  - Información detallada de equipos
  - Cobertura global

### 4. LiveScore
- **URL**: `https://www.livescore.com/en/football/`
- **Descripción**: Resultados en vivo y fixtures actualizados
- **Ventajas**:
  - Actualización en tiempo real
  - Interface simple y directa
  - Alta disponibilidad

### 5. FotMob
- **URL**: `https://www.fotmob.com/matches`
- **Descripción**: Partidos, noticias y análisis de fútbol
- **Ventajas**:
  - Análisis detallado de partidos
  - Noticias integradas
  - Cobertura de ligas de todo el mundo

## 🔧 Configuración Técnica

Cada fuente incluye:

### Selectores CSS Personalizados
Cada fuente tiene selectores CSS específicos para extraer:
- Equipos local y visitante
- Hora del partido
- Liga/competición
- Canales de transmisión (cuando disponible)

### Headers HTTP Optimizados
Headers configurados para:
- Evitar bloqueos por bots
- Simular navegadores reales
- Aceptar múltiples tipos de contenido

### Timeouts Ajustados
- Fuentes principales: 10 segundos
- Nuevas fuentes: 15 segundos (para mayor estabilidad)

## 📊 Comparación: Antes vs Después

### Antes
- **Fuentes activas**: 1 (La Pelotona)
- **Cobertura**: Limitada
- **Redundancia**: Ninguna

### Después
- **Fuentes activas**: 6
- **Cobertura**: Global (múltiples regiones y ligas)
- **Redundancia**: Alta (si una fuente falla, hay 5 más)

## 🚀 Cómo Usar

### Probar todas las fuentes
```bash
python test_scraper.py
```

### Probar una fuente específica
```bash
python test_scraper.py "https://www.flashscore.com/football/"
```

### Obtener partidos del día
```python
from mcp_partidos.scraper import PartidosScraper
from datetime import datetime

scraper = PartidosScraper()
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
partidos = await scraper.obtener_partidos_fecha(fecha_hoy)
```

## ⚙️ Personalización

### Agregar más fuentes
Para agregar una nueva fuente, edita `src/mcp_partidos/config.py`:

1. Agrega la URL a `FUENTES_PARTIDOS`
2. Agrega la configuración a `CONFIGURACION_FUENTES` con el dominio como clave

Ejemplo:
```python
FUENTES_PARTIDOS = [
    # ... fuentes existentes ...
    "https://tu-nueva-fuente.com/futbol",
]

CONFIGURACION_FUENTES = {
    # ... configuraciones existentes ...
    "tu-nueva-fuente.com": {
        "selectores": {
            "partido": ".match",
            "equipo_local": ".home",
            "equipo_visitante": ".away",
            "hora": ".time",
            "liga": ".league",
            "canal": ".tv"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0..."
        },
        "timeout": 15
    }
}
```

### Desactivar fuentes
Para desactivar una fuente temporalmente, simplemente comenta la línea en `FUENTES_PARTIDOS`:

```python
FUENTES_PARTIDOS = [
    "https://www.lapelotona.com/us-en/soccer-games/",
    # "https://www.espndeportes.espn.com/futbol/calendario",  # Desactivada temporalmente
    "https://www.flashscore.com/football/",
    # ... resto de fuentes
]
```

## 🎓 Beneficios de Múltiples Fuentes

1. **Mayor Cobertura**: Diferentes fuentes cubren diferentes ligas y competiciones
2. **Redundancia**: Si una fuente falla, otras pueden compensar
3. **Diversidad de Datos**: Cada fuente puede proporcionar información complementaria
4. **Confiabilidad**: Reduce dependencia de una única fuente
5. **Comparación**: Permite validar información entre fuentes

## 📝 Notas Importantes

- Las fuentes web pueden cambiar su estructura HTML en cualquier momento
- Es recomendable probar las fuentes periódicamente
- Los selectores CSS pueden necesitar actualizaciones con el tiempo
- Algunas fuentes pueden requerir JavaScript para cargar contenido (no soportado actualmente)

## 🔍 Troubleshooting

### Si una fuente no funciona:
1. Verifica que la URL sigue siendo válida
2. Revisa si la estructura HTML del sitio cambió
3. Actualiza los selectores CSS en `config.py`
4. Verifica que no haya bloqueos por IP o User-Agent

### Para depurar:
```bash
# Probar fuente específica con detalles
python test_scraper.py "https://fuente-problematica.com"
```

## 📚 Referencias

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.asp)
- [aiohttp Documentation](https://docs.aiohttp.org/)

---

**Autor**: Copilot Agent  
**Fecha**: 2 de Octubre, 2025  
**Versión**: 1.0
