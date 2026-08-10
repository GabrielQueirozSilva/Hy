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
    # Gera todos os pares possíveis entre os 4 itens (6 pares no total)
    pares = list(combinations(itens, 2))

    for item_a, item_b in pares:
        preco_a = df[df['name'] == item_a]['price']
        preco_b = df[df['name'] == item_b]['price']

        # Mann-Whitney: existe diferença no NÍVEL de preço?
        stat_mw, p_mw = stats.mannwhitneyu(preco_a, preco_b, alternative='two-sided')

        # Levene: existe diferença na VOLATILIDADE (variância) de preço?
        stat_lv, p_lv = stats.levene(preco_a, preco_b, center='median')
        
        
        print(f"\n=== {item_a}  vs  {item_b} ===")

        print(f"Mann-Whitney (nível de preço): U={stat_mw:.1f}, p={p_mw:.4f}", end="  ")
        if p_mw < 0.05:
            mediana_a = preco_a.median()
            mediana_b = preco_b.median()
            maior = item_a if mediana_a > mediana_b else item_b
            print(f"-> Diferença significativa ({maior} é mais caro)")
        else:
            print("-> Sem diferença significativa")

        print(f"Levene (volatilidade):         W={stat_lv:.1f}, p={p_lv:.4f}", end="  ")
        if p_lv < 0.05:
            desvio_a = preco_a.std()
            desvio_b = preco_b.std()
            mais_volatil = item_a if desvio_a > desvio_b else item_b
            print(f"-> Diferença significativa ({mais_volatil} é mais volátil)")
        else:
            print("-> Sem diferença significativa de volatilidade")

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