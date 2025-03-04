import random
from datetime import datetime
import json
import hashlib
import string

from banco import SGBD
from Geral import metodos

class AlgoritmoGenetico():     
    
    def __init__(self):        
        self.pdo = SGBD()
        self.fn = metodos()        
        
        
    def criar_aposta(self):
        return sorted(random.sample(range(1, 26), 15))

    def populacao_inicial(self, tamanho):
        return [self.criar_aposta() for _ in range(tamanho)]

    def fitness(self, individuo):    
    
        pontuacao_maxima = 100
        pontos_acertos = 0    
        
        # Pontos acertos
        if individuo['quinze_acertos'] >= 1:
            pontos_acertos += individuo['quinze_acertos'] * 300
        if individuo['quatorze_acertos'] >= 1:
            pontos_acertos += individuo['quatorze_acertos'] * 150
        if individuo['treze_acertos'] >= 1:
            pontos_acertos += individuo['treze_acertos'] * 50
        if individuo['doze_acertos'] >= 1:
            pontos_acertos += individuo['doze_acertos'] * 10
        if individuo['onze_acertos'] >= 1:
            pontos_acertos += individuo['onze_acertos'] * 2
        
        # Pontos simples por estarem dentro dos números mais frequentes
        numeros_frequentes = self.fn.getNumerosFrequentes()        
        pontos_frequencia = sum(1 for num in individuo['cromossomo'] if num in numeros_frequentes)
        
        # Pontuação por balanceamento
        pares = 0    
        for gene in individuo['cromossomo']:
            if gene % 2 == 0:
                pares += 1        
        
        pontos_balanceamento = 0
        if pares >= 7 and pares <= 8:
            pontos_balanceamento = 15
        elif pares == 6 or pares == 9:
            pontos_balanceamento = 10
        elif pares == 5 or pares == 10:
            pontos_balanceamento = 5
            
            
        total = pontos_acertos + pontos_frequencia + pontos_balanceamento
        total /= pontuacao_maxima
        
        # print(f'{pontos_acertos} Acertos + {pontos_frequencia} de frequencia + {pontos_balanceamento} pontos de balanceamento. \t TOTAL: {total}')
        return total            
    
    def cruzamento(self, pai1, pai2):
        pai1 = pai1['cromossomo']
        pai2 = pai2['cromossomo']
        
        filho = list(set(pai1[:8] + pai2[8:]))        
        
        while len(filho) < 15:        
            num = random.randint(1, 25)
            if num not in filho:
                filho.append(num)
        
        ordenado = sorted(filho)            
        
        item = {
            'cromossomo': ordenado,
            'fitness': 0,
            'onze_acertos': 0,
            'doze_acertos': 0,
            'treze_acertos': 0,
            'quatorze_acertos': 0,
            'quinze_acertos': 0
        }
        
        item['fitness'] = self.fitness(item)
        
        return item

    def mutacao(self, filho, taxa=0.2):
        
        aposta = filho['cromossomo']    
        
        if random.random() < taxa:        
            idx = random.randint(0, 14)
            novo_num = random.randint(1, 25)
            while novo_num in aposta:
                novo_num = random.randint(1, 25)
            aposta[idx] = novo_num        
        
        item = {
            'cromossomo': aposta,
            'fitness': 0,
            'onze_acertos': 0,
            'doze_acertos': 0,
            'treze_acertos': 0,
            'quatorze_acertos': 0,
            'quinze_acertos': 0
        }
        
        item['fitness'] = self.fitness(item)
        
        return item

    def selecao_inicial(self, populacao):
        
        dados = []
        
        # Pontuando ele
        for individuo in populacao:
            item = {
                'cromossomo': individuo,
                'fitness': 0,
                'onze_acertos': 0,
                'doze_acertos': 0,
                'treze_acertos': 0,
                'quatorze_acertos': 0,
                'quinze_acertos': 0
            }
            
            item['fitness'] = self.fitness(item)
            
            dados.append(item)
        
        # Ordenando ele
        dados_ordenado = sorted(dados, key=lambda x: x['fitness'], reverse=True)    
        
        return dados_ordenado
                    
    def selecao(self, populacao):        
    
        # Aqui já rodou uma vez e têm-se os dados de acertos
        for individuo in populacao:
            individuo['fitness'] = self.fitness(individuo)       
        
        # Ordenando ele
        dados_ordenado = sorted(populacao, key=lambda x: x['fitness'], reverse=True)    
        
        return dados_ordenado
                
    def algoritmo_genetico(self, geracoes=100, tamanho_populacao=50, jogos_treinamento=100, save=False):        
    
        geracoes += 1
        populacao = self.populacao_inicial(tamanho_populacao)            
        passam_direto_percent = 0.1
        passam_direto = tamanho_populacao * passam_direto_percent
        if passam_direto < 1:
            passam_direto = 1        
        progress = 0
        
        the_best = []
        the_most_wanted = []
        
        jogos_base = self.pdo.select(f'select * from dataframe order by random() limit {jogos_treinamento}')
        
        # Log dos resultados        
        nome = hashlib.md5(self.fn.gerar_str_aleatoria().encode()).hexdigest()
        
        inicio = datetime.now()    
        
        for geracao in range(geracoes):                                                                
            
            if geracao == 0:
                populacao = self.selecao_inicial(populacao) # Isso coloca no padrão json e ordena por fitness    
                print(f'\n\t\t{geracao+1}° Geracao \t [Calculando...]\n')                    
            else:
                populacao = self.selecao(populacao) # Aplica o fitness com os acertos passados
                
                # Salvando os melhores dos melhores
                if len(the_best) == 0: # na primeira geração só passamos direto sem comparar
                    the_best = populacao
                else:                                                                                                         
                    for individuo in populacao:
                        for idx, best in enumerate(the_best):
                            
                            # Salvando os que acertaram as melhores apostas
                            if individuo['quatorze_acertos'] > 1 or individuo['quinze_acertos'] > 1:
                                the_most_wanted.append(individuo)
                            
                            # Salvando/Trocando na lista dos melhores
                            if individuo['fitness'] > best['fitness']:
                                the_best[idx] = individuo
                                break
                            
                    if save:
                        self.fn.saveResultado(populacao, nome, (geracao+1))  
                        
                    fim = datetime.now()
                    delta = self.fn.calcular_tempo_decorrido(inicio, fim)                
                    print(f'\n\t\t{geracao+1}° Geracao \t [{delta}]\n')
                    inicio = datetime.now()
                
            
            # Criando a nova população
            nova_populacao = []
            # Passam direto os X primeiros colocados        
            passaram_direto = populacao[:int(passam_direto)]        
            nova_populacao = passaram_direto
            
            while len(nova_populacao) < tamanho_populacao:                        
                            
                pai1, pai2 = random.sample(populacao, 2)            
                filho = self.cruzamento(pai1, pai2)   
                filho = self.mutacao(filho)                                                    
                
                nova_populacao.append(filho)
            populacao = nova_populacao                    

            # Re-avaliar a nova população        
            for individuo in populacao:                        
                
                houve_acertos = False
                onze_acertos = 0
                doze_acertos = 0
                treze_acertos = 0
                quatorze_acertos = 0
                quinze_acertos = 0
                
                # Joga elas na selva
                for jogo in jogos_base:
                    
                    progress += 1
                    acertos = self.fn.getNumeroAcertos(jogo, individuo['cromossomo'])
                    
                    if acertos == 11:
                        onze_acertos += 1
                        houve_acertos = True
                    elif acertos == 12:
                        doze_acertos += 1
                        houve_acertos = True
                    elif acertos == 13:
                        treze_acertos += 1
                        houve_acertos = True
                    elif acertos == 14:
                        quatorze_acertos += 1
                        houve_acertos = True
                    elif acertos == 15:
                        quinze_acertos += 1      
                        houve_acertos = True
                        
                # Salva o resultado no indivíduo
                individuo['onze_acertos'] = onze_acertos
                individuo['doze_acertos'] = doze_acertos
                individuo['treze_acertos'] = treze_acertos
                individuo['quatorze_acertos'] = quatorze_acertos
                individuo['quinze_acertos'] = quinze_acertos
                
                # if houve_acertos:
                #     print(f'Resultado: {individuo}')                        
                # print('-----------------------------------------')                                                                                    

        
        # Apresentando os resultados
        # print('\t\t\t\n\nTHE MOST WANTED\n\n')
        # print(the_most_wanted)
        print(f'DONE - {nome}')