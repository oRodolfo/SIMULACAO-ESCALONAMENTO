# utils/analisador.py
from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import json
import csv
import math
from statistics import mean, pstdev
from models.processo import Processo
from models.resultado import ResultadoSimulacao


class AnalisadorResultados:
    """
    Utilitários para calcular métricas, comparar algoritmos e gerar relatórios.
    """

    # ===================== CÁLCULO DE MÉTRICAS =====================

    @staticmethod
    def calcular_metricas(
        processos: List[Processo],
        algoritmo: str,
        timeline: Optional[List[Dict[str, int]]] = None,
    ) -> ResultadoSimulacao:
        """
        Retorna um ResultadoSimulacao com as métricas agregadas.

        - Se 'timeline' for fornecida, usa o primeiro início e o último fim de cada PID.
        - Caso contrário, usa atributos do Processo:
          resposta = tempo_inicio - chegada
          fim      = processo.tempo_fim (se existir) ou tempo_inicio + duracao
        """
        if not processos:
            raise ValueError("Lista de processos vazia.")

        por_pid = {p.pid: p for p in processos}

        # Deriva (inicio, fim) por PID
        if timeline:
            primeiros, ultimos = AnalisadorResultados._primeiro_e_ultimo_por_pid(timeline)
        else:
            primeiros, ultimos = {}, {}
            for p in processos:
                t_inicio = getattr(p, "tempo_inicio", None)
                if t_inicio is None:
                    raise AttributeError(
                        f"Processo P{p.pid} sem atributo 'tempo_inicio' e sem timeline."
                    )
                t_fim = getattr(p, "tempo_fim", t_inicio + p.duracao)
                primeiros[p.pid] = t_inicio
                ultimos[p.pid] = t_fim

        # Métricas por processo
        tempos_resposta, tempos_retorno, tempos_espera = [], [], []
        for pid, p in por_pid.items():
            inicio = primeiros[pid]
            fim = ultimos[pid]
            resposta = inicio - p.chegada
            retorno = fim - p.chegada
            espera = retorno - p.duracao
            tempos_resposta.append(resposta)
            tempos_retorno.append(retorno)
            tempos_espera.append(espera)

        tempo_total = max(ultimos.values())
        n = len(processos)
        tempo_medio_resposta = sum(tempos_resposta) / n
        tempo_medio_retorno  = sum(tempos_retorno)  / n
        tempo_medio_espera   = sum(tempos_espera)   / n
        throughput = n / tempo_total if tempo_total > 0 else 0.0

        return ResultadoSimulacao(
            algoritmo=algoritmo,
            processos=processos,
            tempo_total=tempo_total,
            tempo_medio_resposta=tempo_medio_resposta,
            tempo_medio_retorno=tempo_medio_retorno,
            tempo_medio_espera=tempo_medio_espera,
            throughput=throughput,
            timeline=timeline or [],
        )

    # ===================== COMPARAÇÃO / RANKING =====================

    @staticmethod
    def comparar_resultados(
        resultados: List[ResultadoSimulacao],
        pesos: Optional[Dict[str, float]] = None,
    ) -> Dict[str, any]:
        """
        Compara uma lista de ResultadoSimulacao e retorna um dicionário com:
          - ranking_geral: lista [{algoritmo, score, score_percentual, componentes:{...}}] (ordenada)
          - normalizadores: min/max usados
        A pontuação é baseada em qualidade normalizada [0..1]:
          • menor melhor: resposta/retorno/espera -> quality = 1 - (x - min)/(max - min)
          • maior melhor: throughput              -> quality = (x - min)/(max - min)
        Score = média ponderada das qualidades.
        """
        if not resultados:
            raise ValueError("Nenhum resultado fornecido para comparação.")

        # Pesos padrão (ajuste como preferir)
        pesos = pesos or {
            "tempo_medio_resposta": 0.35,
            "tempo_medio_retorno":  0.25,
            "tempo_medio_espera":   0.20,
            "throughput":           0.20,
        }
        # Evita erros se os pesos não somarem 1
        soma_pesos = sum(pesos.values()) or 1.0
        pesos = {k: v / soma_pesos for k, v in pesos.items()}

        # Coleta valores para normalização
        vals = {
            "tempo_medio_resposta": [r.tempo_medio_resposta for r in resultados],
            "tempo_medio_retorno":  [r.tempo_medio_retorno  for r in resultados],
            "tempo_medio_espera":   [r.tempo_medio_espera   for r in resultados],
            "throughput":           [r.throughput           for r in resultados],
        }
        mins = {k: min(v) for k, v in vals.items()}
        maxs = {k: max(v) for k, v in vals.items()}

        def norm_menor_melhor(x, k):
            if math.isclose(maxs[k], mins[k]):  # todos iguais
                return 1.0
            return 1.0 - ((x - mins[k]) / (maxs[k] - mins[k]))

        def norm_maior_melhor(x, k):
            if math.isclose(maxs[k], mins[k]):
                return 1.0
            return (x - mins[k]) / (maxs[k] - mins[k])

        ranking = []
        for r in resultados:
            q_resp = norm_menor_melhor(r.tempo_medio_resposta, "tempo_medio_resposta")
            q_ret  = norm_menor_melhor(r.tempo_medio_retorno,  "tempo_medio_retorno")
            q_esp  = norm_menor_melhor(r.tempo_medio_espera,   "tempo_medio_espera")
            q_thr  = norm_maior_melhor(r.throughput,           "throughput")

            score = (
                q_resp * pesos["tempo_medio_resposta"]
              + q_ret  * pesos["tempo_medio_retorno"]
              + q_esp  * pesos["tempo_medio_espera"]
              + q_thr  * pesos["throughput"]
            )
            ranking.append({
                "algoritmo": r.algoritmo,
                "score": score,
                "score_percentual": score * 100.0,
                "componentes": {
                    "qualidade_resposta": q_resp,
                    "qualidade_retorno":  q_ret,
                    "qualidade_espera":   q_esp,
                    "qualidade_thrpt":    q_thr,
                },
                "metricas": {
                    "tempo_medio_resposta": r.tempo_medio_resposta,
                    "tempo_medio_retorno":  r.tempo_medio_retorno,
                    "tempo_medio_espera":   r.tempo_medio_espera,
                    "throughput":           r.throughput,
                    "tempo_total":          r.tempo_total,
                },
            })

        ranking.sort(key=lambda x: x["score"], reverse=True)
        return {
            "ranking_geral": ranking,
            "normalizadores": {"mins": mins, "maxs": maxs, "pesos": pesos},
        }

    # ===================== ANÁLISE DE CENÁRIO =====================

    @staticmethod
    def analisar_caracteristicas_cenario(processos: List[Processo]) -> Dict[str, any]:
        """Heurísticas simples para descrever o cenário."""
        if not processos:
            return {
                "num_processos": 0, "duracao_media": 0.0, "variabilidade_duracao": 0.0,
                "tipo_estimado": "Vazio"
            }

        duracoes = [p.duracao for p in processos]
        chegadas = [p.chegada for p in processos]
        num = len(processos)
        media = mean(duracoes)
        desv = pstdev(duracoes) if num > 1 else 0.0
        variab = (desv / media) if media > 0 else 0.0

        # tipo estimado (bem simples e ilustrativo)
        if all(c == chegadas[0] for c in chegadas):
            tipo = "Simultâneo"
        elif variab > 0.8:
            tipo = "Misto (Alta variabilidade)"
        elif media >= 12:
            tipo = "CPU-Intensivo"
        else:
            tipo = "Básico"

        return {
            "num_processos": num,
            "duracao_media": float(media),
            "variabilidade_duracao": float(variab if variab != float('inf') else 0.0),
            "tipo_estimado": tipo,
        }

    # ===================== RELATÓRIOS TEXTUAIS =====================

    @staticmethod
    def gerar_relatorio_texto(comparacao: Dict[str, any], nome_cenario: str) -> str:
        """Gera um texto descritivo a partir do resultado de comparar_resultados."""
        ranking = comparacao["ranking_geral"]
        linhas = []
        linhas.append("-" * 80)
        linhas.append(f"🏁 RANKING – CENÁRIO: {nome_cenario}")
        linhas.append("-" * 80)
        for i, item in enumerate(ranking, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            linhas.append(
                f"{emoji} {item['algoritmo']:<25} | "
                f"Score: {item['score_percentual']:>5.1f}%  | "
                f"Resp:{item['metricas']['tempo_medio_resposta']:>6.2f}  "
                f"Ret:{item['metricas']['tempo_medio_retorno']:>6.2f}  "
                f"Esp:{item['metricas']['tempo_medio_espera']:>6.2f}  "
                f"Thrpt:{item['metricas']['throughput']:>6.4f}"
            )
        return "\n".join(linhas)

    # ===================== SAÍDAS CSV / JSON =====================

    def gerar_relatorio_csv(self, resultados_por_cenario: Dict[str, List[ResultadoSimulacao]]) -> str:
        caminho = "resultados_simulacao.csv"
        campos = [
            "cenario", "algoritmo", "tempo_total",
            "tempo_medio_resposta", "tempo_medio_retorno",
            "tempo_medio_espera", "throughput"
        ]
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            for cenario, resultados in resultados_por_cenario.items():
                for r in resultados:
                    w.writerow({
                        "cenario": cenario,
                        "algoritmo": r.algoritmo,
                        "tempo_total": r.tempo_total,
                        "tempo_medio_resposta": f"{r.tempo_medio_resposta:.4f}",
                        "tempo_medio_retorno":  f"{r.tempo_medio_retorno:.4f}",
                        "tempo_medio_espera":   f"{r.tempo_medio_espera:.4f}",
                        "throughput":           f"{r.throughput:.6f}",
                    })
        return f"✅ CSV salvo: {caminho}"

    def gerar_relatorio_json(self, resultados_por_cenario: Dict[str, List[ResultadoSimulacao]]) -> str:
        caminho = "resultados_simulacao.json"
        saida = {}
        for cenario, resultados in resultados_por_cenario.items():
            saida[cenario] = [{
                "algoritmo": r.algoritmo,
                "tempo_total": r.tempo_total,
                "tempo_medio_resposta": r.tempo_medio_resposta,
                "tempo_medio_retorno":  r.tempo_medio_retorno,
                "tempo_medio_espera":   r.tempo_medio_espera,
                "throughput":           r.throughput,
            } for r in resultados]
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(saida, f, ensure_ascii=False, indent=2)
        return f"✅ JSON salvo: {caminho}"

    # ===================== UTILIDADES =====================

    @staticmethod
    def _primeiro_e_ultimo_por_pid(
        timeline: List[Dict[str, int]]
    ) -> Tuple[Dict[int, int], Dict[int, int]]:
        """Devolve primeiro início e último fim por PID a partir da timeline."""
        primeiros: Dict[int, int] = {}
        ultimos: Dict[int, int] = {}
        for seg in timeline:
            pid = int(seg["pid"])
            ini = int(seg["inicio"])
            fim = int(seg["fim"])
            if fim <= ini:
                raise ValueError(f"Segmento inválido para P{pid}: fim ({fim}) <= início ({ini}).")
            if pid not in primeiros or ini < primeiros[pid]:
                primeiros[pid] = ini
            if pid not in ultimos or fim > ultimos[pid]:
                ultimos[pid] = fim
        return primeiros, ultimos

    @staticmethod
    def validar_timeline(timeline: List[Dict[str, int]]) -> None:
        """Valida segmentos básicos da timeline por PID (negativos/sobreposições)."""
        por_pid: Dict[int, List[Tuple[int, int]]] = {}
        for seg in timeline:
            pid = int(seg["pid"]); ini = int(seg["inicio"]); fim = int(seg["fim"])
            if ini < 0 or fim < 0:
                raise ValueError(f"Segmento com tempo negativo em P{pid}: ({ini}, {fim})")
            por_pid.setdefault(pid, []).append((ini, fim))
        for pid, segs in por_pid.items():
            segs.sort()
            for (a1, a2), (b1, b2) in zip(segs, segs[1:]):
                if b1 < a2:
                    raise ValueError(f"Sobreposição de segmentos para P{pid}: ({a1},{a2}) vs ({b1},{b2})")
