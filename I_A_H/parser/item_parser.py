from thefuzz import fuzz
from .sanitizer import item_sanitizer
from ..constants import *
import re

def parse_item_data(text):
    item_data = {}
    discrepancia = False

    sanitized_text = item_sanitizer(text, context="GLOBAL")
    lines = sanitized_text.splitlines()
    if not lines:
        return {}, {}
    
    primeira_linha = lines[0].strip().lower()
    primeira_linha = item_sanitizer(primeira_linha, context="NAME")
    item_data['name'] = primeira_linha
    nome_limpo = item_data['name']
    
    quinta_ultima_linha = ""
    quarta_ultima_linha = ""
    terceira_ultima_linha = ""

    # --- ETAPA 1: EXTRAÇÃO DE DADOS BRUTOS ---           
    if len(lines) >= 5:
        quinta_ultima_linha = lines[-5].strip().lower()
        print(f"QUINTA ULTIMA LINHA: {quinta_ultima_linha}")
        
        quarta_ultima_linha = lines[-4].strip().lower()
        print(f"QUARTA ULTIMA LINHA: {quarta_ultima_linha}")
        quarta_ultima_linha = item_sanitizer(quarta_ultima_linha, context="SELLER")
    
        a = fuzz.partial_ratio("seller", quarta_ultima_linha)
        if a <= LIMITE_DE_CONFIANCA_GERAL:
            print(f"DISCREPANCIA DETECTADA: LINHAS COM PROBLEMA. Pontuação: {a}")
            discrepancia = True
            
        
        if discrepancia == False:
            print("entrou")
            #limpeza especifica
            terceira_ultima_linha = lines[-3].strip().lower()
            print(f"TERCEIRA ULTIMA LINHA: {terceira_ultima_linha}")
            terceira_ultima_linha = item_sanitizer(terceira_ultima_linha, context="PRICE")
            
            lines[0] = primeira_linha  # Atualiza a linha tratada no array original
            lines[-4] = quarta_ultima_linha  # Atualiza a linha tratada no array original
            lines[-3] = terceira_ultima_linha  # Atualiza a linha tratada no array original
            sanitized_text = '\n'.join(lines)

            #ANALISE BRUTA, PRIORITÁRIA, DAS ÚLTIMAS LINHAS
            # Pega a quinta última linha para o TIER
            melhor_pontuacao_tier = 0
            melhor_match_tier = None
            for tier in TIERS:
                pontuacao = fuzz.partial_ratio(tier,quinta_ultima_linha)
                if pontuacao > melhor_pontuacao_tier:
                    melhor_pontuacao_tier = pontuacao
                    melhor_match_tier = tier              
            item_data['tier'] = melhor_match_tier
            
            # Pega a quarta última linha para o SELLER   
            partes = quarta_ultima_linha.split(maxsplit=1)
            if len(partes) == 2:
                seller, vendedor = partes[0], partes[1]  
                if 'seller:' in seller.lower():
                    item_data['seller'] = vendedor.strip()
                else:
                    item_data['seller'] = None
                            
            # Pega a terceira última linha para o PRICE    
            try:
                
                parte_do_preco = terceira_ultima_linha.split(':', 1)[1]
                price_str = re.sub(r'[^\d]', '', parte_do_preco)
                if price_str:
                    item_data['price'] = int(price_str)
                    
            except (IndexError, ValueError):
                item_data['price'] = None                 


    # --- ETAPA 2: CLASSIFICAÇÃO INTELIGENTE DAS CLASSES ---
    if 'class' not in item_data and discrepancia == False: 
        melhor_pontuacao_pet = 0
        melhor_match_pet = None
        for pet_type in PET_TYPES:
            pontuacao = fuzz.partial_ratio(pet_type, nome_limpo)
            if pontuacao > melhor_pontuacao_pet:
                melhor_pontuacao_pet = pontuacao
                melhor_match_pet = pet_type
                
    #Caso especial, caso o item estaja classificado como special ou very special,
        if ('tier' in item_data) and (item_data['tier'] == "special" or item_data['tier'] == "very special"):
            item_data['class'] = "special_item" 
        
        #TENTAIVAS PELA QUINTA ÚLTIMA LINHA E PELO NOME DO ITEM
        # 1°-TENTATIVA. CLASSIFICAR COMO CONSUMABLE PELA QUINTA ÚLTIMA LINHA ou PELO NOME
        elif (any(fuzz.partial_ratio(keyword, quinta_ultima_linha) >= LIMITE_DE_CONFIANCA_GERAL for keyword in PET_ITENS_KEYWORDS)) or (any(fuzz.partial_ratio(keyword, nome_limpo) >= LIMITE_DE_CONFIANCA_GERAL for keyword in CONSUMABLE_TITLE)):
            item_data['class'] = "Consumables" 
        # 2°-TENTATIVA. CLASSIFICAR COMO ACESSORIO PELA QUINTA ÚLTIMA LINHA
        elif any(fuzz.partial_ratio(keyword, quinta_ultima_linha) >= LIMITE_DE_CONFIANCA_GERAL for keyword in ACCESSORY_KEYWORDS):
            item_data['class'] = "Accessory"
            
        elif any(fuzz.partial_ratio(keyword, nome_limpo) >= LIMITE_DE_CONFIANCA_GERAL for keyword in EQUIPAMENT_TITLES):
            item_data['class'] = "Equipment"
            
        #TENTATIVAS APENAS PELO NOME DO ITEM
        # 3°-TENTATIVA. CLASSIFICAR COMO COSMECT PELO NOME 
        elif any(fuzz.partial_ratio(keyword, nome_limpo) >= LIMITE_DE_CONFIANCA_GERAL for keyword in COSMETIC_KEYWORDS):  
            item_data['class'] = "Cosmetic"            
        # 4°-TENTATIVA. CLASSIFICAR COMO DYE PELO NOME 
        elif fuzz.partial_ratio("dye", nome_limpo) >= LIMITE_DE_CONFIANCA_GERAL:
            item_data['class'] = "Dye"               
        # 5°-TENTATIVA. CLASSIFICAR COMO RUNE PELO NOME 
        elif fuzz.partial_ratio("rune", nome_limpo) >= LIMITE_DE_CONFIANCA_GERAL:
            item_data['class'] = "Rune"
        # 6°-TENTATIVA. CLASSIFICAR COMO PET PELO NOME
        elif melhor_pontuacao_pet >= LIMITE_DE_CONFIANCA_PET:
            item_data['class'] = "Pet"
            item_data['pet_type'] = melhor_match_pet        
    
    
    #FUNÇÃO DE BACKUP(CASO NÃO TENHA ENCONTRADO VALORES AINDA)
    for line in lines[1:]: # Começa da segunda linha
        line_clean = line.strip().lower()
        if not line_clean:
            continue
        if ('price' not in item_data or item_data.get('price') is None) and any(keyword in line_clean for keyword in PRICE_KEYWORDS):
            try:
                parte_do_preco = line.split(':', 1)[1]
                price_str = re.sub(r'[^\d]', '', parte_do_preco)
                if price_str:
                    item_data['price'] = int(price_str)
            except (IndexError, ValueError):
                pass
            
        if ('seller' not in item_data or item_data.get('seller') is None) and "seller" in line_clean:
            partes = line_clean.split(maxsplit=1)
            if len(partes) == 2:
                seller, vendedor = partes[0], partes[1]  
                if 'seller:' in seller.lower():
                    item_data['seller'] = vendedor.strip()
                    
        if('tier' not in item_data or item_data.get('tier') is None) and any(keyword in line_clean for keyword in TIERS):
            for tier in TIERS:
                if fuzz.partial_ratio(tier, line_clean) >= LIMITE_DE_CONFIANCA_GERAL:
                    item_data['tier'] = tier
                    break
                    
        if 'class' not in item_data: 
            if any(keyword in line_clean for keyword in DUNGEON_KEYWORDS):
                item_data['class'] = "Item"
            elif any(keyword in line_clean for keyword in CONSUMABLES_KEYWORDS):
                item_data['class'] = "Consumables"
                         
    final_sanitized_text = '\n'.join(lines).lower()       
    return item_data, final_sanitized_text