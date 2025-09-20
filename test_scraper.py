"""
Script de prueba para verificar el funcionamiento del scraper
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_partidos.scraper import PartidosScraper
from mcp_partidos.config import FUENTES_PARTIDOS


async def probar_scraper():
    """Prueba el scraper con una fecha específica"""
    print("🏈 Probando el scraper de partidos de fútbol")
    print("=" * 50)
    
    # Crear instancia del scraper
    scraper = PartidosScraper()
    
    try:
        # Obtener fecha de hoy
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 Fecha objetivo: {fecha_hoy}")
        print(f"🌐 Fuentes configuradas: {len(FUENTES_PARTIDOS)}")
        print()
        
        # Probar cada fuente individualmente
        print("🔍 Probando fuentes individuales:")
        print("-" * 30)
        
        for i, url in enumerate(FUENTES_PARTIDOS[:3], 1):  # Probar solo las primeras 3
            print(f"{i}. {url}")
            exito, mensaje = await scraper.probar_fuente(url)
            print(f"   {mensaje}")
            print()
        
        # Obtener partidos de todas las fuentes
        print("🔄 Obteniendo partidos de todas las fuentes...")
        partidos = await scraper.obtener_partidos_fecha(fecha_hoy)
        
        print(f"✅ Total de partidos encontrados: {len(partidos)}")
        print()
        
        # Mostrar algunos partidos de ejemplo
        if partidos:
            print("🏆 Ejemplos de partidos encontrados:")
            print("-" * 40)
            
            for i, partido in enumerate(partidos[:5], 1):
                print(f"{i}. {partido.equipo_local} vs {partido.equipo_visitante}")
                print(f"   🕐 {partido.hora} | 🏟️ {partido.liga}")
                if partido.canales:
                    print(f"   📺 {', '.join(partido.canales)}")
                print(f"   ⭐ Nivel atractivo: {partido.nivel_atractivo}/5")
                print(f"   🌐 Fuente: {partido.fuente}")
                print()
            
            if len(partidos) > 5:
                print(f"... y {len(partidos) - 5} partidos más")
        else:
            print("❌ No se encontraron partidos para hoy")
            print("   Esto puede deberse a:")
            print("   - Las fuentes no tienen partidos programados para hoy")
            print("   - Problemas de conectividad")
            print("   - Cambios en la estructura de las páginas web")
        
        # Mostrar estadísticas
        if partidos:
            print("\n📊 Estadísticas:")
            print("-" * 20)
            
            ligas = {}
            partidos_importantes = 0
            
            for partido in partidos:
                liga = partido.liga
                ligas[liga] = ligas.get(liga, 0) + 1
                
                if partido.es_partido_importante:
                    partidos_importantes += 1
            
            print(f"🏆 Partidos importantes: {partidos_importantes}")
            print(f"🏟️ Ligas representadas: {len(ligas)}")
            
            if ligas:
                print("   Top ligas:")
                for liga, count in sorted(ligas.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"   - {liga}: {count} partidos")
    
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()


async def probar_fuente_especifica(url: str):
    """Prueba una fuente específica"""
    print(f"🔍 Probando fuente específica: {url}")
    print("=" * 60)
    
    scraper = PartidosScraper()
    
    try:
        exito, mensaje = await scraper.probar_fuente(url)
        print(mensaje)
        
        if exito:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            partidos = await scraper._obtener_partidos_fuente(url, fecha_hoy)
            
            print(f"\n📋 Partidos encontrados: {len(partidos)}")
            
            for i, partido in enumerate(partidos[:3], 1):
                print(f"{i}. {partido.equipo_local} vs {partido.equipo_visitante}")
                print(f"   🕐 {partido.hora} | 🏟️ {partido.liga}")
                if partido.canales:
                    print(f"   📺 {', '.join(partido.canales)}")
                print()
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Probar fuente específica
        url = sys.argv[1]
        asyncio.run(probar_fuente_especifica(url))
    else:
        # Probar todas las fuentes
        asyncio.run(probar_scraper())