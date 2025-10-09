#implementando o algoritmo CSF (Completely Fair Scheduler)
import time
import statistics

from dataclasses import asdict
from typing import List
from models.processo import Processo
from models.resultado import ResultadoSimulacao

#Completely Fair Scheduler
class CFS:
    #Define o nome do algoritmo e a latência alvo usado no calculo de timeslice
    def __init__(self, latencia_alvo=20):
        self.nome = "CFS (Simplified)"
        self.latencia_alvo = latencia_alvo
    
    #iniciando a simulação e registra o tempo inicial
    def executar(self, processos: List[Processo]) -> ResultadoSimulacao:
        start_time = time.time()
        processos_copia = [Processo(**asdict(p)) for p in processos]
        
        tempo_atual = 0
        arvore_rb = [] #lista que simula a árvore rubro-negra usado no CFS
        processos_restantes = processos_copia.copy()
        
        # Inicializa vruntime
        for p in processos_copia:
            p.vruntime = 0.0
        
        #looping principal da simulação
        while processos_restantes or arvore_rb:
            #Adiciona processos que chegaram em tempo real
            chegaram = [p for p in processos_restantes if p.chegada <= tempo_atual]
            for p in chegaram:
                #Ajusta vruntime ao adicionar novos processos
                if arvore_rb:
                    p.vruntime = min(proc.vruntime for proc in arvore_rb)
                arvore_rb.append(p)
                processos_restantes.remove(p)
            
            #Se não há processos prontos, avança o tempo
            if not arvore_rb:
                if processos_restantes:
                    tempo_atual = min(p.chegada for p in processos_restantes)
                continue
            
            #Ordena os processos pelo menor vruntime (mais justo)
            arvore_rb.sort(key=lambda x: x.vruntime)
            processo_atual = arvore_rb[0]
            
            #Registra o início do processo, se ainda não tiver começado
            if processo_atual.tempo_inicio == -1:
                processo_atual.tempo_inicio = tempo_atual
            
            #Calcula o timeslice proporcional ao peso do processo
            peso_total = sum(p.peso for p in arvore_rb)
            timeslice = max(1, int(self.latencia_alvo * processo_atual.peso / peso_total))
            
            #Executa o processo pelo tempo definido
            tempo_execucao = min(timeslice, processo_atual.tempo_restante)
            processo_atual.tempo_restante -= tempo_execucao
            tempo_atual += tempo_execucao
            
            #Atualiza o vruntime com base no peso
            processo_atual.vruntime += tempo_execucao * (1024.0 / processo_atual.peso)
            
            #Remove o processo da fila se ele terminou
            if processo_atual.tempo_restante == 0:
                processo_atual.tempo_fim = tempo_atual
                arvore_rb.remove(processo_atual)
        
        #Calcula o tempo total de execução
        exec_time = time.time() - start_time
        return self._calcular_metricas(processos_copia, tempo_atual, exec_time)
    
    #Calcula as métricas finais da simulação
    def _calcular_metricas(self, processos, tempo_total, exec_time):
        tempos_resposta = [p.tempo_resposta for p in processos]
        tempos_retorno = [p.tempo_retorno for p in processos]
        tempos_espera = [p.tempo_espera for p in processos]
        
        #Retorna um objeto ResultadoSimulacao com os dados consolidados
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