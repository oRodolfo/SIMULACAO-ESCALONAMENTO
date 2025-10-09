#importando as classes principais do módulo
from .processo import Processo
from .resultado import ResultadoSimulacao

#definindo quais são serão exportados ao importar cada pacote
__all__ = ["Processo", "ResultadoSimulacao"]