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
        return gera_response(201, "cadastro-aluno", novo_aluno.matricula, "Criado com sucesso.")
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
        for pr in lista_provas:
            provas_disponiveis.append({'id': str(pr['_id']), "nome": pr['nome']})

        return gera_response(200, "provas", provas_disponiveis, "ok")

    return gera_response(400, "provas", {}, "matricula inválida")


@app.route("/prova/<matricula>/<id>", methods=['GET'])
def prova(matricula, id):
    aluno = AlunosDb()
    aluno.matricula = matricula
    pro = ProvasDb()

    if aluno.valida_matricula():
        try:
            lista_provas = pro.buscar_prova(id)
            dict_prova = pro.gera_dados_prova(lista_provas)

            return gera_response(200, "prova", dict_prova, "ok")
        except:
            return gera_response(400, "prova", {}, "Erro localizar prova")

    return gera_response(400, "prova", {}, "Erro localizar matricula")


@app.route("/prova/<matricula>/<id>", methods=['POST'])
def responder_prova(matricula, id):
    aluno = AlunosDb()
    aluno.matricula = matricula
    pro = ProvasDb()

    if aluno.valida_matricula() and pro.valida_prova(id):
        raw_request = request.data.decode("utf-8")
        dict_values = json.loads(raw_request)
        validador, dados_corrigidos = pro.corrigir_prova(id, dict_values)
        dados_corrigidos['matricula'] = matricula

        if validador:
            aluno.responder_prova(dados_corrigidos)
            mensagem = f"Respondida com sucesso, nota: {str(dados_corrigidos['nota'])}"
            return gera_response(201, "prova", id, mensagem)
        return gera_response(400, "prova", {}, "Erro responder prova, dados invalidos")
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
        prova = ProvasDb()

        raw_request = request.data.decode("utf-8")
        dict_values = json.loads(raw_request)

        if not prova.validar_peso_questoes(dict_values):
            return gera_response(400, "cadastro-provas", {}, "peso incorreto")

        nova_prova = dict(nome=dict_values["nome"],
                          questoes=dict_values["questoes"])

        prova.cadastrar_prova(nova_prova)

        return gera_response(200, "cadastro-provas", dict_values, "ok")

    return gera_response(400, "cadastro-provas", {}, "chave escola inválida")


def gera_response(status, nome_conteudo, conteudo, mensagem=None):
    body = {nome_conteudo: conteudo}
    if mensagem:
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
