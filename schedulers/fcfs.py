#Implementa o algoritmo de escalonamento FCFS (First Come, First Served)
import time
import statistics

from models.processo import Processo
from models.resultado import ResultadoSimulacao
from dataclasses import asdict
from typing import List

#First Come First Served
class FCFS:
    #define o nome do algoritmo
    def __init__(self):
        self.nome = "FCFS"
    
    def executar(self, processos: List[Processo]) -> ResultadoSimulacao:
        #Inicia a simulação e registra o tempo inicial
        start_time = time.time()
        # Cria uma cópia dos processos para não alterar os originais
        processos_copia = [Processo(**asdict(p)) for p in processos]
        #Ordena os processos pela ordem de chegada
        processos_copia.sort(key=lambda x: x.chegada)
        
        # Executa cada processo na ordem em que chegou
        tempo_atual = 0
        for processo in processos_copia:
            # Se o processo ainda não chegou, o tempo avança até sua chegada
            if tempo_atual < processo.chegada:
                tempo_atual = processo.chegada
            
            #Define o tempo de início e fim de cada processo
            processo.tempo_inicio = tempo_atual
            processo.tempo_fim = tempo_atual + processo.duracao

            #Atualiza o tempo atual para o fim do processo
            tempo_atual = processo.tempo_fim
        
        exec_time = time.time() - start_time #Calcula o tempo total de execução
        return self._calcular_metricas(processos_copia, tempo_atual, exec_time) #Retorna os resultados calculados
    
    #Calcula as métricas de desempenho do algoritmo
    def _calcular_metricas(self, processos, tempo_total, exec_time):
        tempos_resposta = [p.tempo_resposta for p in processos]
        tempos_retorno = [p.tempo_retorno for p in processos]
        tempos_espera = [p.tempo_espera for p in processos]
        
        #Retorna um objeto com os resultados consolidados
        return ResultadoSimulacao(
            algoritmo=self.nome,
            processos=processos,
            tempo_total=tempo_total,
            tempo_medio_resposta=statistics.mean(tempos_resposta),
            tempo_medio_retorno=statistics.mean(tempos_retorno),
            tempo_medio_espera=statistics.mean(tempos_espera),
            throughput=len(processos) / tempo_total if tempo_total > 0 else 0,
            tempo_execucao_simulacao=exec_time
        )