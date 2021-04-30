from flask import Flask, request, Response
import json
from bd import Banco
from alunos import AlunosDb
from provas import ProvasDb

app = Flask(__name__)
banco = Banco()


@app.route("/")
def index():
    return "HELLO WORLD!"


@app.route("/cadastro-aluno", methods=['POST'])
def cadastrar_aluno():
    raw_request = request.data.decode("utf-8")
    dict_values = json.loads(raw_request)

    novo_aluno = AlunosDb()

    if novo_aluno.cria_aluno(dict_values) and novo_aluno.cadastra_aluno():
        return gera_response(201, "matricula", novo_aluno.matricula, "Criado com sucesso.")
    else:
        return gera_response(400, "cadastro-aluno", {}, "Erro ao cadastrar")


@app.route("/provas/<matricula>", methods=['GET'])
def provas(matricula):
    aluno = AlunosDb()
    aluno.matricula = matricula

    if aluno.valida_matricula():
        prova = ProvasDb()
        lista_provas = prova.buscar_todas_provas()

        provas_disponiveis = []
        for prova in lista_provas:
            provas_disponiveis.append({'id': str(prova['_id']), "nome": prova['nome']})

        return gera_response(200, "provas", provas_disponiveis, "ok")

    return gera_response(400, "provas", {}, "matricula inválida")


@app.route("/prova/<matricula>/<id>", methods=['GET'])
def prova(matricula, id):
    aluno = AlunosDb()
    aluno.matricula = matricula

    if aluno.valida_matricula():
        provas_disponiveis = []

        try:
            pro = ProvasDb()
            lista_provas = pro.buscar_prova(id)

            for prova in lista_provas:

                for item in prova['questoes']:
                    del prova['questoes'][item]['correta']

                provas_disponiveis.append({'id': str(prova['_id']),
                                           'nome': prova['nome'],
                                           'questoes': prova['questoes']})

            return gera_response(200, "prova", provas_disponiveis, "ok")
        except:
            return gera_response(400, "prova", {}, "Erro localizar prova")

    return gera_response(400, "prova", {}, "Erro localizar matricula")


@app.route("/prova/<matricula>/<id>", methods=['POST'])
def responder_prova(matricula, id):
    matriculas_lst = []
    provas_lst = []
    resposta = []

    aluno = AlunosDb()
    aluno.matricula = matricula

    if aluno.valida_matricula():
        pro = ProvasDb()

        if pro.valida_prova(id):
            raw_request = request.data.decode("utf-8")
            dict_values = json.loads(raw_request)

            lista_prova = pro.buscar_prova(id)
            lista_respostas = pro.buscar_respostas(id)

            for prova in lista_prova:
                nota_aluno = 0

                for resposta_prova in lista_respostas:
                    matriculas_lst.append(str(int(resposta_prova['matricula'])))
                    provas_lst.append(str(resposta_prova['prova']))
                    resposta.append(resposta_prova)

                    if str(dict_values['matricula']) == str(int(resposta_prova['matricula'])) and str(id) == str(resposta_prova['prova']):
                        return gera_response(400, "prova", {}, "Você já respondeu a prova")

                if len(prova['questoes']) == len(dict_values['respostas_aluno']) and len(prova['questoes']) != 0:
                    for questao in range(1, len(prova['questoes'])):
                        if dict_values['respostas_aluno'][f'{questao}'] in prova['questoes'][f'{questao}']['alternativas']:
                            if str(dict_values['respostas_aluno'][f'{questao}']) == str(prova['questoes'][f'{questao}']['correta']):
                                nota_aluno += float(prova['questoes'][f'{questao}']['peso'])

                    respostas_aluno = dict(matricula=dict_values['matricula'],
                                           prova=id,
                                           nota=nota_aluno,
                                           respostas_aluno=dict_values['respostas_aluno'])

                    if aluno.responder_prova(respostas_aluno):
                        return gera_response(201, "prova", prova['nome'], f"Respondida com sucesso, nota: {nota_aluno}")

                else:
                    return gera_response(400, "prova", {}, "Erro responder prova, alternativa nao localizada na questao.")

            return gera_response(400, "prova", {}, "Erro responder prova, numero de questoes respondidas incorreto.")

        return gera_response(400, "prova", {}, "Erro responder prova, id prova incorreto")

    return gera_response(400, "prova", {}, "Erro responder prova, matricula inválida")


@app.route("/alunos/<chave>", methods=['GET'])
def alunos(chave):
    aluno = AlunosDb()

    if banco.valida_chave_escola(chave):
        alunos_disponiveis = []
        lista_alunos = aluno.buscar_alunos()
        for aluno in lista_alunos:
            alunos_disponiveis.append({"id": str(aluno['_id']),
                                       "matricula": aluno['matricula'],
                                       "nome": aluno['nome'],
                                       "nascimento": aluno['nascimento']})

        return gera_response(200, "alunos", alunos_disponiveis, "ok")

    return gera_response(400, "alunos", {}, "chave escola inválida")

@app.route("/cadastro-provas/<chave>", methods=['POST'])
def cadastro_provas(chave: str):
    if banco.valida_chave_escola(chave):

        raw_request = request.data.decode("utf-8")
        dict_values = json.loads(raw_request)
        peso_questoes = 0
        try:
            for questao in dict_values['questoes']:
                peso_questoes += float(dict_values['questoes'][f'{questao}']['peso'])

            if peso_questoes > 10 or peso_questoes < 0:
                return gera_response(400, "cadastro-provas", {}, "peso incorreto")
        except:
            return gera_response(400, "cadastro-provas", {}, "peso incorreto")

        prova = ProvasDb()

        nova_prova = dict(nome=dict_values["nome"],
                          questoes=dict_values["questoes"])

        prova.cadastrar_prova(nova_prova)

        return gera_response(200, "cadastro-provas", dict_values, "ok")

    return gera_response(400, "cadastro-provas", {}, "chave escola inválida")


def gera_response(status, nome_conteudo, conteudo, mensagem=False):
    body = {nome_conteudo: conteudo}
    if mensagem:
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
