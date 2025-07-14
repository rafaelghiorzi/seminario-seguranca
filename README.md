# Blockchain Privado com Validação de Transações via Assinatura
### Segurança Computacional - 2025.1 - Turma 02 - Universidade de Brasília
### Integrantes:
#### Lucas Gabriel de Oliveira Lima (https://github.com/lucasdbr05)
#### Pedro Lucas Pereira Neris (https://github.com/pedro-neris)
#### Rafael Dias Ghiorzi (https://github.com/rafaelghiorzi)

Este projeto implementa um **sistema de blockchain privado** com foco em criação e validação de transações através de assinaturas digitais e com um fluxo de blocos, com mecanismo de consenso para autorizar ou não a entrada de um bloco na cadeia. Este trabalho foi desenvolvido para o seminário da disciplina de Segurança Computacional da Universidade de Brasília no semestre 2025.1. 

## 📋 Sobre o Projeto

Este projeto implementa uma blockchain simplificada com foco educacional, incluindo:

- **Sistema de usuários** com geração de chaves públicas/privadas RSA
- **Transações assinadas digitalmente** para garantir autenticidade
- **Mineração de blocos** com validação criptográfica
- **Mecanismo de consenso** distribuído entre usuários
- **Interface web interativa** construída com Streamlit
- **Visualizações gráficas** da rede e blockchain

## 🏗️ Arquitetura

O projeto é composto pelos seguintes módulos principais:

### Core da Blockchain
- **`blockchain.py`**: Classe principal que gerencia a cadeia de blocos
- **`bloco.py`**: Implementação individual de blocos com hash e assinatura
- **`transacao.py`**: Sistema de transações com assinatura digital RSA
- **`usuario.py`**: Gerenciamento de usuários e chaves criptográficas

### Interface
- **`main.py`**: Interface web com Streamlit e visualizações interativas

## 🔧 Funcionalidades

### 🏠 Dashboard
- Visão geral da blockchain (número de blocos, usuários, transações)
- Estatísticas em tempo real
- Status da integridade da cadeia

### 👥 Gerenciamento de Usuários
- Criação de novos usuários com geração automática de chaves RSA
- Visualização de usuários registrados
- Sistema de amizades/conexões entre usuários

### 💰 Sistema de Transações
- Criação de transações entre usuários
- Assinatura digital automática
- Validação criptográfica

### ⛏️ Mineração
- Mineração de blocos com validação completa
- Mecanismo de consenso distribuído
- Verificação de integridade da cadeia

### 📊 Visualizações
- **Grafo da Comunidade**: Rede de conexões entre usuários
- **Visualização da Blockchain**: Estrutura visual da cadeia de blocos
- **Gráficos interativos** com Plotly

## 🚀 Setup e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Execute a aplicação
```bash
streamlit run main.py
```

### 4. Acesse a aplicação
A aplicação será executada em: **http://localhost:8501**


## 🎯 Conceitos Demonstrados

### Criptografia
- **Chaves RSA**: Geração de pares de chaves pública/privada
- **Assinatura Digital**: Autenticação de transações e blocos
- **Hash SHA-256**: Integridade e ligação entre blocos

### Blockchain
- **Cadeia de Blocos**: Estrutura sequencial imutável
- **Bloco Gênesis**: Primeiro bloco da cadeia
- **Validação**: Verificação criptográfica de blocos e transações

### Consenso Distribuído
- **Validação por Pares**: Múltiplos usuários validam transações
- **Integridade da Cadeia**: Verificação completa da blockchain
- **Prevenção de Fraudes**: Sistema resistente a alterações maliciosas

Em uma blockchain real, as transações realizadas ne rede são
compartilhadas e passam para uma _mempool_ de transações não
confirmadas. Mineradores juntam essas transações em um bloco
candidato e realizam um proof of work (um quebra-cabeça) que
demonstra o esforço e compartilham esse bloco para a rede, e
os usuários validam as informações contidas nesse bloco. Se
um consenso é atingido, o bloco é adicionado à blockchain e o
minerador ganha uma taxa de cada transação como recompensa por
ajudar na organização da blockchain.  
No nosso caso, não realizamos proof of work e mempool, todas as
transações são assinadas e adicionada em um bloco contendo uma
única transação, e o bloco é minerado, sem proof of work, pelo
próprio criador da transação única.

## 🔍 Como Usar

1. **Inicie a aplicação** executando `streamlit run main.py`
2. **Crie usuários** na seção "Gerenciar Usuários"
3. **Estabeleça conexões** entre usuários para formar uma rede
4. **Crie transações** entre usuários conectados
5. **Mineralize blocos** para adicionar transações à blockchain
6. **Visualize** a rede e a blockchain nas abas correspondentes
7. **Verifique a integridade** usando o botão na sidebar
