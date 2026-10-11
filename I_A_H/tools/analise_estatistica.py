import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
from sqlalchemy import create_engine
from itertools import combinations
import os

engine = create_engine(f'postgresql://postgres:aiskegoal@localhost:5432/i_a_h_db_lotes')

query = """
SELECT * FROM auction_items 
WHERE tier = 'legendary' 
AND name IN ('helmet of divan', 'chestplate of divan', 'leggings of divan', 'boots of divan')
"""

df = pd.read_sql(query, engine)

itens = ['helmet of divan', 'chestplate of divan', 'leggings of divan', 'boots of divan']

print("1 - Histograma")
print("2 - Q-Q Plot")
print("3 - Q-Q Plot + Shapiro-Wilk")
print("4 - Estatísticas descritivas (mediana, desvio, IQR)")
print("5 - Mann-Whitney + Levene (comparação par a par)")
opcao = input("Opção: ").strip()

if opcao == '4':
    for item in itens:
        dados = df[df['name'] == item]['price']
        mediana = dados.median()
        desvio = dados.std()
        q1 = dados.quantile(0.25)
        q3 = dados.quantile(0.75)
        n = dados.count()
        mad = stats.median_abs_deviation(dados)     

        print(f"\n--- {item} ---")
        print(f"N listagens: {n}")
        print(f"Mediana: {mediana:,.0f}")
        print(f"Desvio padrão: {desvio:,.0f}")
        print(f"IQR (Q3-Q1): {q3 - q1:,.0f}")
        print(f"Coef. de variação (desvio/mediana): {desvio/mediana:.2f}")
        print(f"MAD: {mad:,.0f}")
    exit()

if opcao == '5':
    # --- Kruskal-Wallis ---
    grupos = [df[df['name'] == item]['price'] for item in itens]
    stat_kw, p_kw = stats.kruskal(*grupos)

    print(f"\n=== Kruskal-Wallis (global, 4 grupos) ===")
    print(f"H={stat_kw:.2f}, p={p_kw:.6f}")

    if p_kw >= 0.05:
        print("-> Sem evidência de diferença entre os grupos. Não faz sentido prosseguir com post-hoc.")
        exit()

    print("-> Existe diferença entre os grupos. Prosseguindo com post-hoc (Mann-Whitney par a par)...\n")

    # --- Mann-Whitney par a par + Levene ---
    pares = list(combinations(itens, 2))
    resultados = []  # guarda tudo pra aplicar Bonferroni depois

    for item_a, item_b in pares:
        preco_a = df[df['name'] == item_a]['price']
        preco_b = df[df['name'] == item_b]['price']

        stat_mw, p_mw = stats.mannwhitneyu(preco_a, preco_b, alternative='two-sided')
        stat_lv, p_lv = stats.levene(preco_a, preco_b, center='median')

        resultados.append({
            'item_a': item_a, 'item_b': item_b,
            'stat_mw': stat_mw, 'p_mw': p_mw,
            'stat_lv': stat_lv, 'p_lv': p_lv,
            'mediana_a': preco_a.median(), 'mediana_b': preco_b.median(),
            'desvio_a': preco_a.std(), 'desvio_b': preco_b.std(),
        })

    # --- Bonferroni sobre os 6 p-valores do Mann-Whitney ---
    n_comparacoes = len(pares)
    alpha_ajustado = 0.05 / n_comparacoes

    print(f"Correção de Bonferroni: alpha ajustado = 0.05 / {n_comparacoes} = {alpha_ajustado:.4f}\n")

    for r in resultados:
        print(f"=== {r['item_a']}  vs  {r['item_b']} ===")

        # Mann-Whitney com Bonferroni
        p_mw_ajustado = min(r['p_mw'] * n_comparacoes, 1.0)  # p-valor ajustado, cap em 1.0
        print(f"Mann-Whitney: U={r['stat_mw']:.1f}, p={r['p_mw']:.4f}, p_ajustado={p_mw_ajustado:.4f}", end="  ")
        if r['p_mw'] < alpha_ajustado:
            maior = r['item_a'] if r['mediana_a'] > r['mediana_b'] else r['item_b']
            print(f"-> Diferença significativa ({maior} é mais caro)")
        else:
            print("-> Sem diferença significativa (após correção)")

        # Levene não entra no Bonferroni (não é post-hoc de comparação múltipla no mesmo sentido,
        print(f"Levene (volatilidade): W={r['stat_lv']:.1f}, p={r['p_lv']:.4f}", end="  ")
        if r['p_lv'] < 0.05:
            mais_volatil = r['item_a'] if r['desvio_a'] > r['desvio_b'] else r['item_b']
            print(f"-> Diferença significativa ({mais_volatil} é mais volátil)")
        else:
            print("-> Sem diferença significativa de volatilidade")
        print()

    exit()
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

if opcao == '1':
    for i, item in enumerate(itens):
        dados_item = df[df['name'] == item]
        sns.histplot(dados_item['price'], kde=True, bins=20, ax=axes[i])
        axes[i].set_title(f'{item} (Legendary)')
        axes[i].set_xlabel('Preço')

elif opcao == '2':
    for i, item in enumerate(itens):
        dados_item = df[df['name'] == item]
        stats.probplot(dados_item['price'], dist="norm", plot=axes[i])
        axes[i].set_title(f'{item} (Legendary) - Q-Q Plot')

elif opcao == '3':
    for i, item in enumerate(itens):
        dados_item = df[df['name'] == item]
        stat, p_valor = stats.shapiro(dados_item['price'])
        stats.probplot(dados_item['price'], dist="norm", plot=axes[i])
        veredito = "NÃO normal" if p_valor < 0.05 else "normal"
        axes[i].set_title(f'{item}\nW={stat:.3f}, p={p_valor:.4f} ({veredito})')

else:
    print("Opção inválida.")
    exit()

plt.tight_layout()
plt.show()