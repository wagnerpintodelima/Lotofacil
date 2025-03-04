from flask import Flask, jsonify
import random
from datetime import datetime
import json
import hashlib
import string

from banco import SGBD
from Geral import metodos
from IA import AlgoritmoGenetico


SAVE_DATA = False

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Dockerized Flask!"

@app.route('/main', methods=['GET'])
def main():
    pdo = SGBD()
    fn = metodos()
    ag = AlgoritmoGenetico()    
    
    # ag.algoritmo_genetico(geracoes=4, tamanho_populacao=10, jogos_treinamento=10, save=SAVE_DATA)
    
    # fn.checkAcertoEmApostas([
    #     [1,2,3,9,10,11,19,13,14,15,18,20,22,24,25],
    #     [1,2,3,4,6,9,12,13,14,15,19,20,22,24,25]
    # ], 3333)
    
            
if __name__ == "__main__":        
    try:
        main()
        app.run(host='127.0.0.1', port=5000)
    finally:
        print('Finalizado')







