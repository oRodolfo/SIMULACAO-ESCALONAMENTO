"""
Relatório Interativo do Simulador de Escalonamento
Permite navegar pelos resultados de forma dinâmica
"""

import os
import sys
import json
import re
import webbrowser

from typing import Dict, List, Any
from datetime import datetime

class RelatorioInterativo:
    # Carrega os dados e lista os cenários válidos
    def __init__(self, arquivo_dados="resultados_simulacao.json"):
        self.dados = {}
        self.carregar_dados(arquivo_dados)
        self.cenarios = [k for k in self.dados.keys() if not k.startswith("__")]
    
    def carregar_dados(self, arquivo):
        #Carrega dados do arquivo JSON ou simula dados se não existir
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                self.dados = json.load(f)
            print(f"✅ Dados carregados de '{arquivo}'")
        except FileNotFoundError:
            print(f"⚠️  Arquivo '{arquivo}' não encontrado. Usando dados de exemplo.")
            self.dados = self.dados_exemplo()
    
    #retorna um conjunto de dados exemplos para demonstração
    def dados_exemplo(self):
        return {
            "Básico": [
                {"algoritmo": "SJF (Preemptivo)", "tempo_medio_resposta": 4.00, "tempo_medio_retorno": 13.50, "tempo_medio_espera": 6.50, "throughput": 0.1429},
                {"algoritmo": "Round Robin (q=2)", "tempo_medio_resposta": 1.50, "tempo_medio_retorno": 18.50, "tempo_medio_espera": 11.50, "throughput": 0.1429},
                {"algoritmo": "FCFS", "tempo_medio_resposta": 8.00, "tempo_medio_retorno": 15.00, "tempo_medio_espera": 8.00, "throughput": 0.1429},
                {"algoritmo": "SJF (Não-Preemptivo)", "tempo_medio_resposta": 8.00, "tempo_medio_retorno": 15.00, "tempo_medio_espera": 8.00, "throughput": 0.1429},
                {"algoritmo": "CFS (Simplified)", "tempo_medio_resposta": 8.00, "tempo_medio_retorno": 15.00, "tempo_medio_espera": 8.00, "throughput": 0.1429},
                {"algoritmo": "Round Robin (q=4)", "tempo_medio_resposta": 4.00, "tempo_medio_retorno": 17.50, "tempo_medio_espera": 10.50, "throughput": 0.1429}
            ],
            "Intensivo CPU": [
                {"algoritmo": "SJF (Preemptivo)", "tempo_medio_resposta": 17.20, "tempo_medio_retorno": 46.60, "tempo_medio_espera": 28.60, "throughput": 0.0556},
                {"algoritmo": "SJF (Não-Preemptivo)", "tempo_medio_resposta": 30.60, "tempo_medio_retorno": 48.60, "tempo_medio_espera": 30.60, "throughput": 0.0556},
                {"algoritmo": "Round Robin (q=2)", "tempo_medio_resposta": 3.00, "tempo_medio_retorno": 74.40, "tempo_medio_espera": 56.40, "throughput": 0.0556},
            ],
            "Misto (Interativo + Batch)": [
                {"algoritmo": "SJF (Preemptivo)", "tempo_medio_resposta": 9.17, "tempo_medio_retorno": 20.67, "tempo_medio_espera": 9.67, "throughput": 0.0909},
                {"algoritmo": "SJF (Não-Preemptivo)", "tempo_medio_resposta": 11.50, "tempo_medio_retorno": 22.50, "tempo_medio_espera": 11.50, "throughput": 0.0909},
                {"algoritmo": "Round Robin (q=2)", "tempo_medio_resposta": 2.17, "tempo_medio_retorno": 30.17, "tempo_medio_espera": 19.17, "throughput": 0.0909},
            ]
        }

    #limpa o terminal automaticamente para deixar limpo apos as interações 
    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    #Mostra cabeçalho com data/hora e total de cenários
    def exibir_header(self):
        print("=" * 80)
        print("🚀 RELATÓRIO INTERATIVO - ALGORITMOS DE ESCALONAMENTO")
        print("=" * 80)
        print(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Cenários disponíveis: {len(self.cenarios)}")
        print("=" * 80)

    #Menu de navegação interativo no terminal
    def menu_principal(self):
        while True:
            self.limpar_tela()
            self.exibir_header()
            
            print("\n🎮 OPÇÕES DISPONÍVEIS:")
            print("1. 📊 Ver todos os cenários")
            print("2. 🎯 Analisar cenário específico")
            print("3. 🏆 Ranking geral dos algoritmos")
            print("4. 📈 Comparar dois algoritmos")
            print("5. 💡 Ver recomendações")
            print("6. 🔍 Buscar por algoritmo")
            print("7. 📄 Gerar relatório HTML")
            print("8. 🚪 Sair")
            
            try:
                opcao = input("\n👉 Escolha uma opção (1-8): ").strip()
                
                if opcao == "1":
                    self.ver_todos_cenarios()
                elif opcao == "2":
                    self.analisar_cenario_especifico()
                elif opcao == "3":
                    self.ranking_geral()
                elif opcao == "4":
                    self.comparar_algoritmos()
                elif opcao == "5":
                    self.ver_recomendacoes()
                elif opcao == "6":
                    self.buscar_algoritmo()
                elif opcao == "7":
                    self.gerar_html_interativo()
                elif opcao == "8":
                    print("👋 Obrigado por usar o Relatório Interativo!")
                    break
                else:
                    print("❌ Opção inválida!")
                    input("Pressione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n👋 Programa encerrado pelo usuário.")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                input("Pressione Enter para continuar...")

    #Exibe visão geral de todos os cenários
    def ver_todos_cenarios(self):
        self.limpar_tela()
        print("📊 VISÃO GERAL - TODOS OS CENÁRIOS")
        print("=" * 80)
        
        for i, cenario in enumerate(self.cenarios, 1):
            resultados = self.dados[cenario]
            melhor = min(resultados, key=lambda x: x['tempo_medio_resposta'])
            
            print(f"\n{i}. 🎯 {cenario}")
            print(f"   Algoritmos testados: {len(resultados)}")
            print(f"   Melhor tempo resposta: {melhor['algoritmo']} ({melhor['tempo_medio_resposta']:.2f})")
            
            # Barra visual simples
            max_resp = max(r['tempo_medio_resposta'] for r in resultados)
            barra_tamanho = int((melhor['tempo_medio_resposta'] / max_resp) * 20)
            barra = "█" * barra_tamanho + "░" * (20 - barra_tamanho)
            print(f"   Performance: {barra} {melhor['tempo_medio_resposta']:.1f}")
        
        input("\n⏸️  Pressione Enter para voltar ao menu...")

    #Lista cenários e exibe detalhes do escolhido
    def analisar_cenario_especifico(self):
        self.limpar_tela()
        print("🎯 ANÁLISE DETALHADA DE CENÁRIO")
        print("=" * 50)
        
        # Lista cenários
        for i, cenario in enumerate(self.cenarios, 1):
            print(f"{i}. {cenario}")
        
        try:
            escolha = int(input(f"\nEscolha um cenário (1-{len(self.cenarios)}): ")) - 1
            if 0 <= escolha < len(self.cenarios):
                cenario_nome = self.cenarios[escolha]
                self.exibir_detalhes_cenario(cenario_nome)
            else:
                print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")
        
        input("\n⏸️  Pressione Enter para voltar...")

    #Mostra tabela com métricas e destaques do cenário
    def exibir_detalhes_cenario(self, cenario_nome):
        self.limpar_tela()
        resultados = self.dados[cenario_nome]
        
        print(f"🎯 ANÁLISE DETALHADA: {cenario_nome.upper()}")
        print("=" * 80)
        
        #Cabeçalho da tabela
        print(f"{'Pos':<4} {'Algoritmo':<25} {'Resp':<8} {'Ret':<8} {'Esp':<8} {'Thrpt':<8}")
        print("-" * 80)
        
        #Ordena por tempo de resposta
        resultados_ordenados = sorted(resultados, key=lambda x: x['tempo_medio_resposta'])
        
        for i, resultado in enumerate(resultados_ordenados, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"{emoji:<4} {resultado['algoritmo']:<25} "
                  f"{resultado['tempo_medio_resposta']:<8.2f} "
                  f"{resultado['tempo_medio_retorno']:<8.2f} "
                  f"{resultado['tempo_medio_espera']:<8.2f} "
                  f"{resultado['throughput']:<8.4f}")
        
        # Análise do melhor algoritmo com base na comparação com os resultados
        melhor = resultados_ordenados[0]
        print(f"\n🏆 ALGORITMO VENCEDOR: {melhor['algoritmo']}")
        print(f"   • Tempo de Resposta: {melhor['tempo_medio_resposta']:.2f}")
        print(f"   • Throughput: {melhor['throughput']:.4f}")
        
        # Comparação com o pior resultado
        pior = resultados_ordenados[-1]
        melhoria = ((pior['tempo_medio_resposta'] - melhor['tempo_medio_resposta']) / pior['tempo_medio_resposta']) * 100
        print(f"   • Melhoria vs pior: {melhoria:.1f}% mais rápido")

    #Exibe ranking geral dos algoritmos
    def ranking_geral(self):
        self.limpar_tela()
        print("🏆 RANKING GERAL DOS ALGORITMOS")
        print("=" * 60)
        
        #Somando pontos por posição em cada cenário
        vitorias = {}
        for cenario, resultados in self.dados.items():
            if cenario.startswith("__"):
                continue
            ordenados = sorted(resultados, key=lambda x: x['tempo_medio_resposta'])
            for i, resultado in enumerate(ordenados):
                alg = resultado['algoritmo']
                if alg not in vitorias:
                    vitorias[alg] = {'1º': 0, '2º': 0, '3º': 0, 'pontos': 0}
                if i == 0:
                    vitorias[alg]['1º'] += 1
                    vitorias[alg]['pontos'] += 3
                elif i == 1:
                    vitorias[alg]['2º'] += 1
                    vitorias[alg]['pontos'] += 2
                elif i == 2:
                    vitorias[alg]['3º'] += 1
                    vitorias[alg]['pontos'] += 1
        
        # Ordena por pontos
        ranking = sorted(vitorias.items(), key=lambda x: x[1]['pontos'], reverse=True)
        
        print(f"{'Pos':<4} {'Algoritmo':<25} {'1º':<4} {'2º':<4} {'3º':<4} {'Pts':<4}")
        print("-" * 60)
        
        for i, (algoritmo, stats) in enumerate(ranking, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}º"
            print(f"{emoji:<4} {algoritmo:<25} {stats['1º']:<4} {stats['2º']:<4} {stats['3º']:<4} {stats['pontos']:<4}")
        
        # Análise do campeão
        campeao = ranking[0]
        print(f"\n🏆 ALGORITMO MAIS VERSÁTIL: {campeao[0]}")
        print(f"   • Total de pontos: {campeao[1]['pontos']}")
        print(f"   • Vitórias: {campeao[1]['1º']}")
        print(f"   • Pódios: {campeao[1]['1º'] + campeao[1]['2º'] + campeao[1]['3º']}")
        
        input("\n⏸️  Pressione Enter para voltar...")

    #Compara dois algoritmos específicos
    def comparar_algoritmos(self):
        self.limpar_tela()
        print("📈 COMPARAÇÃO ENTRE ALGORITMOS")
        print("=" * 50)
        
        # Lista algoritmos únicos
        algoritmos = sorted({
            r['algoritmo']
            for c in self.cenarios
            for r in (self.dados.get(c, []) or [])
            if isinstance(self.dados.get(c, []), list)
        })
        
        print("Algoritmos disponíveis:")
        for i, alg in enumerate(algoritmos, 1):
            print(f"{i}. {alg}")
        
        try:
            print(f"\nEscolha 2 algoritmos para comparar:")
            alg1_idx = int(input("Primeiro algoritmo (número): ")) - 1
            alg2_idx = int(input("Segundo algoritmo (número): ")) - 1
            
            if 0 <= alg1_idx < len(algoritmos) and 0 <= alg2_idx < len(algoritmos):
                alg1 = algoritmos[alg1_idx]
                alg2 = algoritmos[alg2_idx]
                self.exibir_comparacao(alg1, alg2)
            else:
                print("❌ Números inválidos!")
        except ValueError:
            print("❌ Digite números válidos!")
        
        input("\n⏸️  Pressione Enter para voltar...")

    #Exibe comparação detalhada entre dois algoritmos
    def exibir_comparacao(self, alg1, alg2):
        self.limpar_tela()
        print(f"⚔️  COMPARAÇÃO: {alg1} vs {alg2}")
        print("=" * 80)
        
        print(f"{'Cenário':<25} {'Métrica':<15} {alg1:<10} {alg2:<10} {'Vencedor':<15}")
        print("-" * 80)
        
        vitorias = {alg1: 0, alg2: 0}
        
        for cenario, resultados in self.dados.items():
            if cenario.startswith("__"):
                continue
            dados_alg1 = next((r for r in resultados if r['algoritmo'] == alg1), None)
            dados_alg2 = next((r for r in resultados if r['algoritmo'] == alg2), None)
            
            if dados_alg1 and dados_alg2:
                # Tempo de resposta
                v1, v2 = dados_alg1['tempo_medio_resposta'], dados_alg2['tempo_medio_resposta']
                vencedor = alg1 if v1 < v2 else alg2
                if v1 != v2:
                    vitorias[vencedor] += 1
                print(f"{cenario:<25} {'Resposta':<15} {v1:<10.2f} {v2:<10.2f} {vencedor:<15}")
                
                # Throughput
                v1, v2 = dados_alg1['throughput'], dados_alg2['throughput']
                vencedor = alg1 if v1 > v2 else alg2
                if v1 != v2:
                    vitorias[vencedor] += 1
                print(f"{'':<25} {'Throughput':<15} {v1:<10.4f} {v2:<10.4f} {vencedor:<15}")
                print()
        
        # Resultado final
        print("🏆 RESULTADO FINAL:")
        if vitorias[alg1] > vitorias[alg2]:
            print(f"   Vencedor: {alg1} ({vitorias[alg1]} vs {vitorias[alg2]})")
        elif vitorias[alg2] > vitorias[alg1]:
            print(f"   Vencedor: {alg2} ({vitorias[alg2]} vs {vitorias[alg1]})")
        else:
            print("   Empate!")

    #Busca informações sobre um algoritmo específico
    def buscar_algoritmo(self):
        self.limpar_tela()
        print("🔍 BUSCA POR ALGORITMO")
        print("=" * 30)
        
        termo = input("Digite o nome do algoritmo (ou parte): ").strip().lower()
        
        resultados_busca = {}
        for cenario, resultados in self.dados.items():
            if cenario.startswith("__"):
                continue
            for resultado in resultados:
                if termo in resultado['algoritmo'].lower():
                    if resultado['algoritmo'] not in resultados_busca:
                        resultados_busca[resultado['algoritmo']] = []
                    resultados_busca[resultado['algoritmo']].append((cenario, resultado))
        
        if resultados_busca:
            print(f"\n📊 RESULTADOS PARA '{termo.upper()}':")
            print("=" * 60)
            
            for algoritmo, dados in resultados_busca.items():
                print(f"\n🔸 {algoritmo}")
                print("-" * 40)
                
                for cenario, resultado in dados:
                    print(f"   {cenario:<20} | Resp: {resultado['tempo_medio_resposta']:>6.2f} | "
                          f"Thrpt: {resultado['throughput']:>6.4f}")
                
                # Estatísticas
                tempos = [r[1]['tempo_medio_resposta'] for r in dados]
                print(f"   📊 Média geral: {sum(tempos)/len(tempos):.2f}")
                print(f"   🏆 Melhor cenário: {min(dados, key=lambda x: x[1]['tempo_medio_resposta'])[0]}")
        else:
            print(f"❌ Nenhum algoritmo encontrado para '{termo}'")
        
        input("\n⏸️  Pressione Enter para voltar...")

    #Exibe recomendações baseadas nos resultados
    def ver_recomendacoes(self):
        self.limpar_tela()
        print("💡 RECOMENDAÇÕES DE USO")
        print("=" * 40)
        
        # Análise automática dos dados
        melhor_geral = self.encontrar_melhor_geral()
        melhor_responsivo = self.encontrar_mais_responsivo()
        melhor_throughput = self.encontrar_melhor_throughput()
        
        print(f"🏆 ALGORITMO MAIS VERSÁTIL:")
        print(f"   {melhor_geral}")
        print(f"   → Recomendado para sistemas multipropósito")
        
        print(f"\n⚡ MAIS RESPONSIVO:")
        print(f"   {melhor_responsivo}")
        print(f"   → Ideal para sistemas interativos")
        
        print(f"\n🚀 MELHOR THROUGHPUT:")
        print(f"   {melhor_throughput}")
        print(f"   → Perfeito para sistemas batch/servidor")
        
        print(f"\n📋 RECOMENDAÇÕES POR TIPO DE SISTEMA:")
        print("-" * 50)
        print("🖥️  Desktop/Interativo:")
        print("   → Round Robin (baixa latência)")
        print("   → CFS (equidade)")
        
        print("\n⚙️  Servidor/Batch:")
        print("   → SJF (eficiência)")
        print("   → FCFS (simplicidade)")
        
        print("\n🔄 Tempo Real:")
        print("   → Round Robin com quantum pequeno")
        print("   → Preemptivo para garantir deadlines")
        
        print("\n🌐 Sistemas Operacionais Reais:")
        print("   → Linux: CFS (Completely Fair Scheduler)")
        print("   → Windows: Algoritmo multinível preemptivo")
        print("   → RTOS: Rate Monotonic ou EDF")
        
        input("\n⏸️  Pressione Enter para voltar...")

    def encontrar_melhor_geral(self):
        pontuacoes = {}
        for cenario in self.cenarios:                       # <<< use apenas cenários válidos
            resultados = self.dados.get(cenario, [])
            if not isinstance(resultados, list):
                continue
            ordenados = sorted(resultados, key=lambda x: x['tempo_medio_resposta'])
            for i, resultado in enumerate(ordenados):
                alg = resultado['algoritmo']
                pontuacoes[alg] = pontuacoes.get(alg, 0) + (len(ordenados) - i)
        return max(pontuacoes.items(), key=lambda x: x[1])[0] if pontuacoes else "—"


    def encontrar_mais_responsivo(self):
        tempos_resposta = {}
        for cenario in self.cenarios:                       # <<< use apenas cenários válidos
            resultados = self.dados.get(cenario, [])
            if not isinstance(resultados, list):
                continue
            for r in resultados:
                tempos_resposta.setdefault(r['algoritmo'], []).append(r['tempo_medio_resposta'])
        if not tempos_resposta:
            return "—"
        medias = {alg: sum(ts)/len(ts) for alg, ts in tempos_resposta.items()}
        return min(medias.items(), key=lambda x: x[1])[0]

    def encontrar_melhor_throughput(self):
        thr = {}
        for cenario in self.cenarios:                       # <<< use apenas cenários válidos
            resultados = self.dados.get(cenario, [])
            if not isinstance(resultados, list):
                continue
            for r in resultados:
                thr.setdefault(r['algoritmo'], []).append(r['throughput'])
        if not thr:
            return "—"
        medias = {alg: sum(vals)/len(vals) for alg, vals in thr.items()}
        return max(medias.items(), key=lambda x: x[1])[0]

    # -------------------- HTML --------------------
    #Cria um id simples para HTML a partir do nome do cenário
    @staticmethod
    def _slug(texto: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-")
        return s or "secao"

    def gerar_html_interativo(self, saida_html: str = 'relatorio_interativo.html', abrir_navegador: bool = True):
        html_content = self.criar_html_dinamico()
        caminho_absoluto = os.path.abspath(saida_html)

        try:
            with open(saida_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Relatório HTML gerado: '{saida_html}'")

            if abrir_navegador:
                webbrowser.open(f"file://{caminho_absoluto}")
                print("🌐 Abrindo no navegador padrão...")
        except Exception as e:
            print(f"❌ Erro ao gerar HTML: {e}")

    #Cria HTML dinâmico baseado nos dados atuais
    def criar_html_dinamico(self):
        meta = self.dados.get("__meta__", {})
        run_id = meta.get("run_id", "—")
        generated_at = meta.get("generated_at", "—")
        cwd = meta.get("cwd", "—")

        destaques = self.dados.get("__destaques__", {})
        mv_txt  = destaques.get("mais_versatil")
        mr_txt  = (destaques.get("mais_responsivo") or {}).get("algoritmo")
        thr_txt = (destaques.get("melhor_throughput") or {}).get("algoritmo")

        # Fallbacks: se o JSON antigo não tiver __destaques__, calculamos como antes
        if not mv_txt:
            mv_txt = self.encontrar_melhor_geral()
        if not mr_txt:
            mr_txt = self.encontrar_mais_responsivo()
        if not thr_txt:
            thr_txt = self.encontrar_melhor_throughput()
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Interativo - Algoritmos de Escalonamento</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.15); }}
        h1 {{ color: #4f46e5; text-align: center; margin-bottom: 30px; font-size: 2.5em; }}
        h2 {{ color: #4f46e5; border-bottom: 3px solid #4f46e5; padding-bottom: 10px; }}
        .cenario-section {{ background: #f8fafc; margin: 20px 0; padding: 20px; border-radius: 10px; border-left: 5px solid #4f46e5; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; color: #000000; font-weight: bold;}}
        th {{ background: #4f46e5; color: white; font-weight: 600; cursor: pointer; }}
        tr:nth-child(even) {{ background: #f9fafb; }}
        tr:hover {{ background: #e0e7ff; }}
        .destaque {{ display: none !important; }}   
        .algoritmo-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin: 2px; }}
        .badge-1 {{ background: #fef3c7; color: #92400e; }}
        .badge-2 {{ background: #e0e7ff; color: #3730a3; }}
        .badge-3 {{ background: #dcfce7; color: #166534; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #ffffff; color: #000000; padding: 15px; border-radius: 8px; text-align: center; }}
        .footer {{ text-align: center; margin-top: 40px; color: #6b7280; font-size: 0.9em; }}
        .hint {{ display: none !important; }}
        .destaque .stats {{ display: none !important; }}
        th {{ cursor: pointer; user-select: none; }}
        th.sort-asc::after {{ content: " ▲"; font-size: 0.9em; }}
        th.sort-desc::after {{ content: " ▼"; font-size: 0.9em; }}
    </style>
    <script>
    function ordenarTabela(tabelaId, coluna) {{
        const tabela = document.getElementById(tabelaId);
        if (!tabela) return;
        const tbody = tabela.querySelector('tbody');
        const linhas = Array.from(tbody.rows);
        const isNumeric = !isNaN(parseFloat(linhas[0]?.cells[coluna].textContent || "").replace(',', '.'));

        linhas.sort((a, b) => {{
            const aTxt = a.cells[coluna].textContent.trim().replace(',', '.');
            const bTxt = b.cells[coluna].textContent.trim().replace(',', '.');

            if (isNumeric) {{
                return parseFloat(aTxt) - parseFloat(bTxt);
            }} else {{
                return aTxt.localeCompare(bTxt);
            }}
        }});

        tbody.innerHTML = '';
        linhas.forEach(linha => tbody.appendChild(linha));
    }}
    </script>
    </head>
    <body>
    <h1>Relatório Interativo - Algoritmos de Escalonamento</h1>
    <p style="margin:6px 0 16px;color:#64748b">
        Execução: <strong>{run_id}</strong> • Gerado em: <strong>{generated_at}</strong><br/>
        Pasta de origem: <code>{cwd}</code>
    </p>
"""
        # Seções por cenário
        for cenario, resultados in self.dados.items():
            if cenario.startswith("__"):
                continue
            tabela_id = f"tabela-{self._slug(cenario)}"
            # Ordena por tempo de resposta para marcar top 3 visualmente
            ordenados = sorted(resultados, key=lambda x: x['tempo_medio_resposta'])
            top3_alg = {ordenados[i]['algoritmo'] for i in range(min(3, len(ordenados)))}

            html += f"""
        <div class="cenario-section" id="{self._slug(cenario)}">
            <h2>🎯 {cenario}</h2>
            <table id="{tabela_id}" class="tabela-ordenavel">
                <thead>
                    <tr>
                        <th onclick="ordenarTabela('{tabela_id}', 0)">Algoritmo</th>
                        <th onclick="ordenarTabela('{tabela_id}', 1)">Tempo Médio de Resposta</th>
                        <th onclick="ordenarTabela('{tabela_id}', 2)">Tempo Médio de Retorno</th>
                        <th onclick="ordenarTabela('{tabela_id}', 3)">Tempo Médio de Espera</th>
                        <th onclick="ordenarTabela('{tabela_id}', 4)">Throughput</th>
                        <th onclick="ordenarTabela('{tabela_id}', 5)">Posição</th>
                    </tr>
                </thead>
                <tbody>
"""
            # Mantém a ordem original; posição será calculada com base no ranking por resposta
            ranking_por_resposta = {r['algoritmo']: i+1 for i, r in enumerate(ordenados)}
            for r in resultados:
                alg = r['algoritmo']
                pos = ranking_por_resposta.get(alg, "—")
                badge_class = ""
                if pos == 1:
                    badge_class = "badge-1"
                elif pos == 2:
                    badge_class = "badge-2"
                elif pos == 3:
                    badge_class = "badge-3"
                alg_cell = f"<span class='algoritmo-badge {badge_class}'>{alg}</span>" if alg in top3_alg else alg
                html += f"""                    <tr>
                        <td>{alg_cell}</td>
                        <td>{r['tempo_medio_resposta']:.2f}</td>
                        <td>{r['tempo_medio_retorno']:.2f}</td>
                        <td>{r['tempo_medio_espera']:.2f}</td>
                        <td>{r['throughput']:.4f}</td>
                        <td>{pos}</td>
                    </tr>
"""
            html += """                </tbody>
            </table>
        </div>
"""
        html += f"""
        <div class="footer">
            <p>Relatório gerado em: <strong>{generated_at}</strong> • Execução <strong>{run_id}</strong></p>
            <p>Use o script no terminal para explorar mais opções: ranking, comparação, recomendações e busca.</p>
        </div>
    </div>
</body>
</html>
"""
        return html


# ===================== MAIN =====================
# Permite informar o caminho do JSON via linha de comando
def main():
    arquivo = sys.argv[1] if len(sys.argv) > 1 else "resultados_simulacao.json"
    rel = RelatorioInterativo(arquivo)
    rel.menu_principal()
if __name__ == "__main__":
    main()