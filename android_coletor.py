# Utilitários para coletar processos Android via ADB para a simulação
import re, subprocess, math
from typing import List, Tuple, Dict
from models.processo import  Processo

# ---------- ADB helpers ----------
#Executa um comando de shell e retorna a saída como string
def _run(cmd):
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return out.decode("utf-8", "replace")

#Retorna lista [(serial, status, resto)], ignorando header/linhas vazias.
def adb_devices():
    out = _run(["adb", "devices"])
    devs = []
    lines = out.strip().splitlines()

    # pula "List of devices attached"
    for line in lines[1:]:                    
        s = line.strip()
        if not s:
            continue
        parts = s.split()
        serial = parts[0]
        status = parts[1] if len(parts) > 1 else ""
        extra = " ".join(parts[2:]) if len(parts) > 2 else ""
        devs.append((serial, status, extra))
    return devs

#Considera conectado se existir AO MENOS um device com status exatamente 'device'. Ignora 'offline', 'unauthorized', etc.
def adb_ok():
    try:
        devs = adb_devices()
        return any(status == "device" for _, status, _ in devs)
    except Exception:
        return False

# ---------- Parsers ----------
#Regex para extrair PID/CPU%/NAME de uma linha do 'top' (formato pode variar por ROM)
TOP_LINE = re.compile(r"""
    ^\s*(\d+)\s+        # PID
    (?:(\S+)\s+){1,3}   # TTY/USER/PR podem variar
    (\d+)%\s+           # CPU%
    .*?                 # pula colunas intermediárias
    ([^\s]+)$           # NAME (pasta/process name, ex: com.whatsapp)
""", re.X)

# Regex para cabeçalho de 'dumpsys cpuinfo' agregada
CPUINFO_LINE = re.compile(r"""
    ^\s*                # inicio
    (?P<cpu>\d+(?:\.\d+)?)%?\s+cpu\s+used\s+by\s+app\s+:
""", re.X)

# Regex para cada linha de processo em 'dumpsys cpuinfo'
CPUINFO_PROC = re.compile(r"""
    ^\s*(?P<pct>\d+(?:\.\d+)?)%\s+(?P<name>.+)$
""", re.X)

#Retorna [(nome, cpu_percent), ...] usando 'adb shell top -n 1 -m N'.
def coletar_top(max_procs: int = 20) -> List[Tuple[str, float]]:
    out = _run(["adb", "shell", "top", "-n", "1", "-m", str(max_procs)])
    rows = []
    for line in out.splitlines():
        #Muitos Androids trazem no final da linha o NAME (pacote)
        m = re.search(r"(\d+)%\s+([a-zA-Z0-9._:-]+)$", line)
        if m:
            cpu = float(m.group(1))
            name = m.group(2)
            rows.append((name, cpu))
            continue
        #Fallback: regex mais rígida para formatos diferentes
        m2 = TOP_LINE.match(line)
        if m2:
            cpu = float(m2.group(3))
            name = m2.group(4)
            rows.append((name, cpu))
    #Ordena por uso de CPU (desc) e limita ao topo
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:max_procs]

#Fallback/Complemento via 'adb shell dumpsys cpuinfo' (mais estável para nomes).
def coletar_cpuinfo(max_procs: int = 20) -> List[Tuple[str, float]]:
    out = _run(["adb", "shell", "dumpsys", "cpuinfo"])
    rows = []
    for line in out.splitlines():
        m = CPUINFO_PROC.match(line.strip())
        if m:
            pct = float(m.group("pct"))
            name = m.group("name").strip()
            rows.append((name, pct))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:max_procs]

# ---------- Mapear para cenário ----------
"""
    Coleta processos Android via ADB, transforma em chegada/duração para o simulador.
    - janela_seg: janela hipotética de observação (para transformar %CPU em 'tempo de CPU').
    - top_n: quantos processos considerar.
    Retorna (nome_cenario, lista_processos)
      onde cada processo: {"chegada": t, "duracao": d, "nome": "com.app"}
"""
def gerar_cenario_android_via_adb(janela_seg: float = 5.0, top_n: int = 12) -> Tuple[str, List[Dict]]:
    if not adb_ok():
    # Tenta uma chamada simples para forçar conexão; se falhar, aborta
        try:
            _ = _run(["adb", "shell", "echo", "ok"])
        except subprocess.CalledProcessError:
            raise RuntimeError("ADB não está conectado (adb devices). Verifique depuração USB e autorização RSA.")
    
    # Tenta 'top'; se vier vazio, usa 'cpuinfo' como fallback
    procs = coletar_top(top_n)
    if not procs:
        procs = coletar_cpuinfo(top_n)

    #Converte %CPU dentro da janela para "tempo de CPU" da simulação
    #Ex.: 20% em 5s => 1.0s de CPU
    processos: List[Processo] = []
    chegada_tick = 0

    # Fator de escala: 0.1s de CPU -> 1 unidade (ajuste conforme a simulação)
    FATOR = 10.0  # 1s * 10 = 10 “quanta”

    for i, (name, cpu_pct) in enumerate(procs, start=1):
        cpu_pct = max(0.0, min(cpu_pct, 100.0))              # limita % entre 0 e 100
        dur_seg = (cpu_pct / 100.0) * janela_seg             # segundos de CPU na janela
        dur_quanta = max(1, int(round(dur_seg * FATOR)))     # inteiro >= 1
        chegada = chegada_tick                               # inteiro
        prioridade = 1                                       # heurística simples
        peso = 1024                                          # default do CFS

        #criando processo com os campos necessários pelo simulador
        processos.append(Processo(i, chegada, dur_quanta, prioridade, peso))
        chegada_tick += 1  #espaça chegadas para manter ordem

    return ("Android (ADB)", processos)