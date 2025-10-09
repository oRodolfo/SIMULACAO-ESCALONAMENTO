#Definindo a classe que representa um processo na simulação
from dataclasses import dataclass

@dataclass
class Processo:
    pid: int                    # ID do processo
    chegada: int               # Tempo de chegada
    duracao: int               # Tempo de CPU necessário
    prioridade: int = 0        # Prioridade (menor = maior prioridade)
    peso: int = 1024           # Peso para CFS (nice 0 = 1024)
    
    # Campos calculados durante execução
    tempo_inicio: int = -1
    tempo_fim: int = -1
    tempo_restante: int = 0
    vruntime: float = 0.0   #tempo virtual usado pelo algoritmo CFS

    #iniciando o tempo restante com a duração total do processo
    def __post_init__(self):
        self.tempo_restante = self.duracao
    
    #calculando o tempo de chegada e o tempo de inicio da execução do processo
    @property
    def tempo_resposta(self) -> int:
        return self.tempo_inicio - self.chegada if self.tempo_inicio != -1 else -1
    
    #calculando o tempo total desde a chegada até a finalização 
    @property
    def tempo_retorno(self) -> int:
        return self.tempo_fim - self.chegada if self.tempo_fim != -1 else -1
    
    #tempo total que o processo ficou esperando na fila
    @property
    def tempo_espera(self) -> int:
        return self.tempo_retorno - self.duracao if self.tempo_retorno != -1 else -1