use locadora;

INSERT INTO status_veiculo (id_status_veiculo, descricao_status) VALUES
(1, 'Disponível'), -- Veículo pronto para locação.
(2, 'Alugado'), -- Veículo em posse de um cliente.
(3, 'Em Manutenção'); -- Veículo na oficina, indisponível para locação.

INSERT INTO marca (id_marca, nome_marca) VALUES
(1, 'Renault'), 
(2, 'Volkswagen'),
(3, 'BYD'), -- Elétricos
(4, 'FIAT'), 
(5, 'BMW');

INSERT INTO combustivel (id_combustivel, tipo_combustivel) VALUES
(1, 'Gasolina'),
(2, 'Álcool'),
(3, 'Diesel'),
(4, 'Flex'),
(5, 'Elétrico');

INSERT INTO cargo (id_cargo, nome_cargo, descricao_permissoes) VALUES
(1, 'Atendente', 'Registrar locações, devoluções e pagamentos.'),
(2, 'Gerente', 'Acesso total ao sistema, gerenciar frota e funcionários.'),
(3, 'Mecânico', 'Registrar manutenções e atualizar status de veículos.');

INSERT INTO categoria_veiculo (id_categoria_veiculo, nome_categoria, valor_diaria) VALUES
(1, 'Compacto', 120.00),
(2, 'Sedan Médio', 180.50),
(3, 'SUV', 250.00),
(4, 'Picape', 300.00),
(5, 'Elétrico', 350.75);

INSERT INTO modelo (id_modelo, nome_modelo, id_marca, id_categoria_veiculo) VALUES
(1, 'kwid', 1, 1),        -- Renault, compacto
(2, 'Virtus', 2, 2),     -- VW, Sedan
(3, 'X3', 5, 3),    -- BMW, SUV
(4, 'Dolphin', 3, 5),       -- byd, elétrico
(5, 'Toro', 4, 4);      -- Fiat, Picape

INSERT INTO usuario (id_usuario, email, senha, perfil) VALUES
(1, 'empresateste74@gmail.com', 1234, 'Gerente');

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'senha';
FLUSH privileges;



INSERT INTO opcional (id_opcional, descricao, valor_diaria, quantidade, id_locacao) VALUES
(1, 'Cadeira de Bebê', 25.00, 1, 2), -- Para Locação 2
(2, 'GPS', 15.00, 1, 3), -- Para Locação 3
(3, 'Cadeira de Bebê', 25.00, 2, 4), -- Para Locação 4
(4, 'Bagageiro de Teto', 40.00, 1, 4); -- Para Locação 4

