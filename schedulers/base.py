#Definindo a classse base para os algoritmosde escalonamento
from abc import ABC, abstractmethod
from typing import List
import statistics
import time
from models.processo import Processo
from models.resultado import ResultadoSimulacao

class SchedulerBase(ABC): 
    #nome do algoritmo de escolamento
    def __init__(self, nome: str):
        self.nome = nome
    
    #metodo abstrato que deve ser implementado por todos os algoritmos
    @abstractmethod
    def executar(self, processos: List[Processo]) -> ResultadoSimulacao:
        pass

    #calculando metricas de desempenho com base nos resultados das simulações dos processos
    def _calcular_metricas(self, processos: List[Processo], tempo_total: int, exec_time: float) -> ResultadoSimulacao:
        tempos_resposta = [p.tempo_resposta for p in processos if p.tempo_resposta != -1]
        tempos_retorno = [p.tempo_retorno for p in processos if p.tempo_retorno != -1]
        tempos_espera = [p.tempo_espera for p in processos if p.tempo_espera != -1]
        
        #retorna um objeto com os resultados da simulação
        return ResultadoSimulacao(
            algoritmo=self.nome,
            processos=processos,
            tempo_total=tempo_total,
            tempo_medio_resposta=statistics.mean(tempos_resposta) if tempos_resposta else 0,
            tempo_medio_retorno=statistics.mean(tempos_retorno) if tempos_retorno else 0,
            tempo_medio_espera=statistics.mean(tempos_espera) if tempos_espera else 0,
            throughput=len(processos) / tempo_total if tempo_total > 0 else 0,
            tempo_execucao_simulacao=exec_time
        )