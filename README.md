# Blockchain Privado com Validação de Transações via Assinatura

### Segurança Computacional - 2025.1 - Turma 02 - Universidade de Brasília

### Integrantes:

#### Lucas Gabriel de Oliveira Lima (https://github.com/lucasdbr05)

#### Pedro Lucas Pereira Neris (https://github.com/pedro-neris)

#### Rafael Dias Ghiorzi (https://github.com/rafaelghiorzi)

Este projeto implementa um **sistema de blockchain privado** com foco em criação e validação de transações através de assinaturas digitais RSA e mecanismo de consenso distribuído para autorizar a entrada de blocos na cadeia. Este trabalho foi desenvolvido para o seminário da disciplina de Segurança Computacional da Universidade de Brasília no semestre 2025.1.

## 📋 Sobre o Projeto

Este projeto implementa uma blockchain simplificada com foco educacional, demonstrando:

- **Sistema de usuários** com geração automática de chaves RSA (2048 bits)
- **Transações assinadas digitalmente** usando RSA-PSS com SHA-256
- **Mineração de blocos** com validação criptográfica completa
- **Mecanismo de consenso** baseado em aprovação de 1/3 dos usuários
- **Interface web interativa** construída com Streamlit
- **Visualizações gráficas** da rede de usuários e estrutura da blockchain
- **Sistema de saldos** com verificação automática de fundos suficientes

## 🏗️ Arquitetura

O projeto é organizado nos seguintes módulos:

### Core da Blockchain (`src/`)

- **`blockchain.py`**: Classe principal que gerencia a cadeia, consenso e usuários
- **`bloco.py`**: Implementação de blocos com hash SHA-256 e assinatura RSA
- **`transacao.py`**: Sistema de transações com assinatura digital RSA-PSS
- **`usuario.py`**: Gerenciamento de usuários, chaves criptográficas e mineração

### Interface Web

- **`app.py`**: Interface completa com Streamlit, visualizações e simulações

## 🔧 Funcionalidades Implementadas

### 🏠 Dashboard Principal

- Visualização da blockchain em tempo real
- Estatísticas dos usuários e seus saldos
- Status da integridade da cadeia

### 👥 Sistema de Usuários

- Criação automática de 15 usuários com nomes brasileiros (Faker)
- Geração de chaves RSA (2048 bits) para cada usuário
- Saldos iniciais aleatórios entre 10 e 100 pontos
- Registro automático na blockchain

### 💰 Sistema de Transações

- Criação de transações entre usuários com seleção intuitiva
- Assinatura automática com chave privada do remetente
- Validação de saldos antes da execução
- Verificação criptográfica completa das assinaturas

### ⛏️ Mineração e Consenso

- **Mineração simplificada**: Usuário cria transação e minera o bloco
- **Consenso distribuído**: Aprovação de 1/3 dos usuários da rede
- **Validação rigorosa**: Verificação de hash, assinatura e saldos
- **Parada otimizada**: Consenso para assim que 1/3 aprova
- **Atualização automática**: Saldos atualizados após consenso

### 📊 Visualizações Interativas

- **Grafo da Comunidade**: Rede de conexões baseada em transações (NetworkX + Plotly)
- **Visualização da Blockchain**: Estrutura linear dos blocos
- **Detalhes dos Blocos**: Informações completas de cada bloco
- **Logs em Tempo Real**: Acompanhamento do processo de consenso

### 🔍 Verificação de Integridade

- Verificação completa da cadeia de blocos
- Validação de hashes sequenciais
- Detecção de blocos corrompidos ou alterados

## 🚀 Setup e Execução

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

### 3. Acesse a aplicação

A aplicação será executada em: **http://localhost:8501**

## 🎯 Conceitos Criptográficos Demonstrados

### Assinatura Digital RSA

- **Chaves RSA-2048**: Geração de pares de chaves pública/privada
- **RSA-PSS**: Esquema de assinatura probabilística com MGF1
- **SHA-256**: Função de hash para integridade das mensagens
- **Verificação**: Validação criptográfica de transações e blocos

### Estrutura Blockchain

- **Bloco Gênesis**: Primeiro bloco com hash anterior fixo
- **Encadeamento**: Cada bloco referencia o hash do anterior
- **Integridade**: Alterações quebram a cadeia de hashes
- **Timestamps**: Ordenação temporal dos blocos

### Consenso Distribuído

- **Validação por Pares**: Usuários validam blocos de outros
- **Aprovação por Maioria**: Necessário 1/3 dos usuários para aprovar
- **Verificação Múltipla**: Hash, assinatura, saldo e estrutura
- **Tolerância a Falhas**: Sistema resiste a usuários maliciosos

## 🔍 Como Usar a Aplicação

1. **Execute** a aplicação com `streamlit run app.py`
2. **Navegue** entre as três páginas principais:

   - **Grafo da Comunidade**: Visualize conexões entre usuários
   - **Blockchain**: Explore a estrutura da cadeia de blocos
   - **Criar e Minerar Transação**: Simule transações reais

3. **Crie transações**:

   - Selecione remetente e destinatário
   - Defina o valor em pontos
   - Acompanhe o processo de consenso em tempo real

4. **Monitore** os saldos dos usuários na barra lateral
5. **Verifique** a integridade da blockchain quando necessário

## 🔬 Características Técnicas

### Diferenças de uma Blockchain Real

- **Sem Proof of Work**: Não há quebra-cabeça computacional
- **Sem Mempool**: Transações são processadas individualmente
- **Mineração Simplificada**: Criador da transação minera o bloco
- **Consenso Adaptado**: Aprovação de 1/3 em vez de maioria de poder computacional

### Validações Implementadas

- **Verificação de saldo** antes da transação
- **Validação criptográfica** de assinaturas
- **Verificação de integridade** da cadeia
- **Consenso distribuído** para aprovação
- **Detecção de alterações** maliciosas

## 🛠️ Estrutura de Arquivos

```
seminario-seguranca/
├── src/
│   ├── blockchain.py      # Gerenciamento da cadeia e consenso
│   ├── bloco.py          # Implementação de blocos
│   ├── transacao.py      # Sistema de transações
│   └── usuario.py        # Gerenciamento de usuários
├── app.py                # Interface web principal
└── README.md            # Este arquivo
```

## 🎓 Valor Educacional

Este projeto demonstra de forma prática e visual:

- **Fundamentos da criptografia** aplicada em blockchains
- **Mecanismos de consenso** distribuído
- **Validação de transações** através de assinaturas digitais
- **Estrutura de dados** de uma blockchain
- **Verificação de integridade** em sistemas distribuídos

Ideal para estudantes de segurança computacional compreenderem os conceitos fundamentais de blockchains e criptografia aplicada.
