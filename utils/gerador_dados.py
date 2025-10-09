from typing import List
from models.processo import Processo
import random

class GeradorDados:
    
    @staticmethod
    def gerar_cenario_basico() -> List[Processo]:
        return [
            Processo(pid=1, chegada=0, duracao=10, prioridade=3, peso=1024),
            Processo(pid=2, chegada=2, duracao=4, prioridade=1, peso=1024),
            Processo(pid=3, chegada=4, duracao=6, prioridade=2, peso=1024),
            Processo(pid=4, chegada=6, duracao=8, prioridade=1, peso=1024),
        ]
    
    @staticmethod
    def gerar_cenario_intensivo_cpu() -> List[Processo]:
        return [
            Processo(pid=1, chegada=0, duracao=20, prioridade=2, peso=1024),   # Compilador
            Processo(pid=2, chegada=1, duracao=15, prioridade=1, peso=512),    # Renderizador (alta prioridade)
            Processo(pid=3, chegada=2, duracao=25, prioridade=3, peso=2048),   # Backup (baixa prioridade, alto peso)
            Processo(pid=4, chegada=3, duracao=12, prioridade=1, peso=1024),   # Análise de dados
            Processo(pid=5, chegada=5, duracao=18, prioridade=2, peso=1536),   # Processamento de vídeo
        ]
    
    @staticmethod
    def gerar_cenario_misto() -> List[Processo]:
        return [
            Processo(pid=1, chegada=0, duracao=2, prioridade=1, peso=1024),    # Clique do mouse
            Processo(pid=2, chegada=1, duracao=20, prioridade=3, peso=1024),   # Processo batch
            Processo(pid=3, chegada=2, duracao=1, prioridade=0, peso=1024),    # Interrupção de teclado
            Processo(pid=4, chegada=3, duracao=15, prioridade=2, peso=1024),   # Download de arquivo
            Processo(pid=5, chegada=4, duracao=3, prioridade=1, peso=1024),    # Atualização de tela
            Processo(pid=6, chegada=6, duracao=25, prioridade=3, peso=1024),   # Desfragmentação
        ]
    
    @staticmethod
    def gerar_cenario_chegada_simultanea() -> List[Processo]:
        return [
            Processo(pid=1, chegada=0, duracao=8, prioridade=2, peso=1024),    # Init
            Processo(pid=2, chegada=0, duracao=4, prioridade=1, peso=1024),    # Kernel modules
            Processo(pid=3, chegada=0, duracao=12, prioridade=3, peso=1024),   # Service daemon
            Processo(pid=4, chegada=0, duracao=6, prioridade=1, peso=1024),    # Network manager
            Processo(pid=5, chegada=0, duracao=10, prioridade=2, peso=1024),   # Display manager
        ]
    
    @staticmethod
    def gerar_cenario_aleatorio(num_processos: int = 8, max_chegada: int = 10, min_duracao: int = 1, max_duracao: int = 20) -> List[Processo]:
        processos = []
        for i in range(num_processos):
            processo = Processo(
                pid=i+1,
                chegada=random.randint(0, max_chegada),
                duracao=random.randint(min_duracao, max_duracao),
                prioridade=random.randint(0, 3),
                peso=random.choice([512, 1024, 1536, 2048])
            )
            processos.append(processo)
        
        return sorted(processos, key=lambda x: x.chegada)
    
    @staticmethod
    def obter_todos_cenarios() -> dict:
        return {
            'Básico': GeradorDados.gerar_cenario_basico(),
            'Intensivo CPU': GeradorDados.gerar_cenario_intensivo_cpu(),
            'Misto (Interativo + Batch)': GeradorDados.gerar_cenario_misto(),
            'Chegada Simultânea': GeradorDados.gerar_cenario_chegada_simultanea(),
            'Aleatório': GeradorDados.gerar_cenario_aleatorio()
        }