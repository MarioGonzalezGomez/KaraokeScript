#!/usr/bin/env python3
"""
Analizador Automático de Audio para Karaoke
Detecta tiempos de líneas usando análisis de audio.
Uso: python audio_analyzer.py <archivo_mp3> <archivo_json_cancion>
"""

import json
import os
import sys
import librosa
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class AnalizadorAudio:
    def __init__(self, archivo_audio: str, archivo_cancion_json: str):
        self.archivo_audio = archivo_audio
        self.archivo_cancion_json = archivo_cancion_json
        self.audio_y = None
        self.sr = None
        self.cancion = None
        
        self.cargar_audio()
        self.cargar_cancion()
    
    def cargar_audio(self) -> None:
        """Carga el archivo de audio usando librosa"""
        if not os.path.exists(self.archivo_audio):
            print(f"❌ Error: No se encontró '{self.archivo_audio}'")
            sys.exit(1)
        
        print(f"📀 Cargando audio: {self.archivo_audio}")
        try:
            self.audio_y, self.sr = librosa.load(self.archivo_audio, sr=None)
            duracion = librosa.get_duration(y=self.audio_y, sr=self.sr)
            print(f"✓ Audio cargado: {duracion:.2f} segundos @ {self.sr} Hz")
        except Exception as e:
            print(f"❌ Error cargando audio: {e}")
            sys.exit(1)
    
    def cargar_cancion(self) -> None:
        """Carga los datos de la canción desde JSON"""
        if not os.path.exists(self.archivo_cancion_json):
            print(f"❌ Error: No se encontró '{self.archivo_cancion_json}'")
            sys.exit(1)
        
        with open(self.archivo_cancion_json, 'r', encoding='utf-8') as f:
            self.cancion = json.load(f)
        
        print(f"🎤 Canción: {self.cancion['titulo']} - {self.cancion['artista']}")
        print(f"📝 Líneas: {len(self.cancion['lineas'])}")
    
    def detectar_onsets(self, units='ms') -> np.ndarray:
        """
        Detecta puntos de ataque (onsets) en el audio.
        Estos indican cambios rítmicos donde comienzan nuevas líneas.
        """
        print("\n🔍 Detectando puntos de ataque (onsets)...")
        
        # Calcular espectrograma
        D = librosa.stft(self.audio_y)
        S = np.abs(D)
        
        # Detectar onsets
        onset_frames = librosa.onset.onset_detect(S=S, sr=self.sr, units='frames')
        
        # Convertir a tiempo (ms)
        if units == 'ms':
            onset_times = librosa.frames_to_time(onset_frames, sr=self.sr) * 1000
        else:
            onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)
        
        print(f"✓ Encontrados {len(onset_times)} onsets")
        return np.array(onset_times)
    
    def detectar_energia(self, units='ms') -> np.ndarray:
        """
        Detecta cambios de energía en el audio.
        Útil para encontrar dónde comienza cada verso.
        """
        print("\n⚡ Detectando cambios de energía...")
        
        # Calcular energía frame por frame
        S = librosa.feature.melspectrogram(y=self.audio_y, sr=self.sr)
        energy = np.sum(S, axis=0)
        
        # Normalizar
        energy = energy / np.max(energy)
        
        # Encontrar picos de energía (lugares donde la voz es fuerte)
        # Usamos un threshold dinámico
        threshold = np.mean(energy) + 0.5 * np.std(energy)
        picos = np.where(energy > threshold)[0]
        
        # Obtener posiciones únicas (agrupar cercanas)
        if len(picos) > 0:
            # Agrupar picos que están muy cerca
            picos_agrupados = [picos[0]]
            for p in picos[1:]:
                if p - picos_agrupados[-1] > self.sr // 512 * 0.5:  # Más de 0.5s de diferencia
                    picos_agrupados.append(p)
            
            picos_agrupados = np.array(picos_agrupados)
        else:
            picos_agrupados = np.array([])
        
        # Convertir a tiempo
        if units == 'ms':
            energy_times = librosa.frames_to_time(picos_agrupados, sr=self.sr) * 1000
        else:
            energy_times = librosa.frames_to_time(picos_agrupados, sr=self.sr)
        
        print(f"✓ Encontrados {len(energy_times)} picos de energía")
        return np.array(energy_times)
    
    def detectar_rms(self, units='ms') -> np.ndarray:
        """
        Detecta cambios en RMS (Root Mean Square).
        Bueno para encontrar dónde hay voz vs. silencio.
        """
        print("\n🔊 Detectando cambios RMS...")
        
        # Calcular RMS (energía)
        S = librosa.feature.melspectrogram(y=self.audio_y, sr=self.sr)
        rms = librosa.feature.rms(S=S)[0]
        
        # Normalizar
        rms = rms / np.max(rms)
        
        # Encontrar cambios (derivada)
        delta_rms = np.abs(np.diff(rms))
        
        # Threshold
        threshold = np.mean(delta_rms) + np.std(delta_rms)
        cambios = np.where(delta_rms > threshold)[0]
        
        # Filtrar cambios muy cercanos
        if len(cambios) > 0:
            cambios_filtrados = [cambios[0]]
            for c in cambios[1:]:
                if c - cambios_filtrados[-1] > len(rms) * 0.05:  # Al menos 5% del audio
                    cambios_filtrados.append(c)
            cambios = np.array(cambios_filtrados)
        
        # Convertir a tiempo
        if units == 'ms':
            rms_times = librosa.frames_to_time(cambios, sr=self.sr) * 1000
        else:
            rms_times = librosa.frames_to_time(cambios, sr=self.sr)
        
        print(f"✓ Encontrados {len(rms_times)} cambios RMS")
        return np.array(rms_times)
    
    def alinear_tiempos(self, tiempos_detectados: np.ndarray) -> Dict[int, int]:
        """
        Alinea los tiempos detectados con las líneas de la canción.
        Usa algoritmo simple: asigna cada tiempo al número correspondiente de línea.
        """
        print("\n🔗 Alineando tiempos detectados con líneas...")
        
        num_lineas = len(self.cancion['lineas'])
        tiempos_detectados = np.sort(tiempos_detectados)
        
        alineamiento = {}
        
        # Si tenemos más tiempos que líneas, usar estrategia de agrupamiento
        if len(tiempos_detectados) >= num_lineas:
            # Dividir los tiempos en num_lineas grupos
            indices = np.linspace(0, len(tiempos_detectados) - 1, num_lineas + 1, dtype=int)
            
            for i in range(num_lineas):
                inicio_grupo = indices[i]
                fin_grupo = indices[i + 1]
                
                if inicio_grupo < len(tiempos_detectados):
                    # Usar el primer tiempo del grupo
                    tiempo = int(tiempos_detectados[inicio_grupo])
                    alineamiento[i] = tiempo
        else:
            # Menos tiempos que líneas: distribuir proporcionalmente
            duracion_audio = librosa.get_duration(y=self.audio_y, sr=self.sr) * 1000
            paso = duracion_audio / num_lineas
            
            for i in range(num_lineas):
                tiempo = int(i * paso)
                alineamiento[i] = tiempo
        
        print(f"✓ Alineadas {len(alineamiento)} líneas")
        return alineamiento
    
    def combinar_metodos(self) -> Dict[int, int]:
        """
        Combina múltiples métodos de detección para obtener mejores resultados.
        """
        print("\n" + "="*70)
        print("COMBINANDO MÚLTIPLES MÉTODOS DE DETECCIÓN")
        print("="*70)
        
        # Ejecutar todos los métodos
        onsets = self.detectar_onsets()
        energia = self.detectar_energia()
        rms = self.detectar_rms()
        
        # Combinar todos los tiempos
        todos_tiempos = np.concatenate([onsets, energia, rms])
        todos_tiempos = np.sort(todos_tiempos)
        
        # Agrupar tiempos similares (dentro de 100ms)
        tiempos_agrupados = []
        if len(todos_tiempos) > 0:
            grupo_actual = [todos_tiempos[0]]
            
            for t in todos_tiempos[1:]:
                if t - grupo_actual[-1] < 100:  # Menos de 100ms
                    grupo_actual.append(t)
                else:
                    # Promediar el grupo actual
                    tiempos_agrupados.append(int(np.mean(grupo_actual)))
                    grupo_actual = [t]
            
            # Agregar último grupo
            if grupo_actual:
                tiempos_agrupados.append(int(np.mean(grupo_actual)))
        
        tiempos_agrupados = np.array(tiempos_agrupados)
        print(f"\n✓ {len(todos_tiempos)} picos combinados en {len(tiempos_agrupados)} puntos principales")
        
        # Alinear con líneas de la canción
        return self.alinear_tiempos(tiempos_agrupados)
    
    def aplicar_tiempos(self, alineamiento: Dict[int, int]) -> None:
        """
        Aplica los tiempos calculados a las líneas de la canción.
        """
        print("\n" + "="*70)
        print("APLICANDO TIEMPOS A LAS LÍNEAS")
        print("="*70 + "\n")
        
        for idx, tiempo in alineamiento.items():
            if idx < len(self.cancion['lineas']):
                self.cancion['lineas'][idx]['tiempo'] = tiempo
        
        # Calcular duración de la canción
        duracion = max([l['tiempo'] for l in self.cancion['lineas']] + [0])
        self.cancion['duracion'] = duracion
        
        # Mostrar muestra
        print(f"{'Línea':>5} | {'Tiempo':>8} | {'Texto':60}")
        print("-" * 80)
        for i in range(min(10, len(self.cancion['lineas']))):
            linea = self.cancion['lineas'][i]
            print(f"{i+1:5d} | {linea['tiempo']:8d}ms | {linea['texto'][:60]}")
        
        if len(self.cancion['lineas']) > 10:
            print(f"... ({len(self.cancion['lineas']) - 10} líneas más)")
    
    def guardar_resultado(self, ruta_salida: str = None) -> str:
        """
        Guarda los tiempos sincronizados en un archivo JSON.
        """
        if ruta_salida is None:
            # Generar nombre de salida automático
            nombre_base = Path(self.archivo_cancion_json).stem
            ruta_salida = f"canciones/{nombre_base}_sincronizada.json"
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(self.cancion, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Resultado guardado en: {ruta_salida}")
        return ruta_salida
    
    def mostrar_estadisticas(self) -> None:
        """Muestra estadísticas de la sincronización."""
        print("\n" + "="*70)
        print("ESTADÍSTICAS")
        print("="*70)
        
        duracion_audio = librosa.get_duration(y=self.audio_y, sr=self.sr) * 1000
        tiempos = [l['tiempo'] for l in self.cancion['lineas']]
        
        print(f"\nDuración del audio:     {duracion_audio/1000:.2f} segundos")
        print(f"Duración detectada:     {max(tiempos)/1000:.2f} segundos")
        print(f"Número de líneas:       {len(self.cancion['lineas'])}")
        print(f"Tiempo promedio/línea:  {np.mean(np.diff([0] + tiempos)):.0f}ms")
        print(f"Tiempo mín/máx:         {min(tiempos)}ms - {max(tiempos)}ms")
        
        print("\n" + "="*70 + "\n")
    
    def ejecutar(self, guardar=True) -> str:
        """Ejecuta el análisis completo."""
        print("\n" + "="*70)
        print("ANALIZADOR AUTOMÁTICO DE AUDIO PARA KARAOKE")
        print("="*70 + "\n")
        
        # Análisis
        alineamiento = self.combinar_metodos()
        
        # Aplicar tiempos
        self.aplicar_tiempos(alineamiento)
        
        # Estadísticas
        self.mostrar_estadisticas()
        
        # Guardar
        if guardar:
            ruta = self.guardar_resultado()
            print(f"✅ Sincronización automática completada")
            print(f"   Puedes refinarla manualmente con:")
            print(f"   python sync_editor.py {ruta}\n")
            return ruta
        
        return None


def main():
    parser = argparse.ArgumentParser(
        description='🎵 Analizador Automático de Audio para Karaoke',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python audio_analyzer.py "C:\\ruta\\bandido.mp3" canciones/bandido.json
  python audio_analyzer.py "audio/obsesion.mp3" canciones/obsesión.json
        """
    )
    
    parser.add_argument(
        'audio',
        help='Ruta al archivo de audio MP3/WAV'
    )
    
    parser.add_argument(
        'cancion',
        help='Ruta al archivo JSON de la canción'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Ruta de salida para el JSON sincronizado (opcional)',
        default=None
    )
    
    parser.add_argument(
        '-n', '--no-guardar',
        action='store_true',
        help='No guardar el resultado, solo mostrar'
    )
    
    args = parser.parse_args()
    
    # Crear analizador y ejecutar
    analizador = AnalizadorAudio(args.audio, args.cancion)
    analizador.ejecutar(guardar=not args.no_guardar)


if __name__ == "__main__":
    main()
