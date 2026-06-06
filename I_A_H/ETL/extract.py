"""
ETL - Extract
=============

Parte responsável por extrair os dados do mongodb, retornando-os em um formato adequado para a transformação e o carregamento.

Routine List
------------
extrair_dados
    Função principal para extrair os dados do mongodb.
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class Extrator:
    """Classe responsável por extrair os dados do mongodb.
    
    Attributes
    ---------
    client: MongoClient
        O cliente do mongodb para a conexão com o banco de dados.
    db: Database
        O banco de dados do mongodb para a extração dos dados.
    
    Methods
    -------
    extrair_dados
        Função principal para extrair os dados do mongodb.
    """
    def __init__(self, uri=None, db_name=None):
        """
        Parameters
        ----------
        uri: str, optional
            A URI de conexão com o mongodb, caso não seja fornecida, será utilizada a variável de ambiente MONGO_URI.
        db_name: str, optional
            O nome do banco de dados do mongodb, caso não seja fornecido, será utilizada a variável de ambiente MONGO_DB.
        """
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def extrair_dados(self, collection_name=None):
        """Função principal para extrair os dados do mongodb.
        
        Parameters
        ----------
        collection_name: str, optional
            O nome da collection do mongodb para a extração dos dados, caso não seja fornecido, será utilizada a variável 
            de ambiente MONGO_COLLECTION_NAME.
            
        Returns
        -------
        list
            Uma lista de dicionários contendo os dados extraídos do mongodb, prontos para serem transformados e 
            carregados no postgres.
            
        Notes
        -----
        A estrutura de cada documento é:
        '__id': Objecid('id')
        'scan_timestamp': 'anomesdia_time'
        'raw_text': string
        'sanitized_text': string
        'parsed': {'name': string, 'tier': string, 'seller': string, 'price': int, 'class': string }
        'bbox': list
        'confidence': float
        'etl_erros': None/string (PARSED_INVALID, NAME_INVALID, CLASS_INVALID, TIER_INVALID, PRICE_INVALID)
        'etl_status': string (validated, quarantine, rejected)        
        """
        collection_name = collection_name or os.getenv("MONGO_COLLECTION_NAME")
        collection = self.db[collection_name]
        return list(collection.find({}))
    