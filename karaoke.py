#!/usr/bin/env python3
"""
Sistema de Karaoke - Reproductor y gestor de canciones
Uso: python karaoke.py [comando] [parámetro]

Comandos:
  list              Listar todas las canciones disponibles
  show <canción>    Mostrar letra de una canción
  search <texto>    Buscar canción por título o artista
  info <canción>    Mostrar información detallada de una canción
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
import argparse
import codecs


class GestorKaraoke:
    def __init__(self, carpeta_canciones: str = "canciones"):
        self.carpeta_canciones = carpeta_canciones
        self.canciones = {}
        # Configurar stdout para UTF-8 en Windows
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        self.cargar_canciones()
    
    def cargar_canciones(self) -> None:
        """Carga todos los JSONs de canciones disponibles."""
        if not os.path.exists(self.carpeta_canciones):
            print(f"❌ Error: Carpeta '{self.carpeta_canciones}' no encontrada")
            return
        
        for archivo in sorted(Path(self.carpeta_canciones).glob("*.json")):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    # Usar el título como clave (en minúsculas para búsqueda)
                    clave = datos['titulo'].lower()
                    self.canciones[clave] = datos
            except Exception as e:
                print(f"⚠️  Error cargando {archivo}: {e}")
    
    def listar_canciones(self) -> None:
        """Muestra listado de todas las canciones."""
        if not self.canciones:
            print("❌ No hay canciones disponibles")
            return
        
        print(f"\n{'='*70}")
        print(f"📋 CANCIONES DISPONIBLES ({len(self.canciones)} total)")
        print(f"{'='*70}\n")
        
        for idx, (clave, datos) in enumerate(self.canciones.items(), 1):
            titulo = datos['titulo']
            artista = datos['artista']
            num_lineas = len(datos['lineas'])
            print(f"{idx:2d}. {titulo:40s} | {artista:30s} ({num_lineas} líneas)")
        
        print(f"\n{'='*70}\n")
        print("💡 Uso: python karaoke.py show \"TITULO CANCIÓN\"")
        print("💡 Ejemplo: python karaoke.py show \"bandido\"\n")
    
    def buscar_cancion(self, nombre: str) -> Optional[str]:
        """
        Busca una canción por nombre (parcial).
        Retorna la clave exacta si encuentra coincidencia.
        """
        nombre_lower = nombre.lower()
        
        # Búsqueda exacta
        if nombre_lower in self.canciones:
            return nombre_lower
        
        # Búsqueda parcial
        coincidencias = []
        for clave, datos in self.canciones.items():
            titulo = datos['titulo'].lower()
            artista = datos['artista'].lower()
            
            if nombre_lower in titulo or nombre_lower in artista:
                coincidencias.append((clave, datos))
        
        return coincidencias
    
    def mostrar_cancion(self, nombre: str) -> None:
        """Muestra la letra de una canción con formato."""
        resultados = self.buscar_cancion(nombre)
        
        if isinstance(resultados, str):
            # Búsqueda exacta
            cancion = self.canciones[resultados]
            self._imprimir_cancion(cancion)
        elif isinstance(resultados, list) and resultados:
            # Búsqueda parcial
            if len(resultados) == 1:
                cancion = resultados[0][1]
                self._imprimir_cancion(cancion)
            else:
                # Múltiples resultados
                print(f"\n⚠️  Se encontraron {len(resultados)} coincidencias:\n")
                for idx, (clave, datos) in enumerate(resultados, 1):
                    print(f"{idx}. {datos['titulo']:40s} - {datos['artista']}")
                print()
        else:
            print(f"\n❌ No se encontró canción con el nombre '{nombre}'")
            print("Usa: python karaoke.py list\n")
    
    def _imprimir_cancion(self, cancion: Dict) -> None:
        """Imprime una canción con formato bonito."""
        print(f"\n{'='*70}")
        print(f"🎤 {cancion['titulo']}")
        print(f"🎵 {cancion['artista']}")
        print(f"{'='*70}\n")
        
        for idx, linea in enumerate(cancion['lineas'], 1):
            texto = linea['texto']
            print(f"{texto}")
        
        print(f"\n{'='*70}\n")
    
    def mostrar_info(self, nombre: str) -> None:
        """Muestra información detallada de una canción (con tiempos)."""
        resultados = self.buscar_cancion(nombre)
        
        if isinstance(resultados, str):
            cancion = self.canciones[resultados]
            self._imprimir_info_detallada(cancion)
        elif isinstance(resultados, list) and len(resultados) == 1:
            cancion = resultados[0][1]
            self._imprimir_info_detallada(cancion)
        else:
            print(f"\n❌ No se encontró canción o resultados ambiguos\n")
    
    def _imprimir_info_detallada(self, cancion: Dict) -> None:
        """Imprime información detallada incluyendo tiempos."""
        print(f"\n{'='*70}")
        print(f"📊 INFORMACIÓN DETALLADA")
        print(f"{'='*70}")
        print(f"\n🎤 Título:    {cancion['titulo']}")
        print(f"🎵 Artista:   {cancion['artista']}")
        print(f"📝 Líneas:    {len(cancion['lineas'])}")
        print(f"⏱️  Duración:  {cancion.get('duracion', 'No configurada')} ms")
        print(f"\n{'─'*70}")
        print(f"{'Tiempo':>8} | {'Texto':70}")
        print(f"{'─'*70}\n")
        
        for linea in cancion['lineas']:
            tiempo = linea['tiempo']
            texto = linea['texto'][:67]  # Truncar si es muy largo
            print(f"{tiempo:>7} ms | {texto}")
        
        print(f"\n{'='*70}\n")
    
    def exportar_datos(self, nombre: str) -> Dict:
        """Exporta datos de una canción como JSON."""
        resultados = self.buscar_cancion(nombre)
        
        if isinstance(resultados, str):
            return self.canciones[resultados]
        elif isinstance(resultados, list) and len(resultados) == 1:
            return resultados[0][1]
        else:
            return None


def main():
    parser = argparse.ArgumentParser(
        description='🎤 Sistema de Karaoke - Gestor de canciones',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python karaoke.py list
  python karaoke.py show "bandido"
  python karaoke.py search "alaska"
  python karaoke.py info "20 de enero"
        """
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comando a ejecutar')
    
    # Comando: list
    subparsers.add_parser('list', help='Listar todas las canciones')
    
    # Comando: show
    show_parser = subparsers.add_parser('show', help='Mostrar letra de una canción')
    show_parser.add_argument('cancion', help='Nombre de la canción')
    
    # Comando: search
    search_parser = subparsers.add_parser('search', help='Buscar canción')
    search_parser.add_argument('termino', help='Término de búsqueda')
    
    # Comando: info
    info_parser = subparsers.add_parser('info', help='Información detallada')
    info_parser.add_argument('cancion', help='Nombre de la canción')
    
    # Comando: export
    export_parser = subparsers.add_parser('export', help='Exportar como JSON')
    export_parser.add_argument('cancion', help='Nombre de la canción')
    
    args = parser.parse_args()
    
    # Crear gestor
    gestor = GestorKaraoke()
    
    # Procesar comandos
    if args.comando == 'list' or not args.comando:
        gestor.listar_canciones()
    
    elif args.comando == 'show':
        gestor.mostrar_cancion(args.cancion)
    
    elif args.comando == 'search':
        resultados = gestor.buscar_cancion(args.termino)
        print(f"\n🔍 Resultados para '{args.termino}':\n")
        if isinstance(resultados, str):
            cancion = gestor.canciones[resultados]
            print(f"   ✓ {cancion['titulo']} - {cancion['artista']}\n")
        elif isinstance(resultados, list):
            for clave, datos in resultados:
                print(f"   ✓ {datos['titulo']} - {datos['artista']}")
            print()
        else:
            print("   ❌ No encontrado\n")
    
    elif args.comando == 'info':
        gestor.mostrar_info(args.cancion)
    
    elif args.comando == 'export':
        datos = gestor.exportar_datos(args.cancion)
        if datos:
            print(json.dumps(datos, ensure_ascii=False, indent=2))
        else:
            print(f"❌ No se encontró '{args.cancion}'")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
