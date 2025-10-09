#Define a classe que armazena os resultados da simulação
from dataclasses import dataclass
from typing import List
from .processo import Processo

@dataclass
class ResultadoSimulacao:
    algoritmo: str                      #nome do algoritmo utilizado
    processos: List[Processo]           #lista referente ao processo de simulação
    tempo_total: int                    #tempo total de execução da simulação
    tempo_medio_resposta: float         #tempo medio total de execução de resposta da simulação 
    tempo_medio_retorno: float          #tempo medio total de execução de retorno da simulação
    tempo_medio_espera: float           #tempo medio total de espera de retorno da simulação
    throughput: float                   #quantidade de processos concluidos por unidade de tempo
    tempo_execucao_simulacao: float     #tempo real total gasto para executar a simulação

    #retorna uma formatação dos resultados de forma estruturada
    def __str__(self):
        return (
            f"{self.algoritmo}:\n"
            f"  Tempo Total: {self.tempo_total}\n"
            f"  Tempo Médio Resposta: {self.tempo_medio_resposta:.2f}\n"
            f"  Tempo Médio Retorno: {self.tempo_medio_retorno:.2f}\n"
            f"  Tempo Médio Espera: {self.tempo_medio_espera:.2f}\n"
            f"  Throughput: {self.throughput:.4f}\n"
            f"  Tempo Exec. Simulação: {self.tempo_execucao_simulacao:.6f}s"
        )