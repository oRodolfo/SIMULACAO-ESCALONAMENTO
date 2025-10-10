# 🧠 Algoritmos de Escalonamento em Sistemas Operacionais  
> Projeto acadêmico — 4º Ano de Sistemas de Informação | Disciplina: Sistemas Operacionais I  
> Professor: Esp. William C. Augustonelli (Billy)

---

## 🎯 Objetivo do Projeto

Este projeto apresenta, de forma prática, o impacto dos **algoritmos de escalonamento de processos** em diferentes sistemas operacionais: **Windows, Linux e Android**.  
Foi desenvolvido um **simulador em Python** capaz de comparar os algoritmos **FCFS**, **SJF**, **Round Robin** e **CFS**, gerando relatórios interativos e análises detalhadas.

---

## 👥 Integrantes

| Nome | RA |
|------|----|
| Arthur Peixoto Lacerda | 116319 |
| Guilherme Henrique Cavarsan | 117017 |
| Octavio Thim Dias | 117607 |
| Rodolfo Henrique Ribeiro Zanchetta | 117179 |

---

## 📘 Resumo

O trabalho tem como objetivo **avaliar o desempenho dos principais algoritmos de escalonamento**, verificando como cada sistema operacional (Windows, Linux e Android) reage sob diferentes cargas de trabalho.

O simulador gera **relatórios interativos em HTML**, **gráficos comparativos** e **métricas consolidadas** (tempo de resposta, retorno, espera e throughput), permitindo observar como cada algoritmo se comporta em termos de desempenho e eficiência.

---

## 🚀 Funcionalidades Principais

- Implementação dos algoritmos clássicos:
  - **FCFS** (First Come, First Served)
  - **SJF** (Shortest Job First) – preemptivo e não preemptivo
  - **Round Robin** – com variação de quantum
  - **CFS** (Completely Fair Scheduler)
- Geração automática de cenários de simulação:
  - Básico, CPU-Intensivo, Misto, Sistema Local e Android (via ADB)
- Relatórios e gráficos automáticos:
  - Comparação de desempenho entre algoritmos
  - Análises detalhadas por cenário
  - Relatórios interativos em HTML

---

## 🧩 Algoritmos Implementados

| Algoritmo | Tipo | Características principais |
|------------|------|-----------------------------|
| **FCFS (First Come, First Served)** | Não preemptivo | Simples, porém sujeito ao “convoy effect” |
| **SJF (Shortest Job First)** | Preemptivo e não preemptivo | Reduz tempo médio de espera, mas pode gerar *starvation* |
| **Round Robin (RR)** | Preemptivo | Justo e eficiente em sistemas interativos |
| **CFS (Completely Fair Scheduler)** | Preemptivo | Baseado no Linux, equilibra justiça e desempenho |

---

## 🧮 Métricas Avaliadas

- ⏱️ **Tempo Médio de Resposta**
- 🔁 **Tempo Médio de Retorno**
- 🕓 **Tempo Médio de Espera**
- 📈 **Throughput**
- ⚙️ **Tempo Total de Execução**

---

## ⚙️ Tecnologias Utilizadas

- 🐍 **Python 3.11+**
- 📊 **Pandas, Numpy, Matplotlib, Seaborn**
- 💾 **ReportLab** (geração de relatórios PDF)
- 🔍 **Psutil** (coleta de métricas do sistema)
- 📱 **ADB (Android Debug Bridge)** (integração com dispositivos Android)
- 🧰 **Flask e Jinja2** (renderização de relatórios interativos)

---

## 📂 Estrutura do Projeto

```text
SIMULACAO-ESCALONAMENTO/
│
├── models/                  # Estruturas de dados (Processo, Resultado)
├── schedulers/              # Algoritmos de escalonamento (FCFS, SJF, RR, CFS)
├── utils/                   # Funções auxiliares, coleta e relatórios
│   ├── android_coletor.py
│   ├── analisador.py
│   ├── gerador_dados.py
│   └── main.py
│
├── relatorio_interativo.py
├── .gitignore
└── requirements.txt
```

---

## 🚀 Como Executar o Simulador

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/oRodolfo/SIMULACAO-ESCALONAMENTO.git
cd SIMULACAO-ESCALONAMENTO
```

### 2️⃣ Criar ambiente virtual
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

### 3️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 4️⃣ Executar o simulador
```bash
python main.py
```

---

### 🎮 Menu Interativo

Ao iniciar, o terminal exibirá:
```text
🎮 MENU DO SIMULADOR DE ESCALONAMENTO
============================================================
1. 🚀 Simulação Básica
2. 🔍 Simulação Detalhada
3. 🎯 Simulação Completa
4. 🧠 Cenário do meu computador
5. 🛠️  Cenário Personalizado
6. 📱 Cenário do meu Android (via ADB)
7. 🚪 Sair
============================================================
```

---

📊 Resultados e Relatórios

Durante a execução, o simulador gera automaticamente:
```tex
Tipo	                           Arquivo	Descrição
📄 relatorio_consolidado.txt	-> Relatório textual completo	
🌐 relatorio_interativo.html	-> Relatório dinâmico em HTML	
📊 resultados_simulacao.csv	  -> Dados brutos das métricas	
🧾 resultados_simulacao.json	-> Saída estruturada para visualização	
📈 comparacao_basica.png	    -> Gráfico comparativo dos algoritmos	
```

---

### 🧠 Conclusão

O simulador permitiu comprovar que:

-⚡ Windows: sensível ao algoritmo adotado, com forte variação entre resultados.

-🧩 Linux (WSL2): estabilidade e eficiência com o CFS.

-🤖 Android: comportamento uniforme, priorizando responsividade e experiência do usuário.

O trabalho confirma que a escolha do algoritmo de escalonamento impacta diretamente métricas fundamentais de desempenho do sistema.

---

### 📚 Referências Bibliográficas
```text
MACHADO, F. B.; MAIA, L. F. Arquitetura de Sistemas Operacionais. LTC, 2019.

TANENBAUM, A. S. Sistemas Operacionais Modernos. Pearson, 2015.

SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. Fundamentos de Sistemas Operacionais. LTC, 2013.

LINUX FOUNDATION. Linux Kernel Documentation.

ANDROID OPEN SOURCE PROJECT (AOSP). Android Developers Documentation.
```

---

###  📄 Relatório Completo do Projeto

[![Ver Relatório PDF](https://github.com/oRodolfo/SIMULACAO-ESCALONAMENTO/blob/3512afbc31679e3c8835a5512afdfd14e8fe825b/ALGORITMO%20DE%20ESCALONAMENTO%20EM%20SISTEMAS%20OPERACIONAIS.pdf)

---

### 🧾 Licença

Este projeto é de uso educacional e acadêmico.

---
