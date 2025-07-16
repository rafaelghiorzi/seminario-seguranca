# Blockchain Privado com Validação de Transações via Assinatura

### Segurança Computacional - 2025.1 - Turma 02 - Universidade de Brasília

### Integrantes:

#### Lucas Gabriel de Oliveira Lima (https://github.com/lucasdbr05)

#### Pedro Lucas Pereira Neris (https://github.com/pedro-neris)

#### Rafael Dias Ghiorzi (https://github.com/rafaelghiorzi)

Este projeto implementa um **sistema de blockchain privado** com foco em criação e validação de transações através de assinaturas digitais RSA e mecanismo de consenso distribuído para autorizar a entrada de blocos na cadeia. Este trabalho foi desenvolvido para o seminário da disciplina de Segurança Computacional da Universidade de Brasília no semestre 2025.1.

## Sobre o Projeto

Este projeto implementa uma blockchain simplificada, com as seguintes funcionalidades principais:

- **Sistema de usuários** com geração automática de chaves pública e privadas utilizando o algoritmo RSA, feito com a biblioteca *criptography* do Python (chave com 2048 bits)
- **Transações assinadas digitalmente** usando RSA-PSS com SHA-256, também utilizando a biblioteca *criptography*
- **Mecanismo de consenso** para aprovar ou recusar a entrada de um bloco na blockchain, baseado em aprovação da maioria simples dos usuários
- **Interface web interativa** construída com Streamlit
- **Visualizações com grafos** da rede de usuários e estrutura da blockchain
- **Sistema de saldos** onde cada usuário pode receber e enviar pontos de/para outros usuários

## Estrutura do projeto

O projeto é organizado da seguinte forma:

- **`blockchain.py`**: Classe principal que gerencia a cadeia, consenso e usuários
- **`bloco.py`**: Implementação de blocos com hash SHA-256 e assinatura RSA
- **`transacao.py`**: Sistema de transações com assinatura digital RSA-PSS
- **`usuario.py`**: Gerenciamento de usuários, chaves criptográficas e mineração
- **`app.py`**: Interface completa com Streamlit, visualizações e simulações

## Funcionalidades Implementadas

- Visualização da blockchain em tempo real, sendo atualizada sempre que uma nova ação é efetuada
- Geração de usuários com chaves pública e privada e saldo inicial aleatório
- Estatísticas dos usuários e seus saldos
- Registro automático de transações/blocos inseridos na blockchain
- Criação/visualização das transações feitas entre usuários, utilizando a estrutura de grafo
- Assinatura das transações utilizando a chave privada do usuário
- Verificação criptográfica das assinaturas
- Usuário cria transação e minera o bloco
- Aprovação da maioria dos usuários da rede para a inserção, sendo verificados hash, assinatura e saldos para permitir com que uma transação seja feita
- Visualização da Blockchain seguindo uma estrutura linear
- Informações completas de cada bloco inserido
- Detecção de blocos corrompidos ou alterados e validação de hashes sequenciais dos blocos

## Como executar o projeto

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Instale as dependências

```bash
pip install streamlit pandas plotly networkx faker cryptography
```

### 2. Execute a aplicação

```bash
streamlit run app.py
```
A aplicação será executada em: **http://localhost:8501**
