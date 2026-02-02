#!/usr/bin/env python3
"""
Parser de archivo Karaoke.txt
Convierte el archivo de texto con canciones a JSONs individuales
"""

import json
import re
import os
import glob
from pathlib import Path
from typing import Dict, List, Tuple

class KaraokeParser:
    def __init__(self, input_file: str, output_dir: str = "canciones"):
        self.input_file = input_file
        self.output_dir = output_dir
        self.canciones = []
        
        # Crear directorio de salida si no existe
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        # Limpiar ficheros antiguos
        self._limpiar_directorio()
    
    def _limpiar_directorio(self):
        print(f"Limpiando directorio {self.output_dir}...")
        files = glob.glob(os.path.join(self.output_dir, "*.json"))
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print(f"Error borrando {f}: {e}")

    def parsear(self) -> List[Dict]:
        """
        Parsea el archivo txt y extrae las canciones.
        Intenta UTF-8 y fallback a Latin-1.
        """
        content = ""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print("UTF-8 falló, intentando ISO-8859-1...")
            with open(self.input_file, 'r', encoding='iso-8859-1') as f:
                content = f.read()

        lineas_totales = content.splitlines()
        
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
                        linea_actual = lineas_totales[idx] # No hacemos strip aun para ver si es vacia
                        linea_strip = linea_actual.strip()
                        
                        # Detectar siguiente canción (si empieza por comillas y parece cabecera)
                        # OJO: A veces una linea de letra podria empezar por comillas (dialogo code), 
                        # pero el formato dice titulo entre comillas al principio. 
                        # Asumimos que dentro de la letra NO hay lineas que sean exactamente "TITULO" ARTISTA
                        if linea_strip.startswith('"') and self._es_cabecera(linea_strip):
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
                    # No incrementamos idx aquí porque el loop interno ya nos dejó en la siguiente cabecera (o fin)
                    continue
            
            idx += 1
        
        return self.canciones
    
    def _es_cabecera(self, linea: str) -> bool:
        # Check rápido para ver si cumple patrón de cabecera
        return bool(re.match(r'"([^"]+)"\s+(.+)', linea))
    
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
            # print(f"✓ Creado: {ruta_json}")
        
        return archivos_creados
    
    def _generar_nombre_archivo(self, titulo: str) -> str:
        """
        Convierte el título a un nombre de archivo válido.
        Ejemplo: "A QUIEN LE IMPORTA" -> "a_quien_le_importa"
        """
        # Convertir a minúsculas y reemplazar caracteres especiales
        nombre = titulo.lower()
        # Mapeo de tildes simple
        replacements = (
            ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
            ("ñ", "n"), ("ü", "u")
        )
        for a, b in replacements:
            nombre = nombre.replace(a, b)
            
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
    # Detectar ruta del archivo
    karaoke_file = "CancionesBenidorm.txt"
    # Si no existe, probar con karaoke.txt por compatibilidad
    if not os.path.exists(karaoke_file):
        if os.path.exists("Karaoke.txt"):
            karaoke_file = "Karaoke.txt"
        else:
            print(f"❌ Error: No se encontró '{karaoke_file}' ni 'Karaoke.txt'")
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
