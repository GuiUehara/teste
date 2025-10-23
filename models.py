class Pessoa:
    def __init__(self, nome, cpf, data_nasc, endereco):
        self.nome = nome
        self.cpf = cpf
        self.data_nasc = data_nasc
        self.endereco = endereco

class Cliente(Pessoa):
    def __init__(self, nome, cpf, data_nasc, endereco, telefone, email, cnh, categoria_cnh, validade_cnh, tempo_habilitacao, forma_pagamento):
        super().__init__(nome, cpf, data_nasc, endereco)
        self.telefone = telefone
        self.email = email
        self.cnh = cnh
        self.categoria_cnh = categoria_cnh
        self.validade_cnh = validade_cnh
        self.tempo_habilitacao = tempo_habilitacao
        self.forma_pagamento = forma_pagamento

class Funcionario:
    def __init__(self, nome, cpf, rg, data_nasc, sexo, estado_civil, endereco, email, senha, perfil="atendente"):
        self.nome = nome
        self.cpf = cpf
        self.rg = rg
        self.data_nasc = data_nasc
        self.sexo = sexo
        self.estado_civil = estado_civil
        self.endereco = endereco
        self.email = email
        self.senha = senha
        self.perfil = perfil

class Veiculo:
    def __init__(self, modelo, placa, ano, status="disponível"):
        self.modelo = modelo
        self.placa = placa
        self.ano = ano
        self._status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, novo_status):
        if novo_status in ['disponível', 'alugado']:
            self._status = novo_status

class Locacao:
    def __init__(self, cliente, veiculo, data_inicio, data_fim=None):
        if veiculo.status != "disponível":
            raise Exception("Veículo indisponível")
        self.cliente = cliente
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        veiculo.status = "alugado"

    def encerrar(self, data_fim):
        self.data_fim = data_fim
        self.veiculo.status = "disponível"
