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

    def buscar_gabarito(self, id_prova):
        gabarito = self.provas.find_one({"_id": ObjectId(id_prova)})
        return gabarito['questoes']

    def corrigir_prova(self, id_prova: int, respostas: dict):
        gabarito = self.buscar_gabarito(id_prova)
        nota_final = 0

        if gabarito.keys() != respostas['respostas_aluno'].keys():
            return False, {}

        for numero_questao in range(1, len(gabarito)):
            if gabarito[f'{numero_questao}']["correta"].lower() == respostas['respostas_aluno'][f'{numero_questao}'].lower():
                nota_final += float(gabarito[f'{numero_questao}']["peso"])

        dados_retorno = dict(prova=id_prova,
                             nota=nota_final,
                             respostas_aluno=respostas['respostas_aluno'])

        return True, dados_retorno

    def validar_peso_questoes(self, questoes: dict) -> bool:
        peso_questoes = 0
        for questao in questoes['questoes']:
            peso_questoes += float(questoes['questoes'][f'{questao}']['peso'])

        if peso_questoes > 10 or peso_questoes < 0:
            return False

        return True

    def gera_dados_prova(self, lista_prova: list) -> dict:
        prova_dict = {}
        for prova in lista_prova:
            for item in prova['questoes']:
                del prova['questoes'][item]['correta']

            prova_dict.append({'id': str(prova['_id']),
                                       'nome': prova['nome'],
                                       'questoes': prova['questoes']})
            return prova_dict