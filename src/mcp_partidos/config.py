"""
Configuración de fuentes de datos para obtener partidos de fútbol
"""

from typing import List, Dict, Any

# URLs de fuentes de partidos de fútbol
# Puedes modificar esta lista fácilmente para agregar o quitar fuentes
FUENTES_PARTIDOS: List[str] = [
    # ESPN - Cobertura internacional completa
    "https://www.lapelotona.com/us-en/soccer-games/",
]

# Configuración específica para cada fuente
CONFIGURACION_FUENTES: Dict[str, Dict[str, Any]] = {
    "lapelotona.com": {
        "selectores": {
            "partido": "table.views-table tbody tr, #partidos-hoy tbody tr",
            "equipo_local": ".equipos span:first-child",
            "equipo_visitante": ".equipos span:last-child",
            "hora": ".fecha .usa-time-et",  # Usar Eastern Time como referencia
            "liga_y_canal": ".fecha",  # Todo el contenido después del <br>
            "liga": ".fecha",  # Se extraerá de liga_y_canal
            "canal": ".fecha"  # Se extraerá de liga_y_canal
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        },
        "timeout": 10,
        "parser_especial": "lapelotona"  # Marcador para usar parser especial
    },
    
    "espn.com": {
        "selectores": {
            "partido": ".Table__TR",
            "equipo_local": ".home-team .AnchorLink",
            "equipo_visitante": ".away-team .AnchorLink", 
            "hora": ".game-time",
            "liga": ".league-name",
            "canal": ".broadcast-info"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    },
    
    "goal.com": {
        "selectores": {
            "partido": ".fixture-row",
            "equipo_local": ".home-team",
            "equipo_visitante": ".away-team",
            "hora": ".fixture-time",
            "liga": ".competition-name",
            "canal": ".tv-info"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    },
    
    "bbc.com": {
        "selectores": {
            "partido": ".fixture",
            "equipo_local": ".team-home",
            "equipo_visitante": ".team-away",
            "hora": ".fixture-date",
            "liga": ".competition",
            "canal": ".broadcast"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    },
    
    "marca.com": {
        "selectores": {
            "partido": ".partido",
            "equipo_local": ".equipo-local",
            "equipo_visitante": ".equipo-visitante",
            "hora": ".hora-partido",
            "liga": ".competicion",
            "canal": ".television"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    },
    
    "as.com": {
        "selectores": {
            "partido": ".match-row",
            "equipo_local": ".local",
            "equipo_visitante": ".visitante", 
            "hora": ".time",
            "liga": ".league",
            "canal": ".tv"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    },
    
    "skysports.com": {
        "selectores": {
            "partido": ".fixres__item",
            "equipo_local": ".matches__participant--side1",
            "equipo_visitante": ".matches__participant--side2",
            "hora": ".matches__date",
            "liga": ".matches__competition",
            "canal": ".matches__coverage"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "timeout": 10
    }
}

# Configuración general del scraper
CONFIGURACION_SCRAPER: Dict[str, Any] = {
    "timeout_general": 15,
    "reintentos": 3,
    "delay_entre_requests": 1,  # segundos
    "usar_cache": True,
    "cache_duracion": 300,  # 5 minutos en segundos
    "max_partidos_por_fuente": 50,
    "headers_default": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
}

# Palabras clave para detectar equipos "grandes" o partidos atractivos
EQUIPOS_GRANDES: List[str] = [
    # España
    "Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Bilbao", "Valencia", "Sevilla",
    
    # Inglaterra  
    "Manchester United", "Manchester City", "Liverpool", "Chelsea", "Arsenal", "Tottenham",
    
    # Italia
    "Juventus", "Inter Milan", "AC Milan", "Napoli", "Roma", "Lazio",
    
    # Alemania
    "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",
    
    # Francia
    "Paris Saint-Germain", "PSG", "Marseille", "Lyon", "Monaco",
    
    # Portugal
    "Porto", "Benfica", "Sporting CP",
    
    # Países Bajos
    "Ajax", "PSV", "Feyenoord",
    
    # Argentina
    "Boca Juniors", "River Plate", "Racing", "Independiente",
    
    # Brasil
    "Flamengo", "Palmeiras", "Corinthians", "Santos", "Sao Paulo",
    
    # Otros equipos relevantes internacionalmente
    "Celtic", "Rangers", "Galatasaray", "Fenerbahce"
]

# Ligas importantes para priorizar partidos
LIGAS_IMPORTANTES: List[str] = [
    "Champions League", "UEFA Champions League", "UCL",
    "Europa League", "UEFA Europa League", "UEL", 
    "Premier League", "EPL",
    "La Liga", "LaLiga", "Primera División",
    "Serie A", "Serie A TIM",
    "Bundesliga", "1. Bundesliga",
    "Ligue 1", "Ligue 1 Uber Eats",
    "Liga MX", "Liga BBVA MX",
    "Copa Libertadores", "CONMEBOL Libertadores",
    "Copa América", "CONMEBOL Copa América",
    "UEFA Nations League",
    "FIFA World Cup", "Mundial", "World Cup"
]