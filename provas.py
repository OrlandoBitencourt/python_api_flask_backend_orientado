from bd import Banco
from bson import ObjectId


class ProvasDb(Banco):

    def __init__(self):
        super().__init__()

    def buscar_todas_provas(self):
        return self.provas.find({})

    def buscar_prova(self, id_prova: int):
        return self.provas.find({'_id': ObjectId(id_prova)})

    def buscar_respostas(self, id_prova: int):
        return self.respostas.find({'prova': id_prova})

    def valida_prova(self, id_prova: str) -> bool:
        prova = self.provas.find({'_id': ObjectId(id_prova)})
        try:
            if prova[0] is not None:
                return True
        except Exception as erro:
            print(str(erro), str(erro.args))
        return False

    def cadastrar_prova(self, prova: dict) -> bool:
        try:
            self.provas.insert_one(prova)
            return True
        except Exception as erro:
            print(str(erro), str(erro.args))
        return False