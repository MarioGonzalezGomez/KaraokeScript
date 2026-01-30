#!/usr/bin/env python3
"""
Parser de archivo Karaoke.txt
Convierte el archivo de texto con canciones a JSONs individuales
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

class KaraokeParser:
    def __init__(self, input_file: str, output_dir: str = "canciones"):
        self.input_file = input_file
        self.output_dir = output_dir
        self.canciones = []
        
        # Crear directorio de salida si no existe
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def parsear(self) -> List[Dict]:
        """
        Parsea el archivo Karaoke.txt y extrae las canciones.
        Formato esperado:
        "TITULO" ARTISTA
        letra línea 1
        letra línea 2
        ...
        
        (línea en blanco separando canciones)
        """
        with open(self.input_file, 'r', encoding='iso-8859-1') as f:
            lineas_totales = f.readlines()
        
        idx = 0
        while idx < len(lineas_totales):
            linea = lineas_totales[idx].strip()
            
            # Buscar línea de cabecera (con comillas)
            if linea.startswith('"'):
                titulo, artista = self._extraer_titulo_artista(linea)
                
                if titulo and artista:
                    # Recopilar letra hasta la siguiente canción
                    letra = []
                    idx += 1
                    
                    while idx < len(lineas_totales):
                        linea_actual = lineas_totales[idx].rstrip('\n')
                        linea_strip = linea_actual.strip()
                        
                        # Detectar siguiente canción o fin de archivo
                        if linea_strip.startswith('"'):
                            break
                        
                        # Agregar línea si no está vacía
                        if linea_strip:
                            letra.append(linea_strip)
                        
                        idx += 1
                    
                    cancion = {
                        "titulo": titulo,
                        "artista": artista,
                        "letra": letra
                    }
                    
                    self.canciones.append(cancion)
                    continue
            
            idx += 1
        
        return self.canciones
    
    def _extraer_titulo_artista(self, linea: str) -> Tuple[str, str]:
        """
        Extrae título (entre comillas) y artista (después de las comillas).
        Ejemplo: "BANDIDO" AZUCAR MORENO
        """
        # Patrón: "TITULO" ARTISTA
        patron = r'"([^"]+)"\s+(.+)'
        match = re.match(patron, linea)
        
        if match:
            titulo = match.group(1).strip()
            artista = match.group(2).strip()
            return titulo, artista
        
        return None, None
    
    def guardar_jsons(self) -> List[str]:
        """
        Guarda cada canción en un archivo JSON separado.
        Retorna lista de archivos creados.
        """
        archivos_creados = []
        
        for idx, cancion in enumerate(self.canciones, 1):
            # Generar nombre de archivo seguro
            nombre_archivo = self._generar_nombre_archivo(cancion["titulo"])
            ruta_json = os.path.join(self.output_dir, f"{nombre_archivo}.json")
            
            # Crear estructura del JSON
            datos_json = {
                "id": idx,
                "titulo": cancion["titulo"],
                "artista": cancion["artista"],
                "duracion": 0,  # Se completará después
                "lineas": [
                    {
                        "tiempo": 0,  # En milisegundos
                        "texto": linea
                    }
                    for linea in cancion["letra"]
                ]
            }
            
            # Guardar JSON
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=2)
            
            archivos_creados.append(ruta_json)
            print(f"✓ Creado: {ruta_json}")
        
        return archivos_creados
    
    def _generar_nombre_archivo(self, titulo: str) -> str:
        """
        Convierte el título a un nombre de archivo válido.
        Ejemplo: "A QUIEN LE IMPORTA" -> "a_quien_le_importa"
        """
        # Convertir a minúsculas y reemplazar caracteres especiales
        nombre = titulo.lower()
        nombre = re.sub(r'[^\w\s]', '', nombre)  # Quitar caracteres especiales
        nombre = re.sub(r'\s+', '_', nombre)     # Espacios a guiones bajos
        return nombre
    
    def listar_canciones(self) -> None:
        """Imprime lista de canciones parseadas."""
        print(f"\n{'='*60}")
        print(f"Total de canciones encontradas: {len(self.canciones)}")
        print(f"{'='*60}\n")
        
        for idx, cancion in enumerate(self.canciones, 1):
            print(f"{idx:2d}. {cancion['titulo']:30s} - {cancion['artista']}")
        
        print(f"\n{'='*60}\n")


def main():
    # Detectar ruta del archivo Karaoke.txt
    karaoke_file = "Karaoke.txt"
    
    if not os.path.exists(karaoke_file):
        print(f"❌ Error: No se encontró '{karaoke_file}'")
        return
    
    print(f"📖 Parseando '{karaoke_file}'...\n")
    
    # Parsear y generar JSONs
    parser = KaraokeParser(karaoke_file)
    parser.parsear()
    parser.listar_canciones()
    
    print("💾 Guardando archivos JSON...\n")
    archivos = parser.guardar_jsons()
    
    print(f"\n✅ Proceso completado!")
    print(f"   Total de JSONs creados: {len(archivos)}")
    print(f"   Ubicación: {parser.output_dir}/")


if __name__ == "__main__":
    main()
