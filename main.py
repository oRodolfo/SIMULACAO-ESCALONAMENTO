#Ponto de entrada do simulador: menu, execução dos cenários e geração de relatórios
import sys
import os
import time
import json
import platform
import uuid
import subprocess

# Imports dos módulos do projeto
from typing import List, Dict, Any
from models.processo import Processo
from models.resultado import ResultadoSimulacao  
from schedulers.fcfs import FCFS
from schedulers.sjf import SJF
from schedulers.round_robin import RoundRobin
from schedulers.cfs import CFS
from utils.gerador_dados import GeradorDados
from utils.analisador import AnalisadorResultados
from relatorio_interativo import RelatorioInterativo
from datetime import datetime
from android_coletor import gerar_cenario_android_via_adb

# Tentar importar psutil para métricas do Sistema Operacional
PSUTIL_DISPONIVEL = False
try:
    import psutil
    PSUTIL_DISPONIVEL = True
except Exception:
    PSUTIL_DISPONIVEL = False

# Verifica se as bibliotecas de visualização estão disponíveis
VISUALIZACAO_DISPONIVEL = False
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    import numpy as np
    VISUALIZACAO_DISPONIVEL = True
    print("✅ Bibliotecas de visualização carregadas com sucesso!")
except ImportError as e:
    print("⚠️  Bibliotecas de visualização não disponíveis.")
    print("   Para habilitar gráficos, instale: pip install matplotlib seaborn pandas numpy")
    # não abortar: apenas desabilitar gráficos

#Armazena snapshots de métricas do Sistema Operacional por cenário/algoritmo coletadas durante as execuções
_METRICS_SIDE_CAR: Dict[str, List[Dict[str, Any]]] = {}

#Mostra o banner inicial e info do sistema
def exibir_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                 🚀 SIMULADOR DE ESCALONAMENTO                    ║
║                     Algoritmos de Sistemas Operacionais          ║
╠══════════════════════════════════════════════════════════════════╣
║  📊 Algoritmos: FCFS • SJF • Round Robin • CFS                  ║
║  🎯 Cenários: Básico • CPU Intensivo • Misto • Simultâneo       ║
║  📈 Análises: Tempo Resposta • Throughput • Relatórios          ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print_system_info()

#Exibe informações do SO, Python e (se possível) CPU/Memória
def print_system_info():
    try:
        py = sys.executable
        print(f"🖥️  Plataforma: {platform.system()} {platform.release()} ({platform.version()})")
        print(f"🐍 Python: {platform.python_version()} - {py}")
        if PSUTIL_DISPONIVEL:
            try:
                cpu_count = psutil.cpu_count(logical=True)
                mem = psutil.virtual_memory()
                print(f"⚙️  CPUs lógicas: {cpu_count} | Memória total: {round(mem.total/1024**2)} MB")
            except Exception:
                pass
        else:
            print("ℹ️  Para métricas mais completas instale: pip install psutil")
    except Exception:
        pass

#Coleta um snapshot rápido do SO/processo atual (se psutil estiver disponível)
def coletar_snapshot_so(label: str = "") -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "timestamp": time.time(),
        "label": label,
        "platform": platform.platform(),
    }

    try:
        if PSUTIL_DISPONIVEL:
            proc = psutil.Process(os.getpid())
            #Leitura leve de CPU/mem e dados do processo
            cpu_total = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            ctx = proc.num_ctx_switches()
            times = proc.cpu_times()

            snapshot.update({
                "cpu_percent": float(cpu_total),
                "cpu_per_core": cpu_per_core,
                "process_cpu_user": float(times.user),
                "process_cpu_system": float(times.system),
                "memory_percent": float(proc.memory_percent()),
                "memory_total_percent": float(mem.percent),
                "swap_percent": float(swap.percent),
                "ctx_switch_voluntary": getattr(ctx, 'voluntary', None),
                "ctx_switch_involuntary": getattr(ctx, 'involuntary', None),
                "num_threads": proc.num_threads(),
                "pid": proc.pid,
            })
        else:
            snapshot.update({
                "note": "psutil não disponível",
                "python_version": platform.python_version(),
            })
    except Exception as e:
        snapshot["error_collecting"] = str(e)

    return snapshot

#Configura todos os algoritmos a serem usados e testados
def configurar_algoritmos():
    return [
        FCFS(),
        SJF(preemptivo=False),
        SJF(preemptivo=True),
        RoundRobin(quantum=2),
        RoundRobin(quantum=4),
        CFS(latencia_alvo=20)
    ]

#Executa simulação básica com todos os cenários
def executar_simulacao_basica():
    print("🔄 Iniciando simulação básica...")
    algoritmos = configurar_algoritmos()
    cenarios = GeradorDados.obter_todos_cenarios()
    resultados_por_cenario = {}

    for nome_cenario, processos in cenarios.items():
        print(f"\n🎯 CENÁRIO: {nome_cenario}")
        print(f"   Processos: {len(processos)}")
        print(f"   Chegadas: {[p.chegada for p in processos]}")
        print(f"   Durações: {[p.duracao for p in processos]}")
        print("-" * 60)

        resultados_cenario = []
        _METRICS_SIDE_CAR[nome_cenario] = []

        for algoritmo in algoritmos:
            try:
                # snapshot antes (opcional)
                snap_before = coletar_snapshot_so(label=f"{nome_cenario}-{algoritmo.nome}-before")
                resultado = algoritmo.executar(processos)
                resultados_cenario.append(resultado)
                # snapshot depois
                snap_after = coletar_snapshot_so(label=f"{nome_cenario}-{algoritmo.nome}-after")

                # armazenar sidecar: liga resultado com snapshots
                _METRICS_SIDE_CAR[nome_cenario].append({
                    "algoritmo": resultado.algoritmo,
                    "snapshot_before": snap_before,
                    "snapshot_after": snap_after,
                })

                print(f"{resultado.algoritmo:<25} | "
                      f"Resp: {resultado.tempo_medio_resposta:>6.2f} | "
                      f"Ret: {resultado.tempo_medio_retorno:>6.2f} | "
                      f"Esp: {resultado.tempo_medio_espera:>6.2f} | "
                      f"Thrpt: {resultado.throughput:>6.4f}")

            except Exception as e:
                print(f"❌ Erro no algoritmo {getattr(algoritmo, 'nome', str(algoritmo))}: {e}")

        resultados_por_cenario[nome_cenario] = resultados_cenario

        #Mostra o melhor algoritmo do cenário (rank rápido)
        if resultados_cenario:
            comparacao = AnalisadorResultados.comparar_resultados(resultados_cenario)
            melhor = comparacao['ranking_geral'][0]
            print(f"\n🏆 Melhor algoritmo para este cenário: {melhor['algoritmo']} ({melhor['score_percentual']:.1f}% qualidade)")

    return resultados_por_cenario

#Executa simulação com análise detalhada
def executar_simulacao_detalhada():
    print("🔍 Iniciando simulação detalhada...")
    resultados_por_cenario = executar_simulacao_basica()

    print("\n" + "="*80)
    print("📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("="*80)

    # Análise por cenário
    for nome_cenario, resultados in resultados_por_cenario.items():
        print(f"\n🎯 ANÁLISE DO CENÁRIO: {nome_cenario}")

        # Características do cenário
        processos = GeradorDados.obter_todos_cenarios()[nome_cenario]
        caracteristicas = AnalisadorResultados.analisar_caracteristicas_cenario(processos)

        print(f"   📋 Características:")
        print(f"      • Tipo Estimado: {caracteristicas['tipo_estimado']}")
        print(f"      • Processos: {caracteristicas['num_processos']}")
        print(f"      • Duração Média: {caracteristicas['duracao_media']:.1f}")
        print(f"      • Variabilidade: {caracteristicas['variabilidade_duracao']:.1f}x")

        # Comparação de resultados
        comparacao = AnalisadorResultados.comparar_resultados(resultados)
        relatorio = AnalisadorResultados.gerar_relatorio_texto(comparacao, nome_cenario)
        print(relatorio)

    return resultados_por_cenario

#Executa simulação completa com todas as funcionalidades
def executar_simulacao_completa():
    print("🚀 Iniciando simulação COMPLETA...")
    resultados_por_cenario = executar_simulacao_detalhada()

    # Gera arquivos de saída
    print("\n📁 Gerando arquivos de saída...")

    # CSV e JSON
    analisador = AnalisadorResultados()
    try:
        print(analisador.gerar_relatorio_csv(resultados_por_cenario))
    except Exception:
        pass
    try:
        print(analisador.gerar_relatorio_json(resultados_por_cenario))
    except Exception:
        pass

    caminho_json = exportar_json_para_relatorio(resultados_por_cenario, 'resultados_simulacao.json')
    gerar_relatorio_interativo_automatico(caminho_json, 'relatorio_interativo.html', abrir=True)

    # Relatório consolidado
    relatorio_consolidado = gerar_relatorio_consolidado(resultados_por_cenario)
    with open('relatorio_consolidado.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio_consolidado)
    print("✅ Relatório consolidado salvo como 'relatorio_consolidado.txt'")

    # Gera relatório HTML simples (sem gráficos)
    relatorio_html = gerar_relatorio_html_simples(resultados_por_cenario)
    with open('relatorio_simples.html', 'w', encoding='utf-8') as f:
        f.write(relatorio_html)
    print("✅ Relatório HTML salvo como 'relatorio_simples.html'")

    # Visualizações (se disponível)
    if VISUALIZACAO_DISPONIVEL:
        print("\n🎨 Gerando visualizações...")
        try:
            gerar_visualizacoes_basicas(resultados_por_cenario)
        except Exception as e:
            print(f"⚠️  Erro ao gerar visualizações: {e}")
    else:
        print("\n📊 Visualizações indisponíveis (matplotlib não instalado)")
        print("   Para habilitar: pip install matplotlib seaborn pandas numpy")

    return resultados_por_cenario

#Converte resultados para o formato do RelatorioInterativo e salva em JSON
def exportar_json_para_relatorio(resultados_por_cenario, caminho_json='resultados_simulacao.json'):
    pacote = {}
    for cenario, resultados in resultados_por_cenario.items():
        linhas = []
        sidecar = _METRICS_SIDE_CAR.get(cenario, [])
        for idx, r in enumerate(resultados):
            metrics = None
            #Tenta associar snapshots ao resultado pelo índice/nome
            if idx < len(sidecar) and sidecar[idx].get('algoritmo') == r.algoritmo:
                metrics = sidecar[idx]
            else:
                for s in sidecar:
                    if s.get('algoritmo') == r.algoritmo:
                        metrics = s
                        break
            linhas.append({
                "algoritmo": r.algoritmo,
                "tempo_medio_resposta": float(r.tempo_medio_resposta),
                "tempo_medio_retorno":  float(r.tempo_medio_retorno),
                "tempo_medio_espera":   float(r.tempo_medio_espera),
                "throughput":           float(r.throughput),
                "tempo_total": getattr(r, 'tempo_total', None),
                "sistema_metrics": metrics,
            })
        pacote[cenario] = linhas

    #Metadados da execução
    pacote["__meta__"] = {
        "run_id": str(uuid.uuid4())[:8],                   # ID curto da execução
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cwd": os.getcwd(),                                 # pasta de onde rodou
        "python": platform.python_version(),
        "platform": f"{platform.system()} {platform.release()}",
        "file_mtime": time.ctime(os.path.getmtime(caminho_json)) if os.path.exists(caminho_json) else None
    }
    
    #Destaques agregados (mais versátil, responsivo e throughput)
    destaques = calcular_destaques_pelo_json(pacote)
    pacote["__destaques__"] = destaques

    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(pacote, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON para relatório salvo em: {caminho_json}")
    return caminho_json

#Calcula destaques globais a partir do pacote JSON
def calcular_destaques_pelo_json(pacote_json):
    # 1) Mais Responsivo (menor tempo de resposta global)
    best_resp = None  # (algoritmo, valor, cenario)
    # 2) Melhor Throughput (maior global)
    best_thr = None   # (algoritmo, valor, cenario)
    # 3) Mais Versátil (contagem de “vitórias” por cenário)
    vitorias = {}     # algoritmo -> contagem

    for cenario, linhas in pacote_json.items():
        if not linhas or cenario.startswith("__"):
            continue

        # vencedor do cenário por menor tempo de resposta (ajustavel conforme necessario com outro critério)
        vencedor = min(linhas, key=lambda x: x["tempo_medio_resposta"])
        vitorias[vencedor["algoritmo"]] = vitorias.get(vencedor["algoritmo"], 0) + 1

        for r in linhas:
            if best_resp is None or r["tempo_medio_resposta"] < best_resp[1]:
                best_resp = (r["algoritmo"], r["tempo_medio_resposta"], cenario)
            if best_thr is None or r["throughput"] > best_thr[1]:
                best_thr = (r["algoritmo"], r["throughput"], cenario)

    mais_versatil = max(vitorias.items(), key=lambda kv: kv[1])[0] if vitorias else "N/A"

    return {
        "mais_versatil": mais_versatil,
        "mais_responsivo": (
            {"algoritmo": best_resp[0], "valor": best_resp[1], "cenario": best_resp[2]}
            if best_resp else None
        ),
        "melhor_throughput": (
            {"algoritmo": best_thr[0], "valor": best_thr[1], "cenario": best_thr[2]}
            if best_thr else None
        ),
    }

#Gera o HTML interativo a partir do JSON e (opcionalmente) abre no navegador
def gerar_relatorio_interativo_automatico(caminho_json='resultados_simulacao.json', caminho_html='relatorio_interativo.html', abrir=True):
    rel = RelatorioInterativo(caminho_json)
    rel.gerar_html_interativo(saida_html=caminho_html, abrir_navegador=abrir)

#Cria um gráfico simples comparando tempos de resposta por cenário
def gerar_visualizacoes_basicas(resultados_por_cenario):
    if not VISUALIZACAO_DISPONIVEL:
        return
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots(figsize=(12, 6))
        cores = ['#FF6B6B', "#45CF7F", "#00D9FF", "#0231FF", '#FFEAA7', '#DDA0DD']
        for i, (cenario, resultados) in enumerate(resultados_por_cenario.items()):
            tempos_resposta = [r.tempo_medio_resposta for r in resultados]
            algoritmos = [r.algoritmo for r in resultados]
            x_pos = np.arange(len(algoritmos)) + i * 0.15
            ax.bar(x_pos, tempos_resposta, width=0.15, 
                  label=cenario, color=cores[i % len(cores)], alpha=0.8)
        ax.set_xlabel('Algoritmos')
        ax.set_ylabel('Tempo Médio de Resposta')
        ax.set_title('Comparação de Algoritmos por Cenário')
        ax.set_xticks(np.arange(len(algoritmos)) + 0.3)
        ax.set_xticklabels(algoritmos, rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('comparacao_basica.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("✅ Gráfico básico salvo como 'comparacao_basica.png'")
    except Exception as e:
        print(f"❌ Erro ao gerar visualizações: {e}")

#Gera relatório HTML simples sem dependências externas (javascript ou css)
def gerar_relatorio_html_simples(resultados_por_cenario):
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Relatório de Simulação - Algoritmos de Escalonamento</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1, h2 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #4CAF50; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .destaque { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .algoritmo { font-weight: bold; color: #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Simulação de Escalonamento</h1>
        <p><strong>Data:</strong> """ + time.strftime('%d/%m/%Y %H:%M:%S') + """</p>
        <p><strong>Cenários Testados:</strong> """ + str(len(resultados_por_cenario)) + """</p>
    """

    for cenario, resultados in resultados_por_cenario.items():
        if not resultados:
            continue
        html += f"""
        <h2>🎯 Cenário: {cenario}</h2>
        <table>
            <tr>
                <th>Algoritmo</th>
                <th>Tempo Resposta</th>
                <th>Tempo Retorno</th>
                <th>Tempo Espera</th>
                <th>Throughput</th>
                <th>Tempo Total</th>
                <th>Métrica SO (ex: CPU%)</th>
            </tr>
        """
        sidecar = _METRICS_SIDE_CAR.get(cenario, [])
        for idx, resultado in enumerate(resultados):
            cpu_after = None
            if idx < len(sidecar) and sidecar[idx].get('snapshot_after'):
                cpu_after = sidecar[idx]['snapshot_after'].get('cpu_percent')
            else:
                # busca por algoritmo
                for s in sidecar:
                    if s.get('algoritmo') == resultado.algoritmo and s.get('snapshot_after'):
                        cpu_after = s['snapshot_after'].get('cpu_percent')
                        break

            html += f"""
            <tr>
                <td class="algoritmo">{resultado.algoritmo}</td>
                <td>{resultado.tempo_medio_resposta:.2f}</td>
                <td>{resultado.tempo_medio_retorno:.2f}</td>
                <td>{resultado.tempo_medio_espera:.2f}</td>
                <td>{resultado.throughput:.4f}</td>
                <td>{getattr(resultado, 'tempo_total', '')}</td>
                <td>{cpu_after if cpu_after is not None else 'N/A'}</td>
            </tr>
            """
        html += "</table>"
        comparacao = AnalisadorResultados.comparar_resultados(resultados)
        melhor = comparacao['ranking_geral'][0]
        html += f"""
        <div class="destaque">
            <strong>🏆 Melhor Algoritmo:</strong> {melhor['algoritmo']} 
            (Score: {melhor['score_percentual']:.1f}%)
        </div>
        """

    html += """
        <h2>💡 Recomendações Gerais</h2>
        <ul>
            <li><strong>Sistemas Interativos:</strong> Round Robin ou CFS</li>
            <li><strong>Sistemas Batch:</strong> SJF ou FCFS</li>
            <li><strong>Sistemas Mistos:</strong> CFS (usado no Linux)</li>
            <li><strong>Sistemas Simples:</strong> FCFS (menor overhead)</li>
        </ul>
    </div>
</body>
</html>
    """
    return html

#Gera relatório consolidado em texto
def gerar_relatorio_consolidado(resultados_por_cenario: Dict[str, List[ResultadoSimulacao]]) -> str:
    relatorio = []
    relatorio.append("="*100)
    relatorio.append("📊 RELATÓRIO CONSOLIDADO - SIMULADOR DE ESCALONAMENTO")
    relatorio.append("="*100)
    relatorio.append(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    relatorio.append(f"Total de Cenários: {len(resultados_por_cenario)}")
    relatorio.append(f"Total de Simulações: {sum(len(r) for r in resultados_por_cenario.values())}")
    relatorio.append("")
    relatorio.append("🏆 RESUMO DOS MELHORES ALGORITMOS POR CENÁRIO:")
    relatorio.append("-" * 80)
    ranking_geral = {}

    for nome_cenario, resultados in resultados_por_cenario.items():
        if resultados:
            comparacao = AnalisadorResultados.comparar_resultados(resultados)
            melhor = comparacao['ranking_geral'][0]
            relatorio.append(f"🎯 {nome_cenario:<30}: {melhor['algoritmo']} ({melhor['score_percentual']:.1f}%)")
            alg = melhor['algoritmo']
            ranking_geral[alg] = ranking_geral.get(alg, 0) + 1

    relatorio.append(f"\n🥇 ALGORITMOS MAIS VERSÁTEIS:")
    relatorio.append("-" * 50)
    ranking_ordenado = sorted(ranking_geral.items(), key=lambda x: x[1], reverse=True)
    for i, (algoritmo, vitorias) in enumerate(ranking_ordenado, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
        relatorio.append(f"{emoji} {algoritmo:<30} ({vitorias} cenários)")

    relatorio.append(f"\n💡 RECOMENDAÇÕES PRÁTICAS:")
    relatorio.append("-" * 50)
    relatorio.append("🖥️  Desktop/Interativo: Round Robin (q=2-4) ou CFS")
    relatorio.append("⚡ Servidor/Batch: SJF (Não-Preemptivo) ou FCFS")  
    relatorio.append("🔄 Tempo Real: Round Robin com quantum baixo")
    relatorio.append("🌐 Multipropósito: CFS (Linux) ou Round Robin adaptativo")
    relatorio.append(f"\n📊 INSIGHTS TÉCNICOS:")
    relatorio.append("-" * 50)
    relatorio.append("• FCFS: Simples, mas pode gerar 'convoy effect'")
    relatorio.append("• SJF: Minimiza tempo médio, risco de starvation")
    relatorio.append("• Round Robin: Justo, quantum impacta performance")
    relatorio.append("• CFS: Balanceia equidade e eficiência")
    relatorio.append(f"\n🎓 PARA APRESENTAÇÃO (5 MIN):")
    relatorio.append("-" * 50)
    relatorio.append("1. Explique brevemente cada algoritmo (1 min)")
    relatorio.append("2. Mostre resultados principais (2 min)")
    relatorio.append("3. Compare com SOs reais (1 min)")
    relatorio.append("4. Conclusões e recomendações (1 min)")
    return "\n".join(relatorio)

#Cria um cenário customizado via input e executa todos os algoritmos
def executar_cenario_personalizado():
    print("\n🛠️  CRIADOR DE CENÁRIO PERSONALIZADO")
    print("="*50)
    try:
        num_processos = int(input("Quantos processos? (1-10): "))
        if not 1 <= num_processos <= 10:
            raise ValueError("Número inválido")
        processos = []
        for i in range(num_processos):
            print(f"\n📋 Processo {i+1}:")
            chegada = int(input("  Tempo de chegada (0-20): "))
            duracao = int(input("  Duração (1-30): "))
            prioridade = int(input("  Prioridade (0-3): ") or "1")
            peso = int(input("  Peso CFS (512,1024,2048): ") or "1024")
            processo = Processo(i+1, chegada, duracao, prioridade, peso)
            processos.append(processo)
        algoritmos = configurar_algoritmos()
        resultados = []
        print(f"\n🚀 Executando cenário personalizado...")
        print("-" * 50)
        for algoritmo in algoritmos:
            resultado = algoritmo.executar(processos)
            resultados.append(resultado)
            print(f"{resultado.algoritmo:<25} | Resposta: {resultado.tempo_medio_resposta:>6.2f}")
        comparacao = AnalisadorResultados.comparar_resultados(resultados)
        relatorio = AnalisadorResultados.gerar_relatorio_texto(comparacao, "Personalizado")
        print(relatorio)
        return {"Personalizado": resultados}
    except (ValueError, KeyboardInterrupt) as e:
        print(f"❌ Entrada inválida: {e}")
        return None

# ====== CENÁRIO GERADO DO SISTEMA LOCAL ======
#Observa os processos reais por 'segundos', com passo 'dt', e cria um cenário (chegada, duração) aproximado para a simulação. Requer psutil.
def gerar_cenario_a_partir_do_sistema(segundos: float = 10.0, dt: float = 0.1, top_k: int = 8):
    if not PSUTIL_DISPONIVEL:
        print("❌ psutil não instalado. Rode: py -m pip install psutil")
        return None, None

    print(f"🔎 Amostrando processos reais por {segundos}s (dt={dt}s)...")
    proc_info = {}  # pid -> {first_ts, last_ts, cpu_total, name, mem, nice/prio}
    start_ts = time.time()
    ticks = 0

    #Prime a leitura de CPU para estabilizar
    psutil.cpu_percent(interval=None)
    while time.time() - start_ts < segundos:
        now = time.time()
        for p in psutil.process_iter(attrs=["pid", "name", "cpu_times", "status", "memory_info", "nice"]):
            try:
                pid = p.info["pid"]
                name = (p.info.get("name") or "proc").strip()[:20]
                cput = p.info["cpu_times"]
                cpu_total = (cput.user or 0.0) + (cput.system or 0.0)
                mem = (p.info.get("memory_info").rss if p.info.get("memory_info") else 0)
                nice = None
                try:
                    nice = int(p.info.get("nice")) if p.info.get("nice") is not None else None
                except Exception:
                    pass

                if pid not in proc_info:
                    proc_info[pid] = {
                        "name": name,
                        "first_ts": now,
                        "last_ts": now,
                        "cpu_total_prev": cpu_total,
                        "cpu_used": 0.0,   # soma de CPU usada
                        "mem": mem,
                        "nice": nice,
                    }
                else:
                    d = proc_info[pid]
                    delta = max(0.0, cpu_total - d["cpu_total_prev"])
                    d["cpu_total_prev"] = cpu_total
                    d["cpu_used"] += delta
                    d["last_ts"] = now
                    d["mem"] = max(d["mem"], mem)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        ticks += 1
        time.sleep(dt)

    #Selecionando TOP-K por CPU e converte em processos da simulação
    items = sorted(proc_info.items(), key=lambda kv: kv[1]["cpu_used"], reverse=True)[:top_k]

   # Normalização: 1 unidade de duração ~= 0.5s de CPU
    unidade = 0.5
    processos = []
    linhas_json = []

    # mapeia nice/mem para prioridade/peso 
    def map_prioridade(nice_val, mem_rss):
        # quanto menor o nice (ou maior memória), mais “prioridade” simbólica
        if nice_val is not None and nice_val < 0:
            pr = 3
        elif mem_rss > 500 * 1024 * 1024:  
            pr = 2
        else:
            pr = 1
        return pr

    for i, (pid, d) in enumerate(items, 1):
        # chegada em unidades: diferença entre first_ts e início, dividido por dt (discretização leve)
        duracao_u = max(1, int(round(d["cpu_used"] / unidade)))
        chegada_u = max(0, int(round((d["first_ts"] - start_ts) / dt)))
        prioridade = map_prioridade(d.get("nice"), d.get("mem", 0))
        peso = 1024 
        # Constrói Processo (id = i)
        p = Processo(i, chegada_u, duracao_u, prioridade, peso)
        processos.append(p)

        #Linha opcional para insumos de tabela
        linhas_json.append({
            "algoritmo": f"{d['name']} (pid {pid})",
            "tempo_medio_resposta": float(duracao_u),   # placeholder p/ tabela; a simulação real calculará
            "tempo_medio_retorno":  float(duracao_u),
            "tempo_medio_espera":   0.0,
            "throughput":           0.0,
        })
    # gera um nome de cenário
    nome_cenario = f"Sistema Local ({platform.system()} {platform.release()})"

    #salva snapshot bruto (opcional, para auditoria)
    try:
        with open("snapshot_sistema.json", "w", encoding="utf-8") as f:
            json.dump({
                "captura_segundos": segundos,
                "dt": dt,
                "top_k": top_k,
                "inicio": start_ts,
                "processos_observados": len(proc_info),
                "selecionados": [
                    {"pid": pid, **d, "cpu_used_s": d["cpu_used"]} for pid, d in items
                ],
            }, f, ensure_ascii=False, indent=2)
        print("✅ Snapshot bruto salvo em 'snapshot_sistema.json'")
    except Exception:
        pass

    print(f"🧩 Cenário gerado: {nome_cenario} | {len(processos)} processos")
    return nome_cenario, processos

#Menu principal interativo no terminal
def menu_interativo():
    while True:
        print("\n" + "="*60)
        print("🎮 MENU DO SIMULADOR DE ESCALONAMENTO")
        print("="*60)
        print("1. 🚀 Simulação Básica")
        print("2. 🔍 Simulação Detalhada")  
        print("3. 🎯 Simulação Completa")
        print("4. 🧠 Cenario do meu computador")
        print("5. 🛠️ Cenário Personalizado")
        print("6. 📱 Cenario do meu Android (via ADB)")
        print("7. 🚪 Sair")
        print("="*60)
        try:
            opcao = input("Escolha uma opção (1-7): ").strip()
            if opcao == "1":
                executar_simulacao_basica()
                input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "2":
                executar_simulacao_detalhada()
                input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "3":
                executar_simulacao_completa()
                input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "4":
                    nome, processos = gerar_cenario_a_partir_do_sistema()
                    if processos:
                        resultados = []
                        for algoritmo in configurar_algoritmos():
                            r = algoritmo.executar(processos)
                            resultados.append(r)
                            print(f"{r.algoritmo:<25} | "
                                f"Resp: {r.tempo_medio_resposta:>6.2f} | "
                                f"Ret: {r.tempo_medio_retorno:>6.2f} | "
                                f"Esp: {r.tempo_medio_espera:>6.2f} | "
                                f"Thrpt: {r.throughput:>6.4f}")
                        resultados_por_cenario = {nome: resultados}
                        _METRICS_SIDE_CAR[nome] = []
                        caminho_json = exportar_json_para_relatorio(resultados_por_cenario, 'resultados_simulacao.json')
                        gerar_relatorio_interativo_automatico(caminho_json, 'relatorio_interativo.html', abrir=True)
                        gerar_visualizacoes_basicas(resultados_por_cenario)
                        input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "5":
                executar_cenario_personalizado()
                input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "6":
                try:
                    nome, processos = gerar_cenario_android_via_adb(janela_seg=5.0, top_n=12)
                    if processos:
                        print(f"\n🚀 Executando simulação com o cenário: {nome}")
                        resultados = []
                        for algoritmo in configurar_algoritmos():
                            r = algoritmo.executar(processos)
                            resultados.append(r)
                            print(f"{r.algoritmo:<25} | "
                                f"Resp: {r.tempo_medio_resposta:>6.2f} | "
                                f"Ret: {r.tempo_medio_retorno:>6.2f} | "
                                f"Esp: {r.tempo_medio_espera:>6.2f} | "
                                f"Thrpt: {r.throughput:>6.4f}")
                        resultados_por_cenario = {nome: resultados}
                        caminho_json = exportar_json_para_relatorio(resultados_por_cenario, 'resultados_simulacao.json')
                        gerar_relatorio_interativo_automatico(caminho_json, 'relatorio_interativo.html', abrir=True)
                    else:
                        print("⚠️ Não foi possível coletar processos via ADB.")
                except FileNotFoundError:
                    print("❌ 'adb' não encontrado. Instale o Android platform-tools e adicione ao PATH.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Falha ao executar adb: {e}")
                except Exception as e:
                    print(f"❌ Erro: {e}")
                input("\n⏸️  Pressione Enter para continuar...")
            elif opcao == "7":
                print("👋 Obrigado por usar o Simulador!")
                break
            else:
                print("❌ Opção inválida.")
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

#Função principal do programa, onde começa a interação com o usuario
def main():
    exibir_banner()
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        if modo == "basico":
            executar_simulacao_basica()
        elif modo == "detalhado":
            executar_simulacao_detalhada()
        elif modo == "completo":
            executar_simulacao_completa()
        else:
            print(f"❌ Modo '{modo}' não reconhecido.")
            print("Modos: basico, detalhado, completo")
    else:
        menu_interativo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)