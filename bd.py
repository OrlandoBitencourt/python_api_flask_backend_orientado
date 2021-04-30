import pymongo
from bson import ObjectId
import json


class Banco():

    def __init__(self):
        self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.conn['escola_alf']
        self.escola = self.db['escola']
        self.alunos = self.db['alunos']
        self.provas = self.db['provas']
        self.respostas = self.db['respostas']

    def valida_chave_escola(self, chave: str) -> bool:
        escola = self.db.escola.find({'_id': ObjectId(chave)})
        try:
            if escola[0] is not None:
                return True
        except:
            return False




