import socket
import threading
import json
import time

class IPFClient:
    """
    Gestiona la conexión TCP con el servidor IPF.
    Equivalente a TcpConnectionService.cs
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = None
        self.connected = False
        self._lock = threading.Lock()

    def connect(self):
        """Establece conexión con el servidor."""
        with self._lock:
            try:
                if self.sock:
                    self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(2.0) # Timeout de conexión
                self.sock.connect((self.ip, self.port))
                self.connected = True
                print(f"✅ Conectado a IPF en {self.ip}:{self.port}")
                return True
            except Exception as e:
                print(f"❌ Error conectando a IPF: {e}")
                self.connected = False
                return False

    def disconnect(self):
        """Cierra la conexión."""
        with self._lock:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            self.sock = None
            self.connected = False
            print("🔌 Desconectado de IPF")

    def send(self, message):
        """Envía un mensaje UTF-8 al servidor."""
        if not self.connected or not self.sock:
            # Intentar reconectar una vez si se perdió
            if not self.connect():
                return False

        try:
            # Nota: En C# usaban GetBytys(UTF8). Python usa encode('utf-8').
            # A veces IPF necesita un terminador como \n o \r\n, pero el C# original no mostraba uno explícito 
            # más allá del WriteAsync. Asumiremos raw string por ahora.
            data = message.encode('utf-8')
            self.sock.sendall(data)
            return True
        except Exception as e:
            print(f"⚠️ Error enviando datos: {e}")
            self.disconnect()
            return False

class IPFProtocol:
    """
    Clase base para construir comandos IPF (itemset, itemgo).
    Equivalente a IPFMensajesBase.cs
    """
    def __init__(self, db_name="DATABASE"):
        self.db_name = db_name

    def _format_value(self, value):
        """Formatea el valor según su tipo para IPF."""
        if value is None:
            return "0"
        
        val_str = str(value).strip()
        
        # Si ya está entre comillas, devolver tal cual
        if len(val_str) >= 2 and ((val_str.startswith("'") and val_str.endswith("'")) or 
                                  (val_str.startswith('"') and val_str.endswith('"'))):
            return val_str
            
        # Si es número, devolver tal cual
        try:
            float(val_str)
            return val_str
        except ValueError:
            pass
            
        # Si es booleano
        if val_str.lower() in ['true', 'false']:
            return val_str.lower()
            
        # Por defecto, entrecomillar como string
        return f"'{val_str}'"

    def itemset(self, objeto, propiedad, valor=None):
        """Genera el comando itemset."""
        full_obj = f"<{self.db_name}>{objeto}"
        if valor is not None:
            f_val = self._format_value(valor)
            return f"itemset('{full_obj}','{propiedad}',{f_val});"
        else:
            return f"itemset('{full_obj}','{propiedad}');"

    def itemgo(self, objeto, propiedad, valor="0", anim_time=0.0, delay=0.0):
        """Genera el comando itemgo (animación)."""
        full_obj = f"<{self.db_name}>{objeto}"
        f_val = self._format_value(valor)
        return f"itemgo('{full_obj}','{propiedad}',{f_val},{anim_time},{delay});"

    def event_run(self, objeto):
        """Ejecuta un evento EVENT_RUN (play)."""
        return self.itemset(objeto, "EVENT_RUN")

class KaraokeMessages(IPFProtocol):
    """
    Constructor específico de mensajes para Karaoke.
    AQUÍ es donde debes modificar si cambian los objetos en IPF.
    """
    def __init__(self, db_name, root_obj="KARAOKE"):
        super().__init__(db_name)
        self.root_obj = root_obj
        # Sub-objetos (adaptar según tu escena gráfica)
        self.obj_texto = f"{root_obj}/TEXTO" 
        self.obj_visibilidad = f"{root_obj}/VISIBILIDAD" 

    def set_texto(self, texto):
        """Cambia el texto de la línea de karaoke."""
        # Propiedad TEXT_STRING es estándar en IPF para objetos de texto
        return self.itemset(self.obj_texto, "TEXT_STRING", texto)

    def mostrar(self):
        """Muestra el grafismo (Ejemplo: Play de animación In)."""
        return self.event_run(f"{self.root_obj}/ENTRA")

    def ocultar(self):
        """Oculta el grafismo (Ejemplo: Play de animación Out)."""
        return self.event_run(f"{self.root_obj}/SALE")
        
    def reset(self):
        """Resetea estado."""
        return self.itemset(self.root_obj, "RESET")
