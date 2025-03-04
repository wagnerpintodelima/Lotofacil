import random
from datetime import datetime
import json
import hashlib
import string

from banco import SGBD

class metodos():
    
    def __init__(self):        
        self.pdo = SGBD()        
    
    def gerar_str_aleatoria(self, tamanho=10):
        caracteres = string.ascii_letters + string.digits  # Letras maiúsculas, minúsculas e números
        return ''.join(random.choices(caracteres, k=tamanho))
    
    def calcular_tempo_decorrido(self, inicio, fim):
        delta = fim - inicio
        segundos = delta.total_seconds()

        if segundos < 60:
            return f"{segundos:.2f} segundos"
        elif segundos < 3600:
            minutos = segundos / 60
            return f"{minutos:.2f} minutos"
        elif segundos < 86400:
            horas = segundos / 3600
            return f"{horas:.2f} horas"
        else:
            dias = segundos / 86400
            return f"{dias:.2f} dias"
        
    def getNumerosFrequentes(self):
        query = f"""
            WITH numeros AS (
            SELECT dezena_1 AS numero FROM dataframe
            UNION ALL
            SELECT dezena_2 FROM dataframe
            UNION ALL
            SELECT dezena_3 FROM dataframe
            UNION ALL
            SELECT dezena_4 FROM dataframe
            UNION ALL
            SELECT dezena_5 FROM dataframe
            UNION ALL
            SELECT dezena_6 FROM dataframe
            UNION ALL
            SELECT dezena_7 FROM dataframe
            UNION ALL
            SELECT dezena_8 FROM dataframe
            UNION ALL
            SELECT dezena_9 FROM dataframe
            UNION ALL
            SELECT dezena_10 FROM dataframe
            UNION ALL
            SELECT dezena_11 FROM dataframe
            UNION ALL
            SELECT dezena_12 FROM dataframe
            UNION ALL
            SELECT dezena_13 FROM dataframe
            UNION ALL
            SELECT dezena_14 FROM dataframe
            UNION ALL
            SELECT dezena_15 FROM dataframe
        )
        SELECT numero, COUNT(*) AS quantidade
        FROM numeros
        GROUP BY numero
        ORDER BY quantidade DESC
        LIMIT 15;
        """
        
        dados = self.pdo.select(query)
        
        numeros_frequentes = [dado['numero'] for dado in dados]   
        
        return numeros_frequentes         
                
    def getNumeroAcertos(self, jogo, aposta):
    
        dezenas_real = [
            jogo['dezena_1'], jogo['dezena_2'], jogo['dezena_3'], jogo['dezena_4'], jogo['dezena_5'], 
            jogo['dezena_6'], jogo['dezena_7'], jogo['dezena_8'], jogo['dezena_9'], jogo['dezena_10'], 
            jogo['dezena_11'], jogo['dezena_12'], jogo['dezena_13'], jogo['dezena_14'], jogo['dezena_15'] 
        ]
        
        dezenas_test = aposta
        
        # Encontrando a interseção
        comuns = set(dezenas_real) & set(dezenas_test)

        # Contando os números em comum
        quantidade = len(comuns)

        # print(f"Números em comum: {comuns}")
        # print(f"Quantidade: {quantidade}")
        
        return quantidade
    
    def saveResultado(self, populacao, nome, geracao, loteria='lotofacil'):                 
        
        for individuo in populacao:        
            
            pares = 0    
            for gene in individuo['cromossomo']:
                if gene % 2 == 0:
                    pares += 1   
            
            dezena_1, dezena_2, dezena_3, dezena_4, dezena_5, dezena_6, dezena_7, dezena_8, dezena_9, dezena_10, dezena_11, dezena_12, dezena_13, dezena_14, dezena_15 = individuo['cromossomo']
            
            insert = f"""
                INSERT INTO resultado (
                nome, loteria, geracao, fitness,
                dezena_1, dezena_2, dezena_3, dezena_4, dezena_5, 
                dezena_6, dezena_7, dezena_8, dezena_9, dezena_10, 
                dezena_11, dezena_12, dezena_13, dezena_14, dezena_15, 
                quinze_acertos, quatorze_acertos, treze_acertos, doze_acertos, onze_acertos, 
                pares, impares
                ) VALUES (
                    '{nome}', '{loteria}', {geracao}, {individuo['fitness']},
                    {dezena_1}, {dezena_2}, {dezena_3}, {dezena_4}, {dezena_5},
                    {dezena_6}, {dezena_7}, {dezena_8}, {dezena_9}, {dezena_10},
                    {dezena_11}, {dezena_12}, {dezena_13}, {dezena_14}, {dezena_15},
                    {individuo['quinze_acertos']}, {individuo['quatorze_acertos']}, {individuo['treze_acertos']}, {individuo['doze_acertos']}, {individuo['onze_acertos']}, 
                    {pares}, {(15-pares)}
                );
            """
            
            self.pdo.execute(insert, False)
            
        
        self.pdo.commit()
            
    def checkAcertoEmApostas(self, apostas, concurso):
        
        jogo = self.pdo.select(f'select * from dataframe where concurso = {concurso}', True)                
        
        for aposta in apostas:
            acertos = self.getNumeroAcertos(jogo, aposta)
            print(f'Na aposta: {aposta} \t houve {acertos} acertos')
            
        
        
        