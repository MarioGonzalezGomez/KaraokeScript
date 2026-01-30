#!/usr/bin/env python3
"""
Comparador de Sincronizaciones
Compara dos versiones de sincronización (automática vs manual).
Uso: python compare_sync.py <json_automatico> <json_manual>
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class ComparadorSync:
    def __init__(self, archivo_auto: str, archivo_manual: str = None):
        self.archivo_auto = archivo_auto
        self.archivo_manual = archivo_manual
        self.sync_auto = None
        self.sync_manual = None
        
        self.cargar_sincronizaciones()
    
    def cargar_sincronizaciones(self):
        """Carga los archivos de sincronización"""
        if not os.path.exists(self.archivo_auto):
            print(f"❌ Error: No se encontró '{self.archivo_auto}'")
            return
        
        with open(self.archivo_auto, 'r', encoding='utf-8') as f:
            self.sync_auto = json.load(f)
        
        print(f"✓ Sincronización automática cargada: {self.sync_auto['titulo']}")
        
        if self.archivo_manual and os.path.exists(self.archivo_manual):
            with open(self.archivo_manual, 'r', encoding='utf-8') as f:
                self.sync_manual = json.load(f)
            print(f"✓ Sincronización manual cargada")
        else:
            self.sync_manual = None
    
    def mostrar_tabla_interactiva(self) -> None:
        """Muestra tabla interactiva con tiempos"""
        print("\n" + "="*100)
        print(f"SINCRONIZACIÓN: {self.sync_auto['titulo']} - {self.sync_auto['artista']}")
        print("="*100 + "\n")
        
        print(f"{'#':>3} | {'Tiempo (s)':>10} | {'Tiempo (ms)':>10} | {'Texto':<60}")
        print("-" * 100)
        
        for i, linea in enumerate(self.sync_auto['lineas'], 1):
            tiempo_ms = linea['tiempo']
            tiempo_s = tiempo_ms / 1000
            texto = linea['texto'][:57]
            
            if self.sync_manual:
                # Mostrar diferencia si existe versión manual
                tiempo_manual = self.sync_manual['lineas'][i-1]['tiempo']
                dif = abs(tiempo_ms - tiempo_manual)
                dif_ms = f" (±{dif}ms)"
            else:
                dif_ms = ""
            
            print(f"{i:3d} | {tiempo_s:10.2f}s | {tiempo_ms:10d}ms | {texto}{dif_ms}")
        
        print("\n" + "="*100 + "\n")
    
    def mostrar_estadisticas(self) -> None:
        """Muestra estadísticas de la sincronización"""
        print("\n📊 ESTADÍSTICAS")
        print("="*50)
        
        tiempos = [l['tiempo'] for l in self.sync_auto['lineas']]
        
        print(f"\nTotal de líneas:        {len(self.sync_auto['lineas'])}")
        print(f"Duración total:         {self.sync_auto['duracion']/1000:.2f}s")
        print(f"Tiempo por línea (prom): {sum(tiempos)/len(tiempos):.0f}ms")
        print(f"Tiempo mínimo:          {min(tiempos)}ms")
        print(f"Tiempo máximo:          {max(tiempos)}ms")
        
        # Diferencias entre líneas consecutivas
        difs = np.diff([0] + tiempos)
        print(f"Espaciado (promedio):   {np.mean(difs):.0f}ms")
        print(f"Espaciado (mín/máx):    {min(difs):.0f}ms - {max(difs):.0f}ms")
        
        if self.sync_manual:
            print("\n📊 COMPARACIÓN CON MANUAL")
            print("-"*50)
            
            tiempos_manual = [l['tiempo'] for l in self.sync_manual['lineas']]
            diferencias = [abs(a - m) for a, m in zip(tiempos, tiempos_manual)]
            
            print(f"Diferencia promedio:    {np.mean(diferencias):.0f}ms")
            print(f"Diferencia máxima:      {max(diferencias):.0f}ms")
            print(f"Desv. estándar:         {np.std(diferencias):.0f}ms")
        
        print()
    
    def exportar_comparacion(self, ruta: str = None) -> str:
        """Exporta una comparación detallada en CSV"""
        if ruta is None:
            ruta = "comparacion_sync.csv"
        
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write("Línea,Texto,Tiempo Auto (ms),Tiempo Auto (s)")
            
            if self.sync_manual:
                f.write(",Tiempo Manual (ms),Diferencia (ms)\n")
            else:
                f.write("\n")
            
            for i, linea_auto in enumerate(self.sync_auto['lineas']):
                linea_manual = self.sync_manual['lineas'][i] if self.sync_manual else None
                
                tiempo_auto = linea_auto['tiempo']
                texto = linea_auto['texto'].replace(',', ';')  # Escapar comas
                
                f.write(f"{i+1},\"{texto}\",{tiempo_auto},{tiempo_auto/1000:.2f}")
                
                if linea_manual:
                    tiempo_manual = linea_manual['tiempo']
                    dif = abs(tiempo_auto - tiempo_manual)
                    f.write(f",{tiempo_manual},{dif}\n")
                else:
                    f.write("\n")
        
        print(f"✅ Comparación exportada a: {ruta}")
        return ruta


def main():
    parser = argparse.ArgumentParser(
        description='📊 Comparador de Sincronizaciones de Karaoke'
    )
    
    parser.add_argument(
        'automatico',
        help='Archivo JSON de sincronización automática'
    )
    
    parser.add_argument(
        '-m', '--manual',
        help='Archivo JSON de sincronización manual (opcional)',
        default=None
    )
    
    parser.add_argument(
        '-c', '--csv',
        help='Exportar comparación a CSV',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Crear comparador
    comparador = ComparadorSync(args.automatico, args.manual)
    
    # Mostrar tabla
    comparador.mostrar_tabla_interactiva()
    
    # Mostrar estadísticas
    # import numpy as np  # Para estadísticas
    # comparador.mostrar_estadisticas()
    
    # Exportar si se pide
    if args.csv:
        comparador.exportar_comparacion()


if __name__ == "__main__":
    main()
