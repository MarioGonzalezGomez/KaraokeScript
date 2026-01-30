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
    Implementa: Entra, Cambio de frases, Sale.
    """
    def __init__(self, db_name, root_obj="KARAOKE"):
        super().__init__(db_name)
        self.root_obj = root_obj
        # Objetos específicos definidos por el usuario
        self.obj_texto_l1 = "KaraokeL1" 
        self.obj_texto_l2 = "KaraokeL2"
        self.obj_efecto_l1 = "KARAOKEEL1"
        self.obj_efecto_l2 = "KARAOKEEL2"
        
        self.evt_entra = f"{root_obj}/ENTRA"
        self.evt_sale = f"{root_obj}/SALE"

    def split_smart(self, text, max_len=26):
        """
        Divide el texto en dos líneas balanceadas si excede max_len.
        Si cabe en una, devuelve ("", text).
        """
        text = text.strip()
        if len(text) <= max_len:
            return "", text
        
        # Buscar el espacio más cercano al centro para balancear
        center = len(text) // 2
        best_split = -1
        min_dist = len(text)
        
        for i, char in enumerate(text):
            if char == ' ':
                dist = abs(i - center)
                if dist < min_dist:
                    min_dist = dist
                    best_split = i
        
        if best_split != -1:
            line1 = text[:best_split].strip()
            line2 = text[best_split:].strip()
            return line1, line2
        else:
            # Fallback forzoso si no hay espacios
            return text[:center], text[center:]

    def entra(self, texto_completo):
        """
        Secuencia de ENTRADA (Primer verso).
        itemset("KaraokeL1", "MAP_STRING_PAR", 'Linea1Texto')
        itemset("KaraokeL2", "MAP_STRING_PAR", 'Linea2Texto')
        itemset("KARAOKE/ENTRA", "EVENT_RUN")
        """
        l1, l2 = self.split_smart(texto_completo)
        
        cmds = []
        cmds.append(self.itemset(self.obj_texto_l1, "MAP_STRING_PAR", l1))
        cmds.append(self.itemset(self.obj_texto_l2, "MAP_STRING_PAR", l2))
        cmds.append(self.event_run(self.evt_entra))
        
        return "".join(cmds)

    def cambio(self, texto_completo):
        """
        Secuencia de CAMBIO DE FRASE.
        itemset("KARAOKEEL1", "TEXT_FX_GOOUT")
        itemset("KARAOKEEL2", "TEXT_FX_GOOUT")
        itemgo("KaraokeL1", "MAP_STRING_PAR", 'Linea1TextoNueva', 0, 0.15)
        itemgo("KaraokeL2", "MAP_STRING_PAR", 'Linea2TextoNueva', 0, 0.15)
        itemgo("KARAOKEEL1", "TEXT_FX_GOIN", 0, 0.16)
        itemgo("KARAOKEEL2", "TEXT_FX_GOIN", 0, 0.16)
        """
        l1, l2 = self.split_smart(texto_completo)
        
        cmds = []
        # Go Out
        cmds.append(self.itemset(self.obj_efecto_l1, "TEXT_FX_GOOUT"))
        cmds.append(self.itemset(self.obj_efecto_l2, "TEXT_FX_GOOUT"))
        
        # Change Text (con delay 0.15s)
        # Nota: itemgo(obj, prop, val, anim_time, delay)
        # Asumimos anim_time=0 como en el ejemplo del usuario
        cmds.append(self.itemgo(self.obj_texto_l1, "MAP_STRING_PAR", l1, 0, 0.15))
        cmds.append(self.itemgo(self.obj_texto_l2, "MAP_STRING_PAR", l2, 0, 0.15))
        
        # Go In (con delay 0.16s)
        cmds.append(self.itemgo(self.obj_efecto_l1, "TEXT_FX_GOIN", 0, 0.16))
        cmds.append(self.itemgo(self.obj_efecto_l2, "TEXT_FX_GOIN", 0, 0.16))
        
        return "".join(cmds)

    def sale(self):
        """
        Secuencia de SALIDA.
        itemset("KARAOKE/SALE", "EVENT_RUN")
        """
        return self.event_run(self.evt_sale)
        
    # Alias / Compatibilidad si fuera necesario
    def reset(self):
        return self.sale()
