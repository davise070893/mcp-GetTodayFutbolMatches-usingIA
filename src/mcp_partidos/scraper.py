"""
Módulo de web scraping para obtener datos de partidos de fútbol
"""

import asyncio
import aiohttp
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from .models import Partido, RespuestaPartidos, FuenteResultado
from .config import (
    FUENTES_PARTIDOS, 
    CONFIGURACION_FUENTES, 
    CONFIGURACION_SCRAPER,
    EQUIPOS_GRANDES,
    LIGAS_IMPORTANTES
)


class PartidosScraper:
    """Clase principal para hacer scraping de partidos de fútbol"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    async def __aenter__(self):
        """Entrada del context manager"""
        await self._inicializar_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Salida del context manager"""
        await self._cerrar_session()
    
    async def _inicializar_session(self):
        """Inicializa la sesión HTTP"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=CONFIGURACION_SCRAPER["timeout_general"])
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=CONFIGURACION_SCRAPER["headers_default"]
            )
    
    async def _cerrar_session(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def obtener_partidos_fecha(self, fecha: str) -> List[Partido]:
        """
        Obtiene partidos para una fecha específica desde todas las fuentes configuradas
        
        Args:
            fecha: Fecha en formato YYYY-MM-DD
            
        Returns:
            Lista de partidos encontrados
        """
        await self._inicializar_session()
        
        todos_partidos = []
        tareas = []
        
        # Crear tareas para cada fuente
        for url in FUENTES_PARTIDOS:
            tarea = self._obtener_partidos_fuente(url, fecha)
            tareas.append(tarea)
        
        # Ejecutar todas las tareas en paralelo
        resultados = await asyncio.gather(*tareas, return_exceptions=True)
        
        # Procesar resultados
        for i, resultado in enumerate(resultados):
            if isinstance(resultado, Exception):
                print(f"Error en fuente {FUENTES_PARTIDOS[i]}: {resultado}")
                continue
            
            if isinstance(resultado, list):
                # Agregar partidos válidos
                for partido in resultado:
                    if partido and self._validar_partido(partido):
                        # Evaluar importancia del partido
                        self._evaluar_partido(partido)
                        todos_partidos.append(partido)
        
        # Eliminar duplicados
        partidos_unicos = self._eliminar_duplicados(todos_partidos)
        
        # Ordenar por hora
        partidos_unicos.sort(key=lambda p: p.hora)
        
        await self._cerrar_session()
        return partidos_unicos
    
    async def _obtener_partidos_fuente(self, url: str, fecha: str) -> List[Partido]:
        """
        Obtiene partidos de una fuente específica
        
        Args:
            url: URL de la fuente
            fecha: Fecha objetivo
            
        Returns:
            Lista de partidos de esa fuente
        """
        try:
            # Verificar caché
            cache_key = f"{url}_{fecha}"
            if self._usar_cache() and cache_key in self.cache:
                cache_data = self.cache[cache_key]
                if time.time() - cache_data["timestamp"] < CONFIGURACION_SCRAPER["cache_duracion"]:
                    return cache_data["partidos"]
            
            # Obtener HTML de la página
            html = await self._obtener_html(url)
            if not html:
                return []
            
            # Parsear partidos según la fuente
            partidos = await self._parsear_partidos(html, url, fecha)
            
            # Guardar en caché
            if self._usar_cache():
                self.cache[cache_key] = {
                    "partidos": partidos,
                    "timestamp": time.time()
                }
            
            return partidos
            
        except Exception as e:
            print(f"Error procesando fuente {url}: {e}")
            return []
    
    async def _obtener_html(self, url: str) -> Optional[str]:
        """
        Obtiene el HTML de una URL con reintentos
        
        Args:
            url: URL objetivo
            
        Returns:
            HTML como string o None si falla
        """
        if not self.session:
            await self._inicializar_session()
        
        for intento in range(CONFIGURACION_SCRAPER["reintentos"]):
            try:
                # Obtener configuración específica de la fuente
                dominio = urlparse(url).netloc
                config_fuente = None
                
                for key in CONFIGURACION_FUENTES:
                    if key in dominio:
                        config_fuente = CONFIGURACION_FUENTES[key]
                        break
                
                # Configurar headers
                headers = CONFIGURACION_SCRAPER["headers_default"].copy()
                if config_fuente and "headers" in config_fuente:
                    headers.update(config_fuente["headers"])
                
                # Hacer request
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return html
                    else:
                        print(f"Error HTTP {response.status} para {url}")
                        
            except Exception as e:
                print(f"Intento {intento + 1} fallido para {url}: {e}")
                if intento < CONFIGURACION_SCRAPER["reintentos"] - 1:
                    await asyncio.sleep(CONFIGURACION_SCRAPER["delay_entre_requests"])
        
        return None
    
    async def _parsear_partidos(self, html: str, url: str, fecha_objetivo: str) -> List[Partido]:
        """
        Parsea partidos del HTML según la fuente
        
        Args:
            html: HTML de la página
            url: URL de origen
            fecha_objetivo: Fecha objetivo en formato YYYY-MM-DD
            
        Returns:
            Lista de partidos parseados
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            partidos = []
            
            # Obtener configuración específica de la fuente
            dominio = urlparse(url).netloc
            config_fuente = self._obtener_config_fuente(dominio)
            
            if config_fuente:
                # Usar selectores específicos de la fuente
                partidos = await self._parsear_con_selectores(soup, config_fuente, url, fecha_objetivo)
            else:
                # Usar parseo genérico
                partidos = await self._parsear_generico(soup, url, fecha_objetivo)
            
            return partidos[:CONFIGURACION_SCRAPER["max_partidos_por_fuente"]]
            
        except Exception as e:
            print(f"Error parseando HTML de {url}: {e}")
            return []
    
    async def _parsear_con_selectores(self, soup: BeautifulSoup, config: Dict[str, Any], 
                                    url: str, fecha_objetivo: str) -> List[Partido]:
        """Parsea usando selectores específicos de la fuente"""
        partidos = []
        selectores = config.get("selectores", {})
        
        # Buscar elementos de partidos
        elementos_partidos = soup.select(selectores.get("partido", ".partido, .match, .fixture"))
        
        for elemento in elementos_partidos:
            try:
                partido = await self._extraer_datos_partido(elemento, selectores, url, fecha_objetivo)
                if partido:
                    partidos.append(partido)
            except Exception as e:
                print(f"Error extrayendo partido individual: {e}")
                continue
        
        return partidos
    
    async def _parsear_generico(self, soup: BeautifulSoup, url: str, fecha_objetivo: str) -> List[Partido]:
        """Parseo genérico cuando no hay configuración específica"""
        partidos = []
        
        # Selectores genéricos comunes
        selectores_genericos = [
            ".fixture", ".match", ".partido", ".game", 
            "[data-fixture]", "[data-match]", ".event-row"
        ]
        
        for selector in selectores_genericos:
            elementos = soup.select(selector)
            if elementos:
                # Intentar extraer con patrones genéricos
                for elemento in elementos[:20]:  # Limitar para evitar spam
                    try:
                        partido = await self._extraer_datos_generico(elemento, url, fecha_objetivo)
                        if partido:
                            partidos.append(partido)
                    except:
                        continue
                break  # Si encontramos elementos, no probar otros selectores
        
        return partidos
    
    async def _extraer_datos_partido(self, elemento: Tag, selectores: Dict[str, str], 
                                   url: str, fecha_objetivo: str) -> Optional[Partido]:
        """Extrae datos de un partido usando selectores específicos"""
        try:
            # Verificar si necesitamos usar un parser especial
            dominio = urlparse(url).netloc
            config_fuente = self._obtener_config_fuente(dominio)
            
            if config_fuente and config_fuente.get("parser_especial") == "lapelotona":
                return await self._extraer_datos_lapelotona(elemento, url, fecha_objetivo)
            
            # Parser genérico para otras fuentes
            # Extraer equipos
            equipo_local = self._extraer_texto(elemento, selectores.get("equipo_local", ""))
            equipo_visitante = self._extraer_texto(elemento, selectores.get("equipo_visitante", ""))
            
            if not equipo_local or not equipo_visitante:
                return None
            
            # Extraer hora
            hora = self._extraer_hora(elemento, selectores.get("hora", ""))
            if not hora:
                hora = "TBD"
            
            # Extraer liga
            liga = self._extraer_texto(elemento, selectores.get("liga", ""))
            if not liga:
                liga = "Liga no especificada"
            
            # Extraer canales
            canales = self._extraer_canales(elemento, selectores.get("canal", ""))
            
            # Extraer estadio
            estadio = self._extraer_texto(elemento, selectores.get("estadio", ""))
            
            # Crear objeto Partido
            partido = Partido(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fecha=fecha_objetivo,
                hora=hora,
                liga=liga,
                canales=canales,
                estadio=estadio,
                fuente=urlparse(url).netloc,
                url_fuente=url
            )
            
            return partido
            
        except Exception as e:
            print(f"Error extrayendo datos del partido: {e}")
            return None
    
    async def _extraer_datos_lapelotona(self, elemento: Tag, url: str, fecha_objetivo: str) -> Optional[Partido]:
        """Parser especial para La Pelotona con estructura específica"""
        try:
            # Extraer equipos de la columna "equipos"
            equipos_td = elemento.select_one(".equipos")
            if not equipos_td:
                return None
            
            equipos_spans = equipos_td.select("span")
            if len(equipos_spans) < 2:
                return None
            
            equipo_local = equipos_spans[0].get_text(strip=True)
            equipo_visitante = equipos_spans[1].get_text(strip=True)
            
            if not equipo_local or not equipo_visitante:
                return None
            
            # Extraer información de fecha/hora/liga/canal
            fecha_td = elemento.select_one(".fecha")
            if not fecha_td:
                return None
            
            # Obtener hora (preferir ET - Eastern Time)
            hora_et = fecha_td.select_one(".usa-time-et")
            if hora_et:
                hora_texto = hora_et.get_text(strip=True)
                # Convertir "7:30 am ET" a "07:30"
                hora = self._convertir_hora_lapelotona(hora_texto)
            else:
                hora = "TBD"
            
            # Extraer liga y canales del texto después del <br>
            fecha_texto_completo = fecha_td.get_text(" ", strip=True)
            
            # Buscar el patrón: Liga - Canales
            # Ejemplo: "Premier League - Fubo Sports,Universo,USA Network"
            liga = "Liga no especificada"
            canales = []
            
            # Dividir por el último " - " para separar liga de canales
            if " - " in fecha_texto_completo:
                partes = fecha_texto_completo.split(" - ")
                if len(partes) >= 2:
                    # La liga está antes del último " - "
                    liga_parte = " - ".join(partes[:-1])
                    canales_parte = partes[-1]
                    
                    # Extraer liga (buscar después de los horarios)
                    lineas = liga_parte.split()
                    # Buscar donde terminan los horarios y empieza la liga
                    for i, palabra in enumerate(lineas):
                        if not any(time_indicator in palabra.lower() for time_indicator in ['am', 'pm', 'pt', 'ct', 'et']):
                            liga = " ".join(lineas[i:])
                            break
                    
                    # Extraer canales
                    if canales_parte:
                        canales = [canal.strip() for canal in canales_parte.split(",")]
            
            # Limpiar liga de posibles restos de horarios
            liga = re.sub(r'\d+:\d+\s+(am|pm)\s+(PT|CT|ET)', '', liga, flags=re.IGNORECASE).strip()
            if not liga:
                liga = "Liga no especificada"
            
            # Crear objeto Partido
            partido = Partido(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fecha=fecha_objetivo,
                hora=hora,
                liga=liga,
                canales=canales,
                fuente="lapelotona.com",
                url_fuente=url
            )
            
            return partido
            
        except Exception as e:
            print(f"Error en parser de La Pelotona: {e}")
            return None
    
    def _convertir_hora_lapelotona(self, hora_texto: str) -> str:
        """Convierte hora de La Pelotona (ej: '7:30 am ET') a formato 24h"""
        try:
            # Remover 'ET', 'PT', 'CT' y espacios extra
            hora_limpia = re.sub(r'\s+(ET|PT|CT)$', '', hora_texto, flags=re.IGNORECASE).strip()
            
            # Parsear hora
            from datetime import datetime
            try:
                # Intentar formato "7:30 am"
                hora_obj = datetime.strptime(hora_limpia, "%I:%M %p")
                return hora_obj.strftime("%H:%M")
            except ValueError:
                # Intentar formato "7:30am" (sin espacio)
                hora_obj = datetime.strptime(hora_limpia, "%I:%M%p")
                return hora_obj.strftime("%H:%M")
                
        except Exception as e:
            print(f"Error convirtiendo hora '{hora_texto}': {e}")
            return hora_texto  # Devolver texto original si falla
    
    async def _extraer_datos_generico(self, elemento: Tag, url: str, fecha_objetivo: str) -> Optional[Partido]:
        """Extrae datos usando patrones genéricos"""
        try:
            texto_completo = elemento.get_text(" ", strip=True)
            
            # Buscar patrones de equipos (vs, contra, -, etc.)
            patrones_vs = [
                r"(.+?)\s+vs?\s+(.+)",
                r"(.+?)\s+-\s+(.+)",
                r"(.+?)\s+contra\s+(.+)",
                r"(.+?)\s+@\s+(.+)"
            ]
            
            equipo_local = None
            equipo_visitante = None
            
            for patron in patrones_vs:
                match = re.search(patron, texto_completo, re.IGNORECASE)
                if match:
                    equipo_local = match.group(1).strip()
                    equipo_visitante = match.group(2).strip()
                    break
            
            if not equipo_local or not equipo_visitante:
                return None
            
            # Buscar hora
            patron_hora = r"(\d{1,2}):(\d{2})"
            match_hora = re.search(patron_hora, texto_completo)
            hora = f"{match_hora.group(1)}:{match_hora.group(2)}" if match_hora else "TBD"
            
            return Partido(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fecha=fecha_objetivo,
                hora=hora,
                liga="Liga no especificada",
                canales=[],
                fuente=urlparse(url).netloc,
                url_fuente=url
            )
            
        except Exception as e:
            print(f"Error en extracción genérica: {e}")
            return None
    
    def _extraer_texto(self, elemento: Tag, selector: str) -> str:
        """Extrae texto usando un selector CSS"""
        if not selector:
            return ""
        
        try:
            sub_elemento = elemento.select_one(selector)
            if sub_elemento:
                return sub_elemento.get_text(strip=True)
        except:
            pass
        
        return ""
    
    def _extraer_hora(self, elemento: Tag, selector: str) -> str:
        """Extrae y normaliza la hora"""
        hora_raw = self._extraer_texto(elemento, selector)
        if not hora_raw:
            return ""
        
        # Normalizar formato de hora
        patron_hora = r"(\d{1,2}):(\d{2})"
        match = re.search(patron_hora, hora_raw)
        if match:
            return f"{match.group(1).zfill(2)}:{match.group(2)}"
        
        return hora_raw
    
    def _extraer_canales(self, elemento: Tag, selector: str) -> List[str]:
        """Extrae canales de transmisión"""
        canales_raw = self._extraer_texto(elemento, selector)
        if not canales_raw:
            return []
        
        # Separar múltiples canales
        separadores = [",", "/", ";", "|", " y ", " and "]
        canales = [canales_raw]
        
        for sep in separadores:
            nuevos_canales = []
            for canal in canales:
                nuevos_canales.extend([c.strip() for c in canal.split(sep)])
            canales = nuevos_canales
        
        return [c for c in canales if c and len(c) > 1]
    
    def _obtener_config_fuente(self, dominio: str) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración específica de una fuente"""
        for key, config in CONFIGURACION_FUENTES.items():
            if key in dominio:
                return config
        return None
    
    def _validar_partido(self, partido: Partido) -> bool:
        """Valida que un partido tenga datos mínimos requeridos"""
        return (
            partido.equipo_local and 
            partido.equipo_visitante and 
            partido.equipo_local != partido.equipo_visitante and
            len(partido.equipo_local) > 2 and
            len(partido.equipo_visitante) > 2
        )
    
    def _evaluar_partido(self, partido: Partido):
        """Evalúa la importancia y atractivo de un partido"""
        nivel_atractivo = 1
        es_importante = False
        
        # Verificar equipos grandes
        equipos_grandes_presentes = 0
        for equipo_grande in EQUIPOS_GRANDES:
            if (equipo_grande.lower() in partido.equipo_local.lower() or 
                equipo_grande.lower() in partido.equipo_visitante.lower()):
                equipos_grandes_presentes += 1
        
        # Verificar liga importante
        liga_importante = any(
            liga.lower() in partido.liga.lower() 
            for liga in LIGAS_IMPORTANTES
        )
        
        # Calcular nivel de atractivo
        if equipos_grandes_presentes >= 2:
            nivel_atractivo = 5
            es_importante = True
        elif equipos_grandes_presentes == 1:
            nivel_atractivo = 4 if liga_importante else 3
            es_importante = liga_importante
        elif liga_importante:
            nivel_atractivo = 3
            es_importante = True
        
        partido.nivel_atractivo = nivel_atractivo
        partido.es_partido_importante = es_importante
    
    def _eliminar_duplicados(self, partidos: List[Partido]) -> List[Partido]:
        """Elimina partidos duplicados basándose en equipos y hora"""
        partidos_unicos = []
        partidos_vistos = set()
        
        for partido in partidos:
            # Crear clave única basada en equipos y hora
            clave = f"{partido.equipo_local.lower()}_{partido.equipo_visitante.lower()}_{partido.hora}"
            
            if clave not in partidos_vistos:
                partidos_vistos.add(clave)
                partidos_unicos.append(partido)
        
        return partidos_unicos
    
    def _usar_cache(self) -> bool:
        """Verifica si usar caché"""
        return CONFIGURACION_SCRAPER.get("usar_cache", True)
    
    async def probar_fuente(self, url: str) -> Tuple[bool, str]:
        """
        Prueba si una fuente específica funciona
        
        Args:
            url: URL a probar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            await self._inicializar_session()
            
            inicio = time.time()
            html = await self._obtener_html(url)
            tiempo_respuesta = time.time() - inicio
            
            if html:
                # Intentar parsear algunos partidos
                partidos = await self._parsear_partidos(html, url, datetime.now().strftime("%Y-%m-%d"))
                
                if partidos:
                    mensaje = f"✅ Fuente funcional. {len(partidos)} partidos encontrados en {tiempo_respuesta:.2f}s"
                    return True, mensaje
                else:
                    mensaje = f"⚠️ Fuente responde pero no se encontraron partidos. Tiempo: {tiempo_respuesta:.2f}s"
                    return False, mensaje
            else:
                mensaje = "❌ No se pudo obtener contenido de la fuente"
                return False, mensaje
                
        except Exception as e:
            mensaje = f"❌ Error probando fuente: {str(e)}"
            return False, mensaje
        finally:
            await self._cerrar_session()