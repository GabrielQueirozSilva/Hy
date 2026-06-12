"""
Módulo para armazenamento de dados em MongoDB.
==============================================

Routine_List
------------
MongoStorage
    Classe para gerenciar a conexão e operações de armazenamento em um banco de dados MongoDB.
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv() 

class MongoStorage:
    """Classe para gerenciar a conexão e operações de armazenamento em um banco de dados MongoDB.
    
    Attributes
    ---------
    client: MongoClient
        O cliente do mongodb para a conexão com o banco de dados.
    col: Collection
        A coleção do mongodb onde os documentos serão armazenados.
    
    Methods
    -------
    save
        Função para salvar um documento no mongodb. 
    """
    def __init__(self, uri=None, db_name=None, co=None):
        """Função para inicializar a conexão com o mongodb.
        
        Parameters
        ----------
        uri: str, optional
            A URI de conexão com o mongodb, caso não seja fornecida, será utilizada a variável de ambiente MONGO_URI.
        db_name: str, optional
            O nome do banco de dados, caso não seja fornecido, será utilizada a variável de ambiente MONGO_DB.
        co: str, optional
            O nome da coleção, caso não seja fornecido, será utilizada a variável de ambiente MONGO_COLLECTION_NAME.
        """
        uri = uri or os.getenv("MONGO_URI")
        db_name = db_name or os.getenv("MONGO_DB")
        co = co or os.getenv("MONGO_COLLECTION_NAME")
        self.client = MongoClient(uri)
        self.col = self.client[db_name][co]

    def save(self, document: dict):
        """Função para salvar um documento no mongodb.
        
        Parameters
        ----------
        document: dict
            O documento a ser salvo no mongodb.
        """
        self.col.insert_one(document)
