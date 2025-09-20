"""
Modelos de datos para representar partidos de fútbol
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Partido:
    """Modelo que representa un partido de fútbol"""
    
    equipo_local: str
    equipo_visitante: str
    fecha: str  # Formato YYYY-MM-DD
    hora: str   # Formato HH:MM
    liga: str
    canales: List[str] = field(default_factory=list)
    estadio: Optional[str] = None
    fuente: Optional[str] = None
    url_fuente: Optional[str] = None
    estado: str = "programado"  # programado, en_vivo, finalizado
    marcador_local: Optional[int] = None
    marcador_visitante: Optional[int] = None
    minuto: Optional[str] = None
    arbitro: Optional[str] = None
    temperatura: Optional[str] = None
    
    # Metadatos adicionales
    es_partido_importante: bool = False
    nivel_atractivo: int = 1  # 1-5, donde 5 son los más atractivos
    fecha_extraccion: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self, incluir_fuente: bool = True, incluir_metadatos: bool = False) -> Dict[str, Any]:
        """Convierte el partido a diccionario para JSON"""
        data = {
            "equipo_local": self.equipo_local,
            "equipo_visitante": self.equipo_visitante,
            "fecha": self.fecha,
            "hora": self.hora,
            "liga": self.liga,
            "canales": self.canales,
            "estadio": self.estadio,
            "estado": self.estado
        }
        
        # Agregar marcador si existe
        if self.marcador_local is not None and self.marcador_visitante is not None:
            data["marcador"] = {
                "local": self.marcador_local,
                "visitante": self.marcador_visitante
            }
        
        # Agregar información del partido en vivo
        if self.minuto:
            data["minuto"] = self.minuto
            
        if self.arbitro:
            data["arbitro"] = self.arbitro
            
        if self.temperatura:
            data["temperatura"] = self.temperatura
        
        # Agregar información de fuente si se solicita
        if incluir_fuente and self.fuente:
            data["fuente"] = {
                "nombre": self.fuente,
                "url": self.url_fuente
            }
        
        # Agregar metadatos si se solicita
        if incluir_metadatos:
            data["metadatos"] = {
                "es_partido_importante": self.es_partido_importante,
                "nivel_atractivo": self.nivel_atractivo,
                "fecha_extraccion": self.fecha_extraccion
            }
        
        return data
    
    def to_json(self, **kwargs) -> str:
        """Convierte el partido a JSON string"""
        return json.dumps(self.to_dict(**kwargs), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Partido':
        """Crea un Partido desde un diccionario"""
        # Extraer marcador si existe
        marcador_local = None
        marcador_visitante = None
        if "marcador" in data:
            marcador_local = data["marcador"].get("local")
            marcador_visitante = data["marcador"].get("visitante")
        
        # Extraer información de fuente si existe
        fuente = None
        url_fuente = None
        if "fuente" in data and isinstance(data["fuente"], dict):
            fuente = data["fuente"].get("nombre")
            url_fuente = data["fuente"].get("url")
        elif "fuente" in data and isinstance(data["fuente"], str):
            fuente = data["fuente"]
        
        # Extraer metadatos si existen
        es_partido_importante = False
        nivel_atractivo = 1
        fecha_extraccion = datetime.now().isoformat()
        
        if "metadatos" in data:
            metadatos = data["metadatos"]
            es_partido_importante = metadatos.get("es_partido_importante", False)
            nivel_atractivo = metadatos.get("nivel_atractivo", 1)
            fecha_extraccion = metadatos.get("fecha_extraccion", fecha_extraccion)
        
        return cls(
            equipo_local=data["equipo_local"],
            equipo_visitante=data["equipo_visitante"],
            fecha=data["fecha"],
            hora=data["hora"],
            liga=data["liga"],
            canales=data.get("canales", []),
            estadio=data.get("estadio"),
            fuente=fuente,
            url_fuente=url_fuente,
            estado=data.get("estado", "programado"),
            marcador_local=marcador_local,
            marcador_visitante=marcador_visitante,
            minuto=data.get("minuto"),
            arbitro=data.get("arbitro"),
            temperatura=data.get("temperatura"),
            es_partido_importante=es_partido_importante,
            nivel_atractivo=nivel_atractivo,
            fecha_extraccion=fecha_extraccion
        )


@dataclass 
class RespuestaPartidos:
    """Modelo para la respuesta completa con múltiples partidos"""
    
    partidos: List[Partido]
    fecha_consulta: str
    total_partidos: int
    fuentes_consultadas: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    errores: List[str] = field(default_factory=list)
    estadisticas: Optional[Dict[str, Any]] = None
    
    def to_dict(self, incluir_fuente: bool = True, incluir_metadatos: bool = False) -> Dict[str, Any]:
        """Convierte la respuesta a diccionario"""
        data = {
            "partidos": [
                partido.to_dict(incluir_fuente=incluir_fuente, incluir_metadatos=incluir_metadatos) 
                for partido in self.partidos
            ],
            "fecha_consulta": self.fecha_consulta,
            "total_partidos": self.total_partidos,
            "fuentes_consultadas": self.fuentes_consultadas,
            "timestamp": self.timestamp
        }
        
        if self.errores:
            data["errores"] = self.errores
            
        if self.estadisticas:
            data["estadisticas"] = self.estadisticas
            
        return data
    
    def to_json(self, **kwargs) -> str:
        """Convierte la respuesta a JSON string"""
        return json.dumps(self.to_dict(**kwargs), ensure_ascii=False, indent=2)
    
    def generar_estadisticas(self) -> Dict[str, Any]:
        """Genera estadísticas de los partidos obtenidos"""
        if not self.partidos:
            return {}
        
        # Contadores por liga
        ligas = {}
        canales = {}
        estados = {}
        
        partidos_importantes = 0
        total_nivel_atractivo = 0
        
        for partido in self.partidos:
            # Contar por liga
            liga = partido.liga
            ligas[liga] = ligas.get(liga, 0) + 1
            
            # Contar por canal
            for canal in partido.canales:
                canales[canal] = canales.get(canal, 0) + 1
            
            # Contar por estado
            estado = partido.estado
            estados[estado] = estados.get(estado, 0) + 1
            
            # Estadísticas de importancia
            if partido.es_partido_importante:
                partidos_importantes += 1
            
            total_nivel_atractivo += partido.nivel_atractivo
        
        estadisticas = {
            "por_liga": dict(sorted(ligas.items(), key=lambda x: x[1], reverse=True)),
            "por_canal": dict(sorted(canales.items(), key=lambda x: x[1], reverse=True)),
            "por_estado": estados,
            "partidos_importantes": partidos_importantes,
            "nivel_atractivo_promedio": round(total_nivel_atractivo / len(self.partidos), 2),
            "ligas_representadas": len(ligas),
            "canales_disponibles": len(canales)
        }
        
        self.estadisticas = estadisticas
        return estadisticas


@dataclass
class FuenteResultado:
    """Modelo para el resultado de una fuente específica"""
    
    url: str
    nombre: str
    exitosa: bool
    partidos_obtenidos: int
    tiempo_respuesta: float  # segundos
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario"""
        return {
            "url": self.url,
            "nombre": self.nombre,
            "exitosa": self.exitosa,
            "partidos_obtenidos": self.partidos_obtenidos,
            "tiempo_respuesta": self.tiempo_respuesta,
            "error": self.error,
            "timestamp": self.timestamp
        }