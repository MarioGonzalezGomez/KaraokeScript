#!/usr/bin/env python3
"""
Analizador Rápido de Audio - Versión Simplificada
Detecta tiempos usando un método más rápido.
Uso: python audio_analyzer_fast.py <archivo_mp3> <archivo_json_cancion>
"""

import json
import os
import sys
import librosa
import numpy as np
from pathlib import Path
import argparse


class AnalizadorAudioRapido:
    def __init__(self, archivo_audio: str, archivo_cancion_json: str):
        self.archivo_audio = archivo_audio
        self.archivo_cancion_json = archivo_cancion_json
        self.audio_y = None
        self.sr = None
        self.cancion = None
        
        self.cargar_audio()
        self.cargar_cancion()
    
    def cargar_audio(self) -> None:
        """Carga el archivo de audio"""
        if not os.path.exists(self.archivo_audio):
            print(f"❌ Error: No se encontró '{self.archivo_audio}'")
            sys.exit(1)
        
        print(f"📀 Cargando audio: {Path(self.archivo_audio).name}")
        try:
            # Cargar con sr=22050 para más velocidad
            self.audio_y, self.sr = librosa.load(self.archivo_audio, sr=22050)
            duracion = librosa.get_duration(y=self.audio_y, sr=self.sr)
            print(f"✓ Audio cargado: {duracion:.2f}s @ {self.sr}Hz")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def cargar_cancion(self) -> None:
        """Carga los datos de la canción"""
        if not os.path.exists(self.archivo_cancion_json):
            print(f"❌ Error: No se encontró '{self.archivo_cancion_json}'")
            sys.exit(1)
        
        with open(self.archivo_cancion_json, 'r', encoding='utf-8') as f:
            self.cancion = json.load(f)
        
        print(f"🎤 {self.cancion['titulo']} - {self.cancion['artista']}")
        print(f"📝 {len(self.cancion['lineas'])} líneas")
    
    def distribuir_tiempos_por_duracion(self) -> None:
        """
        Método simple: distribuir tiempos proporcionales a la duración.
        """
        print("\n⏱️  Calculando tiempos basados en duración...")
        
        duracion_ms = librosa.get_duration(y=self.audio_y, sr=self.sr) * 1000
        num_lineas = len(self.cancion['lineas'])
        
        # Distribuir linealmente
        for i, linea in enumerate(self.cancion['lineas']):
            # Cada línea ocupa un tiempo proporcional
            tiempo = int((i / num_lineas) * duracion_ms)
            linea['tiempo'] = tiempo
        
        self.cancion['duracion'] = int(duracion_ms)
        print(f"✓ Tiempos distribuidos")
    
    def detectar_con_energia_simple(self) -> None:
        """
        Detección simple usando energía del espectrograma.
        MUCHO más rápido que onset_detect.
        """
        print("\n⚡ Detectando cambios de energía (método rápido)...")
        
        # Calcular espectrograma de Mel (baja resolución para velocidad)
        S = librosa.feature.melspectrogram(y=self.audio_y, sr=self.sr, n_mels=20, n_fft=1024)
        
        # Energía por frame
        energy = np.sum(S, axis=0)
        energy = energy / (np.max(energy) + 1e-9)  # Normalizar
        
        # Encontrar picos simples
        threshold = np.mean(energy) + 0.3 * np.std(energy)
        
        # Encontrar dónde cambia la energía significativamente
        delta = np.abs(np.diff(energy))
        delta = np.concatenate([[0], delta])
        
        picos = np.where(delta > threshold)[0]
        
        # Convertir frames a tiempo (ms)
        picos_tiempo = librosa.frames_to_time(picos, sr=self.sr) * 1000
        
        print(f"✓ Encontrados {len(picos)} picos potenciales")
        
        # Alinear con líneas de la canción
        self._alinear_con_lineas(picos_tiempo)
    
    def _alinear_con_lineas(self, picos_tiempo: np.ndarray) -> None:
        """Alinea los picos detectados con las líneas"""
        num_lineas = len(self.cancion['lineas'])
        picos_tiempo = np.sort(picos_tiempo)
        
        print(f"🔗 Alineando {len(picos_tiempo)} picos con {num_lineas} líneas...")
        
        if len(picos_tiempo) >= num_lineas * 0.5:
            # Tenemos suficientes picos, distribuir
            indices = np.linspace(0, len(picos_tiempo) - 1, num_lineas, dtype=int)
            
            for i, idx in enumerate(indices):
                if i < len(self.cancion['lineas']):
                    self.cancion['lineas'][i]['tiempo'] = int(picos_tiempo[idx])
        else:
            # Pocos picos, usar distribución lineal
            duracion_ms = picos_tiempo[-1] if len(picos_tiempo) > 0 else \
                         librosa.get_duration(y=self.audio_y, sr=self.sr) * 1000
            
            for i in range(num_lineas):
                tiempo = int((i / num_lineas) * duracion_ms)
                self.cancion['lineas'][i]['tiempo'] = tiempo
        
        # Calcular duración
        self.cancion['duracion'] = max([l['tiempo'] for l in self.cancion['lineas']] + [0])
        print(f"✓ Alineamiento completado")
    
    def mostrar_resultado(self) -> None:
        """Muestra una muestra del resultado"""
        print("\n" + "="*80)
        print("RESULTADO DE LA SINCRONIZACIÓN")
        print("="*80 + "\n")
        
        print(f"{'#':>3} | {'Tiempo (ms)':>12} | {'Texto':<60}")
        print("-" * 80)
        
        for i in range(min(15, len(self.cancion['lineas']))):
            linea = self.cancion['lineas'][i]
            tiempo_fmt = f"{linea['tiempo']}ms ({linea['tiempo']/1000:.2f}s)"
            texto = linea['texto'][:57]
            print(f"{i+1:3d} | {tiempo_fmt:>12} | {texto}")
        
        if len(self.cancion['lineas']) > 15:
            print(f"... ({len(self.cancion['lineas']) - 15} líneas más)")
        
        print("\n" + "="*80 + "\n")
    
    def guardar(self, ruta: str = None) -> str:
        """Guarda el resultado"""
        if ruta is None:
            nombre_base = Path(self.archivo_cancion_json).stem
            ruta = f"canciones/{nombre_base}_sincronizada_auto.json"
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.cancion, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Guardado en: {Path(ruta).name}\n")
        return ruta
    
    def ejecutar(self) -> str:
        """Ejecuta el análisis"""
        print("\n" + "="*80)
        print("ANALIZADOR RÁPIDO DE AUDIO (Método Simple)")
        print("="*80 + "\n")
        
        # Usar método rápido
        self.detectar_con_energia_simple()
        
        # Mostrar resultado
        self.mostrar_resultado()
        
        # Guardar
        ruta = self.guardar()
        
        print(f"💡 Para refinar manualmente:")
        print(f"   .\\\.venv\\Scripts\\python.exe sync_editor.py {ruta}\n")
        
        return ruta


def main():
    parser = argparse.ArgumentParser(
        description='⚡ Analizador Rápido de Audio (Versión Simplificada)'
    )
    
    parser.add_argument('audio', help='Ruta al MP3')
    parser.add_argument('cancion', help='Ruta al JSON de la canción')
    parser.add_argument('-o', '--output', help='Ruta de salida')
    
    args = parser.parse_args()
    
    analizador = AnalizadorAudioRapido(args.audio, args.cancion)
    analizador.ejecutar()


if __name__ == "__main__":
    main()
