#Implementa o algoritmo de escalonamento Round Robin
import time
import statistics

from models.processo import Processo
from models.resultado import ResultadoSimulacao
from dataclasses import asdict
from typing import List

#Round Robin
class RoundRobin:
    #Define o nome do algoritmo e o valor do quantum
    def __init__(self, quantum=2):
        self.nome = f"Round Robin (q={quantum})"
        self.quantum = quantum
    
    def executar(self, processos: List[Processo]) -> ResultadoSimulacao:
        #Inicia a simulação e registra o tempo inicial
        start_time = time.time()
        #Cria cópias dos processos originais
        processos_copia = [Processo(**asdict(p)) for p in processos]
        
        tempo_atual = 0
        fila_prontos = []   #Fila de processos prontos para execução
        processos_restantes = processos_copia.copy()
        
        #looping principal da simulação round robin
        while processos_restantes or fila_prontos:
            # Adiciona processos que chegaram até o tempo real
            chegaram = [p for p in processos_restantes if p.chegada <= tempo_atual]
            fila_prontos.extend(chegaram)
            for p in chegaram:
                processos_restantes.remove(p)

            #Se não há processos prontos, avança o tempo até o próximo
            if not fila_prontos:
                if processos_restantes:
                    tempo_atual = min(p.chegada for p in processos_restantes)
                continue
            
            #Retira o primeiro processo da fila (ordem circular)
            processo_atual = fila_prontos.pop(0)
            
            #Define o tempo de início se for a primeira execução
            if processo_atual.tempo_inicio == -1:
                processo_atual.tempo_inicio = tempo_atual
            
            # Executa por quantum ou até terminar
            tempo_execucao = min(self.quantum, processo_atual.tempo_restante)
            processo_atual.tempo_restante -= tempo_execucao
            tempo_atual += tempo_execucao
            
            # Adiciona novos processos que chegaram durante a execução
            chegaram = [p for p in processos_restantes if p.chegada <= tempo_atual]
            fila_prontos.extend(chegaram)
            for p in chegaram:
                processos_restantes.remove(p)
            
            #Se ainda restar tempo de CPU, recoloca o processo no final da fila
            if processo_atual.tempo_restante > 0:
                fila_prontos.append(processo_atual)
            else:
                # Caso contrário, registra o tempo de término
                processo_atual.tempo_fim = tempo_atual
        
        exec_time = time.time() - start_time #Calcula o tempo total e o tempo de execução real
        return self._calcular_metricas(processos_copia, tempo_atual, exec_time) #Retorna os resultados consolidados
    
    #Calcula as métricas de desempenho da simulação
    def _calcular_metricas(self, processos, tempo_total, exec_time):
        tempos_resposta = [p.tempo_resposta for p in processos]
        tempos_retorno = [p.tempo_retorno for p in processos]
        tempos_espera = [p.tempo_espera for p in processos]
        
        #Retornando um objeto com os resultados calculados
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