#!/usr/bin/env python3
"""
Editor de Sincronización de Karaoke
Permite asignar tiempos a las líneas de una canción de forma interactiva.
Uso: python sync_editor.py <nombre_cancion>
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import argparse


class SyncEditor:
    def __init__(self, cancion_json: str):
        self.cancion_path = cancion_json
        self.cancion = None
        self.cargar_cancion()
    
    def cargar_cancion(self) -> None:
        """Carga la canción desde JSON."""
        if not os.path.exists(self.cancion_path):
            print(f"❌ Error: No se encontró '{self.cancion_path}'")
            return
        
        with open(self.cancion_path, 'r', encoding='utf-8') as f:
            self.cancion = json.load(f)
    
    def mostrar_menu(self) -> None:
        """Muestra el menú principal."""
        if not self.cancion:
            return
        
        print(f"\n{'='*70}")
        print(f"🎤 EDITOR DE SINCRONIZACIÓN")
        print(f"   Canción: {self.cancion['titulo']} - {self.cancion['artista']}")
        print(f"   Total de líneas: {len(self.cancion['lineas'])}")
        print(f"{'='*70}\n")
        
        print("Opciones:")
        print("  1. Ver letra completa con tiempos")
        print("  2. Sincronizar línea por línea (manual)")
        print("  3. Ajustar tiempo de una línea específica")
        print("  4. Cargar tiempos desde archivo")
        print("  5. Generar tiempos automáticamente (estimado)")
        print("  6. Guardar cambios")
        print("  7. Salir")
        print()
    
    def ver_letra_completa(self) -> None:
        """Muestra la letra con tiempos actuales."""
        print(f"\n{'='*70}")
        print(f"  {self.cancion['titulo']} - {self.cancion['artista']}")
        print(f"{'='*70}\n")
        print(f"{'Línea':>5} | {'Tiempo (ms)':>12} | Texto")
        print(f"{'-'*70}\n")
        
        for idx, linea in enumerate(self.cancion['lineas'], 1):
            tiempo = linea['tiempo']
            texto = linea['texto'][:50]  # Truncar si es muy largo
            print(f"{idx:5d} | {tiempo:12d} | {texto}")
        
        print()
    
    def sincronizar_interactivo(self) -> None:
        """Sincroniza línea por línea de forma interactiva."""
        print(f"\n{'='*70}")
        print("SINCRONIZACIÓN INTERACTIVA")
        print("Ingresa el tiempo (en milisegundos) para cada línea")
        print("Presiona Enter para saltar, 'q' para cancelar")
        print(f"{'='*70}\n")
        
        for idx, linea in enumerate(self.cancion['lineas'], 1):
            print(f"\n[{idx}/{len(self.cancion['lineas'])}] {linea['texto'][:60]}")
            
            try:
                entrada = input("Tiempo (ms) [actual: {}]: ".format(linea['tiempo'])).strip()
                
                if entrada.lower() == 'q':
                    print("❌ Sincronización cancelada")
                    return
                
                if entrada:
                    tiempo = int(entrada)
                    self.cancion['lineas'][idx - 1]['tiempo'] = tiempo
                    print(f"✓ Asignado: {tiempo} ms")
            except ValueError:
                print("⚠️  Entrada inválida, saltando...")
    
    def ajustar_tiempo_especifico(self) -> None:
        """Ajusta el tiempo de una línea específica."""
        try:
            num_linea = int(input("\n¿Qué línea deseas ajustar? (1-{}): ".format(
                len(self.cancion['lineas'])
            ))) - 1
            
            if 0 <= num_linea < len(self.cancion['lineas']):
                linea = self.cancion['lineas'][num_linea]
                print(f"\nLínea: {linea['texto'][:60]}")
                print(f"Tiempo actual: {linea['tiempo']} ms")
                
                nuevo_tiempo = input("Nuevo tiempo (ms): ").strip()
                if nuevo_tiempo:
                    linea['tiempo'] = int(nuevo_tiempo)
                    print(f"✓ Actualizado a {linea['tiempo']} ms")
            else:
                print("❌ Número de línea inválido")
        except ValueError:
            print("❌ Entrada inválida")
    
    def generar_tiempos_automaticos(self) -> None:
        """
        Genera tiempos automáticos estimados.
        Asume que aproximadamente 3 líneas por segundo.
        """
        duracion_ms = int(input("\n¿Cuál es la duración total de la canción (segundos)? "))
        duracion_ms *= 1000
        
        num_lineas = len(self.cancion['lineas'])
        tiempo_por_linea = duracion_ms / num_lineas
        
        print(f"\nGenerando tiempos ({tiempo_por_linea:.0f} ms por línea)...\n")
        
        for idx, linea in enumerate(self.cancion['lineas']):
            linea['tiempo'] = int(idx * tiempo_por_linea)
        
        print(f"✓ {num_lineas} tiempos generados")
        self.ver_letra_completa()
    
    def cargar_desde_archivo(self) -> None:
        """Carga tiempos desde un archivo de tiempos."""
        archivo = input("\n¿Nombre del archivo de tiempos? (formato: tiempo,ms por línea): ").strip()
        
        if not os.path.exists(archivo):
            print(f"❌ Archivo '{archivo}' no encontrado")
            return
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                tiempos = []
                for linea in f:
                    linea = linea.strip()
                    if linea and linea.isdigit():
                        tiempos.append(int(linea))
            
            if len(tiempos) != len(self.cancion['lineas']):
                print(f"⚠️  Advertencia: Se encontraron {len(tiempos)} tiempos,")
                print(f"    pero la canción tiene {len(self.cancion['lineas'])} líneas")
            
            for idx, tiempo in enumerate(tiempos):
                if idx < len(self.cancion['lineas']):
                    self.cancion['lineas'][idx]['tiempo'] = tiempo
            
            print(f"✓ {len(tiempos)} tiempos cargados")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def guardar_cambios(self) -> None:
        """Guarda los cambios en el JSON."""
        try:
            with open(self.cancion_path, 'w', encoding='utf-8') as f:
                json.dump(self.cancion, f, ensure_ascii=False, indent=2)
            
            # También calcular duración
            tiempos = [l['tiempo'] for l in self.cancion['lineas']]
            duracion = max(tiempos) if tiempos else 0
            self.cancion['duracion'] = duracion
            
            # Guardar de nuevo con duración actualizada
            with open(self.cancion_path, 'w', encoding='utf-8') as f:
                json.dump(self.cancion, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Cambios guardados en '{self.cancion_path}'")
            print(f"   Duración detectada: {duracion} ms ({duracion/1000:.2f} segundos)")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
    
    def ejecutar(self) -> None:
        """Ejecuta el loop principal del editor."""
        if not self.cancion:
            return
        
        while True:
            self.mostrar_menu()
            
            try:
                opcion = input("Selecciona una opción (1-7): ").strip()
                
                if opcion == '1':
                    self.ver_letra_completa()
                elif opcion == '2':
                    self.sincronizar_interactivo()
                elif opcion == '3':
                    self.ajustar_tiempo_especifico()
                elif opcion == '4':
                    self.cargar_desde_archivo()
                elif opcion == '5':
                    self.generar_tiempos_automaticos()
                elif opcion == '6':
                    self.guardar_cambios()
                elif opcion == '7':
                    print("\n👋 Hasta luego!\n")
                    break
                else:
                    print("❌ Opción inválida")
            except KeyboardInterrupt:
                print("\n\n👋 Hasta luego!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='🎤 Editor de Sincronización de Karaoke',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python sync_editor.py canciones/bandido.json
  python sync_editor.py canciones/y_yo_te_besé.json
        """
    )
    
    parser.add_argument(
        'cancion',
        help='Ruta al archivo JSON de la canción'
    )
    
    args = parser.parse_args()
    
    editor = SyncEditor(args.cancion)
    editor.ejecutar()


if __name__ == "__main__":
    main()
