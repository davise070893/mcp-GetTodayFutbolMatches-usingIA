#!/usr/bin/env python3
"""
Script para probar una nueva fuente de partidos de fútbol
Uso: python probar_nueva_fuente.py
"""

import sys
import asyncio
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_partidos.config import FUENTES_PARTIDOS


async def menu_fuentes():
    """Muestra un menú para seleccionar y probar fuentes"""
    print("=" * 60)
    print("🔍 PROBADOR DE FUENTES DE PARTIDOS DE FÚTBOL")
    print("=" * 60)
    print()
    print("Fuentes disponibles:")
    print()
    
    for i, url in enumerate(FUENTES_PARTIDOS, 1):
        # Extraer nombre de la fuente de la URL
        dominio = url.split("//")[1].split("/")[0]
        print(f"{i}. {dominio}")
        print(f"   URL: {url}")
        print()
    
    print("-" * 60)
    print("Opciones:")
    print("  1-{}: Probar fuente específica".format(len(FUENTES_PARTIDOS)))
    print("  0: Probar todas las fuentes")
    print("  q: Salir")
    print("-" * 60)
    
    try:
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion.lower() == 'q':
            print("👋 ¡Hasta luego!")
            return
        
        if opcion == '0':
            print("\n🔄 Probando todas las fuentes...")
            await probar_todas()
        else:
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(FUENTES_PARTIDOS):
                    url = FUENTES_PARTIDOS[indice]
                    await probar_fuente_especifica(url)
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
    
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")


async def probar_fuente_especifica(url: str):
    """Prueba una fuente específica"""
    from mcp_partidos.scraper import PartidosScraper
    from datetime import datetime
    
    print(f"\n{'=' * 60}")
    print(f"🔍 Probando: {url}")
    print("=" * 60)
    
    scraper = PartidosScraper()
    
    try:
        # Probar conectividad
        print("\n1️⃣ Verificando conectividad...")
        exito, mensaje = await scraper.probar_fuente(url)
        print(f"   {mensaje}")
        
        if exito:
            # Intentar obtener partidos
            print("\n2️⃣ Obteniendo partidos...")
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            partidos = await scraper._obtener_partidos_fuente(url, fecha_hoy)
            
            if partidos:
                print(f"   ✅ {len(partidos)} partidos encontrados\n")
                print("📋 Ejemplos de partidos:")
                print("-" * 60)
                
                for i, partido in enumerate(partidos[:5], 1):
                    print(f"\n{i}. {partido.equipo_local} vs {partido.equipo_visitante}")
                    print(f"   🕐 Hora: {partido.hora}")
                    print(f"   🏟️  Liga: {partido.liga}")
                    if partido.canales:
                        print(f"   📺 Canales: {', '.join(partido.canales)}")
                    print(f"   ⭐ Nivel atractivo: {partido.nivel_atractivo}/5")
                
                if len(partidos) > 5:
                    print(f"\n... y {len(partidos) - 5} partidos más")
            else:
                print("   ⚠️  No se encontraron partidos para hoy")
                print("   Esto puede ser normal si no hay partidos programados.")
        else:
            print("\n❌ La fuente no está funcionando correctamente")
            print("   Posibles causas:")
            print("   - Problemas de red")
            print("   - Sitio web caído")
            print("   - Cambios en la estructura HTML")
            print("   - Bloqueo por User-Agent")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)


async def probar_todas():
    """Prueba todas las fuentes configuradas"""
    from mcp_partidos.scraper import PartidosScraper
    
    scraper = PartidosScraper()
    resultados = []
    
    for i, url in enumerate(FUENTES_PARTIDOS, 1):
        print(f"\n[{i}/{len(FUENTES_PARTIDOS)}] Probando: {url}")
        exito, mensaje = await scraper.probar_fuente(url)
        print(f"    {mensaje}")
        resultados.append((url, exito))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    exitosas = sum(1 for _, exito in resultados if exito)
    total = len(resultados)
    
    print(f"\n✅ Fuentes funcionando: {exitosas}/{total}")
    print(f"❌ Fuentes con problemas: {total - exitosas}/{total}")
    
    if exitosas > 0:
        print("\n✅ Fuentes exitosas:")
        for url, exito in resultados:
            if exito:
                dominio = url.split("//")[1].split("/")[0]
                print(f"   - {dominio}")
    
    if exitosas < total:
        print("\n❌ Fuentes con problemas:")
        for url, exito in resultados:
            if not exito:
                dominio = url.split("//")[1].split("/")[0]
                print(f"   - {dominio}")
    
    print()


if __name__ == "__main__":
    try:
        asyncio.run(menu_fuentes())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
