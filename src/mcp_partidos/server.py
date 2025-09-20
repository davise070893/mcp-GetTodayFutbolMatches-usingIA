"""
Servidor MCP principal para obtener datos de partidos de fútbol
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from .scraper import PartidosScraper
from .config import FUENTES_PARTIDOS
from .models import Partido


class PartidosMCPServer:
    """Servidor MCP para obtener datos de partidos de fútbol"""
    
    def __init__(self):
        self.server = Server("mcp-partidos")
        self.scraper = PartidosScraper()
        self._setup_tools()
    
    def _setup_tools(self):
        """Configura las herramientas disponibles en el servidor MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Lista las herramientas disponibles"""
            return [
                Tool(
                    name="obtener_partidos_hoy",
                    description="Obtiene todos los partidos de fútbol programados para hoy desde múltiples fuentes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "incluir_fuentes": {
                                "type": "boolean",
                                "description": "Si incluir información de la fuente de cada partido",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="obtener_partidos_fecha",
                    description="Obtiene partidos de fútbol para una fecha específica",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "fecha": {
                                "type": "string",
                                "description": "Fecha en formato YYYY-MM-DD",
                                "pattern": r"^\d{4}-\d{2}-\d{2}$"
                            },
                            "incluir_fuentes": {
                                "type": "boolean",
                                "description": "Si incluir información de la fuente de cada partido",
                                "default": True
                            }
                        },
                        "required": ["fecha"]
                    }
                ),
                Tool(
                    name="listar_fuentes",
                    description="Lista todas las fuentes configuradas para obtener datos de partidos",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="probar_fuente",
                    description="Prueba una fuente específica para verificar si funciona correctamente",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL de la fuente a probar"
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Maneja las llamadas a las herramientas"""
            
            if name == "obtener_partidos_hoy":
                return await self._obtener_partidos_hoy(arguments)
            
            elif name == "obtener_partidos_fecha":
                return await self._obtener_partidos_fecha(arguments)
            
            elif name == "listar_fuentes":
                return await self._listar_fuentes()
            
            elif name == "probar_fuente":
                return await self._probar_fuente(arguments)
            
            else:
                raise ValueError(f"Herramienta desconocida: {name}")
    
    async def _obtener_partidos_hoy(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Obtiene partidos de hoy"""
        try:
            incluir_fuentes = arguments.get("incluir_fuentes", True)
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            
            partidos = await self.scraper.obtener_partidos_fecha(fecha_hoy)
            
            resultado = {
                "partidos": [partido.to_dict(incluir_fuente=incluir_fuentes) for partido in partidos],
                "fecha": fecha_hoy,
                "timestamp": datetime.now().isoformat(),
                "total_partidos": len(partidos),
                "fuentes_consultadas": len(FUENTES_PARTIDOS)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(resultado, indent=2, ensure_ascii=False)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Error al obtener partidos de hoy: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            )]
    
    async def _obtener_partidos_fecha(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Obtiene partidos para una fecha específica"""
        try:
            fecha = arguments["fecha"]
            incluir_fuentes = arguments.get("incluir_fuentes", True)
            
            partidos = await self.scraper.obtener_partidos_fecha(fecha)
            
            resultado = {
                "partidos": [partido.to_dict(incluir_fuente=incluir_fuentes) for partido in partidos],
                "fecha": fecha,
                "timestamp": datetime.now().isoformat(),
                "total_partidos": len(partidos),
                "fuentes_consultadas": len(FUENTES_PARTIDOS)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(resultado, indent=2, ensure_ascii=False)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Error al obtener partidos para {arguments.get('fecha', 'fecha no especificada')}: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            )]
    
    async def _listar_fuentes(self) -> List[TextContent]:
        """Lista todas las fuentes configuradas"""
        resultado = {
            "fuentes": [
                {
                    "url": fuente,
                    "activa": True,  # TODO: Implementar verificación de estado
                    "descripcion": self._obtener_descripcion_fuente(fuente)
                }
                for fuente in FUENTES_PARTIDOS
            ],
            "total_fuentes": len(FUENTES_PARTIDOS),
            "timestamp": datetime.now().isoformat()
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(resultado, indent=2, ensure_ascii=False)
        )]
    
    async def _probar_fuente(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Prueba una fuente específica"""
        try:
            url = arguments["url"]
            
            # Probar la fuente
            exito, mensaje = await self.scraper.probar_fuente(url)
            
            resultado = {
                "url": url,
                "funciona": exito,
                "mensaje": mensaje,
                "timestamp": datetime.now().isoformat()
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(resultado, indent=2, ensure_ascii=False)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Error al probar fuente {arguments.get('url', 'URL no especificada')}: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            )]
    
    def _obtener_descripcion_fuente(self, url: str) -> str:
        """Obtiene una descripción legible de la fuente"""
        if "espn" in url.lower():
            return "ESPN - Deportes y fútbol internacional"
        elif "goal" in url.lower():
            return "Goal.com - Noticias de fútbol mundial"
        elif "marca" in url.lower():
            return "Marca - Deportes en español"
        elif "as" in url.lower():
            return "AS - Diario deportivo"
        elif "bbc" in url.lower():
            return "BBC Sport - Deportes británicos"
        else:
            return f"Fuente deportiva: {url}"


async def main():
    """Función principal para ejecutar el servidor MCP"""
    server_instance = PartidosMCPServer()
    
    # Configurar opciones de inicialización
    init_options = InitializationOptions(
        server_name="mcp-partidos",
        server_version="0.1.0",
        capabilities={
            "tools": {}
        }
    )
    
    # Ejecutar el servidor
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, 
            write_stream, 
            init_options
        )


if __name__ == "__main__":
    asyncio.run(main())