#Implementa o algoritmo de escalonamento SJF (Shortest Job First)
import time
import statistics

from models.processo import Processo
from models.resultado import ResultadoSimulacao
from dataclasses import asdict
from typing import List

#SJF (Shortest Job First)
class SJF:
    #Define o nome do algoritmo e se ele será preemptivo ou não
    def __init__(self, preemptivo=False):
        self.nome = f"SJF {'(Preemptivo)' if preemptivo else '(Não-Preemptivo)'}"
        self.preemptivo = preemptivo
    
    def executar(self, processos: List[Processo]) -> ResultadoSimulacao:
        #Inicia a simulação e registra o tempo inicial
        start_time = time.time()
        #Cria cópias dos processos originais
        processos_copia = [Processo(**asdict(p)) for p in processos]
        
        # Escolhe a versão do algoritmo conforme o modo definido
        if not self.preemptivo:
            return self._executar_nao_preemptivo(processos_copia, time.time() - start_time)
        else:
            return self._executar_preemptivo(processos_copia, time.time() - start_time)
    
    #Versão não preemptiva do SJF (executa o processo até o fim)
    def _executar_nao_preemptivo(self, processos, start_exec_time):
        tempo_atual = 0
        fila_prontos = []
        processos_restantes = processos.copy()
        processos_concluidos = []
        
        #looping principal da simulação do SJF em nao preemptivo
        while processos_restantes or fila_prontos:
            #Adiciona processos que chegaram até o tempo atual
            chegaram = [p for p in processos_restantes if p.chegada <= tempo_atual]
            fila_prontos.extend(chegaram)
            for p in chegaram:
                processos_restantes.remove(p)
            
            #Se não há processos prontos, avança o tempo
            if not fila_prontos:
                if processos_restantes:
                    tempo_atual = min(p.chegada for p in processos_restantes)
                continue
            
            # Seleciona processo com menor duração
            processo_atual = min(fila_prontos, key=lambda x: x.duracao)
            fila_prontos.remove(processo_atual)
            
            #Define tempos de início e fim
            processo_atual.tempo_inicio = tempo_atual
            processo_atual.tempo_fim = tempo_atual + processo_atual.duracao
            tempo_atual = processo_atual.tempo_fim
            processos_concluidos.append(processo_atual)
        
        exec_time = time.time() - start_exec_time #Calcula o tempo de execução total
        return self._calcular_metricas(processos_concluidos, tempo_atual, exec_time) #Retorna as métricas calculadas

    # Versão preemptiva do SJF (interrompe processos quando um mais curto chega)  
    def _executar_preemptivo(self, processos, start_exec_time):
        tempo_atual = 0
        fila_prontos = []
        processos_restantes = processos.copy()
        processo_executando = None

        #looping principal da simulação do SJF em preemptivo
        while processos_restantes or fila_prontos or processo_executando:
            #Adiciona processos que chegaram até o tempo atual
            chegaram = [p for p in processos_restantes if p.chegada <= tempo_atual]
            fila_prontos.extend(chegaram)
            for p in chegaram:
                processos_restantes.remove(p)
            
            #Verifica se deve ocorrer preempção
            if processo_executando and fila_prontos:
                menor_tempo = min(p.tempo_restante for p in fila_prontos)
                if menor_tempo < processo_executando.tempo_restante:
                    fila_prontos.append(processo_executando)
                    processo_executando = None
            
            #Seleciona o processo com menor tempo restante
            if not processo_executando and fila_prontos:
                processo_executando = min(fila_prontos, key=lambda x: x.tempo_restante)
                fila_prontos.remove(processo_executando)
                if processo_executando.tempo_inicio == -1:
                    processo_executando.tempo_inicio = tempo_atual
            
            #Executa o processo por 1 unidade de tempo
            if processo_executando:
                processo_executando.tempo_restante -= 1
                tempo_atual += 1
                #Finaliza o processo se ele terminou
                if processo_executando.tempo_restante == 0:
                    processo_executando.tempo_fim = tempo_atual
                    processo_executando = None
            else:
                #Avança o tempo se nenhum processo estiver executando
                tempo_atual += 1
        
        #Calcula o tempo total e retorna os resultados
        exec_time = time.time() - start_exec_time
        return self._calcular_metricas(processos, tempo_atual, exec_time)
    
    #calculando as métricas de desempenho da simulação
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
