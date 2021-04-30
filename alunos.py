from bd import Banco
import uuid


class AlunosDb(Banco):

    _id: str
    nome: str
    nascimento: str
    matricula: int

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f' nome: {self.nome} \n nascimento: {self.nascimento} \n matricula: {self.matricula}\n'

    def cria_aluno(self, dados_aluno: dict):
        try:
            self.nome = dados_aluno['nome']
            self.nascimento = dados_aluno['idade']
            self.matricula = self.gera_matricula()
            return True
        except:
            return False

    def gera_matricula(self) -> str:
        return str(uuid.uuid4().int)

    def responder_prova(self, respostas: dict) -> bool:
        try:
            self.respostas.insert_one(respostas)
            return True
        except Exception as erro:
            print(str(erro), str(erro.args))
        return False

    def valida_matricula(self) -> bool:
        aluno = self.alunos.find({'matricula': self.matricula})
        try:
            if aluno[0] is not None:
                return True

        except Exception as erro:
            print(str(erro), str(erro.args))
        return False

    def cadastra_aluno(self) -> bool:
        try:
            self.alunos.insert_one({'nome': self.nome,
                                    'nascimento': self.nascimento,
                                    'matricula': self.matricula})
            return True
        except Exception as erro:
            print(str(erro), str(erro.args))

        return False

    def buscar_alunos(self):
        return self.alunos.find({})


# alu = AlunosDb(dict(nome="Orlando", nascimento="1996-01-15"))
# print(alu)
