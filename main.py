import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import json
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Dict, Any

from bloco import Bloco
from usuario import Usuario
from transacao import Transacao
from blockchain import Blockchain

# Configuração da página
st.set_page_config(
    page_title="Blockchain Educacional",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def inicializar_sessao():
    """Inicializa o estado da sessão com blockchain e usuários padrão"""
    if 'blockchain' not in st.session_state:
        st.session_state.blockchain = Blockchain()
        
        # Criar usuários demonstrativos
        nomes = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        st.session_state.usuarios = []
        
        for nome in nomes:
            usuario = Usuario(nome, st.session_state.blockchain)
            st.session_state.usuarios.append(usuario)
        
        # Definir usuário padrão
        st.session_state.usuario_atual = st.session_state.usuarios[0]
        
        # Log de ações para demonstrar o consenso
        st.session_state.log_consenso = []

def exibir_grafo_comunidade():
    """Visualiza o grafo de relacionamentos da comunidade"""
    st.subheader("🌐 Grafo da Comunidade")
    
    blockchain = st.session_state.blockchain
    
    if not blockchain.comunidade:
        st.info("Nenhuma transação ainda foi criada. O grafo está vazio.")
        return
    
    # Criar grafo usando NetworkX
    G = nx.Graph()
    
    # Adicionar nós (usuários)
    for usuario in st.session_state.usuarios:
        G.add_node(str(usuario.id), label=usuario.nome, color='lightblue')
    
    # Adicionar arestas (transações)
    for remetente_id, destinatarios in blockchain.comunidade.items():
        for destinatario_id in destinatarios:
            if remetente_id != UUID(int=0):  # Ignorar bloco gênesis
                G.add_edge(str(remetente_id), str(destinatario_id))
    
    if len(G.edges()) == 0:
        st.info("Nenhuma conexão entre usuários ainda.")
        return
    
    # Calcular posições dos nós
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Criar traces para Plotly
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Encontrar nome do usuário
        nome = "Desconhecido"
        for usuario in st.session_state.usuarios:
            if str(usuario.id) == node:
                nome = usuario.nome
                break
        
        node_text.append(nome)
        node_info.append(f"Usuário: {nome}<br>ID: {node[:8]}...")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        hovertext=node_info,
        hoverinfo='text',
        marker=dict(
            size=50,
            color='lightblue',
            line=dict(width=2, color='darkblue')
        )
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="Relacionamentos entre Usuários",
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Conexões baseadas em transações realizadas",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color="gray", size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def exibir_blockchain():
    """Visualiza a cadeia de blocos"""
    st.subheader("⛓️ Cadeia de Blocos")
    
    blockchain = st.session_state.blockchain
    
    if len(blockchain.cadeia) <= 1:
        st.info("Apenas o bloco gênesis existe na cadeia.")
        return
    
    # Criar DataFrame para tabela
    dados_blocos = []
    for i, bloco in enumerate(blockchain.cadeia):
        # Encontrar nomes dos usuários
        nome_minerador = "Sistema"
        nome_remetente = "Sistema"
        nome_destinatario = "Sistema"
        
        if bloco.minerador != UUID(int=0):
            for usuario in st.session_state.usuarios:
                if usuario.id == bloco.minerador:
                    nome_minerador = usuario.nome
                    break
        
        if bloco.transacao.remetente != UUID(int=0):
            for usuario in st.session_state.usuarios:
                if usuario.id == bloco.transacao.remetente:
                    nome_remetente = usuario.nome
                    break
        
        if bloco.transacao.destinatario != UUID(int=0):
            for usuario in st.session_state.usuarios:
                if usuario.id == bloco.transacao.destinatario:
                    nome_destinatario = usuario.nome
                    break
        
        dados_blocos.append({
            "Índice": i,
            "ID do Bloco": str(bloco.id)[:8] + "...",
            "Minerador": nome_minerador,
            "Transação": f"{nome_remetente} → {nome_destinatario}",
            "Conteúdo": bloco.transacao.conteudo[:30] + "..." if len(bloco.transacao.conteudo) > 30 else bloco.transacao.conteudo,
            "Timestamp": bloco.timestamp.strftime("%H:%M:%S"),
            "Hash": bloco.hash.hex()[:16] + "..." if bloco.hash else "N/A"
        })
    
    df = pd.DataFrame(dados_blocos)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Visualização gráfica da cadeia
    st.subheader("📊 Visualização da Cadeia")
    
    fig = go.Figure()
    
    x_positions = list(range(len(blockchain.cadeia)))
    y_positions = [0] * len(blockchain.cadeia)
    
    # Adicionar blocos
    for i, bloco in enumerate(blockchain.cadeia):
        cor = "red" if i == 0 else "lightblue"
        nome = "Gênesis" if i == 0 else f"Bloco {i}"
        
        fig.add_trace(go.Scatter(
            x=[i], y=[0],
            mode='markers+text',
            text=[nome],
            textposition="top center",
            marker=dict(size=60, color=cor, line=dict(width=2, color='darkblue')),
            hovertext=f"ID: {str(bloco.id)[:8]}...<br>Hash: {bloco.hash.hex()[:16] if bloco.hash else 'N/A'}...",
            hoverinfo='text',
            showlegend=False
        ))
    
    # Adicionar conexões
    for i in range(len(blockchain.cadeia) - 1):
        fig.add_trace(go.Scatter(
            x=[i, i+1], y=[0, 0],
            mode='lines',
            line=dict(width=3, color='gray'),
            showlegend=False,
            hoverinfo='none'
        ))
    
    fig.update_layout(
        title="Estrutura da Blockchain",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 0.5]),
        height=200,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_transacao():
    """Interface para criar uma nova transação"""
    st.subheader("💰 Criar Transação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Seletor de destinatário
        nomes_usuarios = [f"{u.nome} ({str(u.id)[:8]}...)" for u in st.session_state.usuarios if u.id != st.session_state.usuario_atual.id]
        
        if not nomes_usuarios:
            st.warning("Nenhum outro usuário disponível para transação.")
            return
        
        destinatario_selecionado = st.selectbox(
            "Destinatário:",
            nomes_usuarios
        )
        
        # Extrair ID do destinatário
        indice_destinatario = nomes_usuarios.index(destinatario_selecionado)
        usuarios_disponiveis = [u for u in st.session_state.usuarios if u.id != st.session_state.usuario_atual.id]
        destinatario = usuarios_disponiveis[indice_destinatario]
    
    with col2:
        conteudo = st.text_area(
            "Conteúdo da transação:",
            placeholder="Digite o conteúdo da transação...",
            height=100
        )
    
    if st.button("🚀 Criar Transação", type="primary"):
        if conteudo.strip():
            try:
                transacao = st.session_state.usuario_atual.criar_transacao(
                    destinatario.id,
                    conteudo.strip()
                )
                
                st.markdown(f"""
                <div class="success-box">
                    ✅ <b>Transação criada com sucesso!</b><br>
                    <b>De:</b> {st.session_state.usuario_atual.nome}<br>
                    <b>Para:</b> {destinatario.nome}<br>
                    <b>Conteúdo:</b> {conteudo}<br>
                    <b>ID:</b> {str(transacao.id)[:8]}...
                </div>
                """, unsafe_allow_html=True)
                
                # Armazenar transação para mineração
                if 'transacoes_pendentes' not in st.session_state:
                    st.session_state.transacoes_pendentes = []
                st.session_state.transacoes_pendentes.append(transacao)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    ❌ <b>Erro ao criar transação:</b> {str(e)}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Por favor, insira o conteúdo da transação.")

def minerar_bloco():
    """Interface para minerar um novo bloco"""
    st.subheader("⛏️ Minerar Bloco")
    
    if 'transacoes_pendentes' not in st.session_state or not st.session_state.transacoes_pendentes:
        st.info("Nenhuma transação pendente para mineração.")
        return
    
    # Mostrar transações pendentes
    st.write("**Transações Pendentes:**")
    for i, transacao in enumerate(st.session_state.transacoes_pendentes):
        # Encontrar nomes dos usuários
        nome_remetente = "Desconhecido"
        nome_destinatario = "Desconhecido"
        
        for usuario in st.session_state.usuarios:
            if usuario.id == transacao.remetente:
                nome_remetente = usuario.nome
            if usuario.id == transacao.destinatario:
                nome_destinatario = usuario.nome
        
        st.write(f"{i+1}. {nome_remetente} → {nome_destinatario}: {transacao.conteudo}")
    
    transacao_selecionada = st.selectbox(
        "Selecione a transação para minerar:",
        range(len(st.session_state.transacoes_pendentes)),
        format_func=lambda i: f"Transação {i+1}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⛏️ Minerar Bloco", type="primary"):
            transacao = st.session_state.transacoes_pendentes[transacao_selecionada]
            
            # Limpar log de consenso
            st.session_state.log_consenso = []
            
            # Minerar o bloco
            bloco_minerado = st.session_state.usuario_atual.minerar_bloco(transacao)
            
            if bloco_minerado:
                st.markdown(f"""
                <div class="success-box">
                    ✅ <b>Bloco minerado e adicionado com sucesso!</b><br>
                    <b>Minerador:</b> {st.session_state.usuario_atual.nome}<br>
                    <b>ID do Bloco:</b> {str(bloco_minerado.id)[:8]}...<br>
                    <b>Hash:</b> {bloco_minerado.hash.hex()[:16]}...
                </div>
                """, unsafe_allow_html=True)
                
                # Remover transação da lista de pendentes
                st.session_state.transacoes_pendentes.pop(transacao_selecionada)
                
                # Rerun para atualizar a interface
                st.rerun()
            else:
                st.markdown(f"""
                <div class="error-box">
                    ❌ <b>Bloco rejeitado pela rede!</b><br>
                    O consenso não foi alcançado.
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🗑️ Remover Transação"):
            st.session_state.transacoes_pendentes.pop(transacao_selecionada)
            st.success("Transação removida da lista de pendentes.")
            st.rerun()

def exibir_log_consenso():
    """Exibe o log do processo de consenso"""
    st.subheader("🤝 Log do Consenso")
    
    if not st.session_state.log_consenso:
        st.info("Nenhum processo de consenso registrado ainda.")
        return
    
    for entrada in st.session_state.log_consenso:
        timestamp = entrada.get('timestamp', 'N/A')
        nivel = entrada.get('nivel', 'INFO')
        mensagem = entrada.get('mensagem', '')
        
        if nivel == 'SUCCESS':
            st.success(f"[{timestamp}] {mensagem}")
        elif nivel == 'ERROR':
            st.error(f"[{timestamp}] {mensagem}")
        elif nivel == 'WARNING':
            st.warning(f"[{timestamp}] {mensagem}")
        else:
            st.info(f"[{timestamp}] {mensagem}")

def gerenciar_usuarios():
    """Interface para gerenciamento de usuários"""
    st.subheader("👥 Gerenciamento de Usuários")
    
    # Usuário atual
    st.write("**Usuário Atual:**")
    nomes_usuarios = [f"{u.nome} ({str(u.id)[:8]}...)" for u in st.session_state.usuarios]
    indice_atual = st.session_state.usuarios.index(st.session_state.usuario_atual)
    
    novo_indice = st.selectbox(
        "Selecionar usuário ativo:",
        range(len(st.session_state.usuarios)),
        index=indice_atual,
        format_func=lambda i: nomes_usuarios[i]
    )
    
    if novo_indice != indice_atual:
        st.session_state.usuario_atual = st.session_state.usuarios[novo_indice]
        st.success(f"Usuário alterado para: {st.session_state.usuario_atual.nome}")
        st.rerun()
    
    # Lista de todos os usuários
    st.write("**Todos os Usuários:**")
    dados_usuarios = []
    for usuario in st.session_state.usuarios:
        ativo = "✅" if usuario == st.session_state.usuario_atual else ""
        dados_usuarios.append({
            "Ativo": ativo,
            "Nome": usuario.nome,
            "ID": str(usuario.id)[:8] + "...",
            "Chave Pública": str(usuario.chave_publica.key_size) + " bits"
        })
    
    df_usuarios = pd.DataFrame(dados_usuarios)
    st.dataframe(df_usuarios, hide_index=True, use_container_width=True)
    
    # Criar novo usuário
    st.write("**Criar Novo Usuário:**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        novo_nome = st.text_input("Nome do novo usuário:")
    
    with col2:
        if st.button("➕ Criar"):
            if novo_nome.strip():
                try:
                    novo_usuario = Usuario(novo_nome.strip(), st.session_state.blockchain)
                    st.session_state.usuarios.append(novo_usuario)
                    st.success(f"Usuário '{novo_nome}' criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {str(e)}")
            else:
                st.warning("Por favor, insira um nome válido.")

def main():
    """Função principal da aplicação"""
    inicializar_sessao()
    
    # Cabeçalho principal
    st.markdown('<h1 class="main-header">⛓️ Blockchain Educacional</h1>', unsafe_allow_html=True)
    
    # Sidebar para navegação
    st.sidebar.title("🧭 Navegação")
    
    paginas = {
        "🏠 Dashboard": "dashboard",
        "🌐 Grafo da Comunidade": "grafo",
        "⛓️ Visualizar Blockchain": "blockchain",
        "💰 Criar Transação": "transacao",
        "⛏️ Minerar Bloco": "minerar",
        "🤝 Log do Consenso": "consenso",
        "👥 Gerenciar Usuários": "usuarios"
    }
    
    pagina_selecionada = st.sidebar.radio(
        "Selecione uma página:",
        list(paginas.keys())
    )
    
    # Informações do usuário atual na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**👤 Usuário Ativo:**")
    st.sidebar.info(f"**{st.session_state.usuario_atual.nome}**\nID: {str(st.session_state.usuario_atual.id)[:8]}...")
    
    # Estatísticas da blockchain na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Estatísticas:**")
    st.sidebar.metric("Blocos na Cadeia", len(st.session_state.blockchain.cadeia))
    st.sidebar.metric("Usuários Registrados", len(st.session_state.usuarios))
    
    transacoes_pendentes = len(st.session_state.get('transacoes_pendentes', []))
    st.sidebar.metric("Transações Pendentes", transacoes_pendentes)
    
    # Conteúdo principal baseado na página selecionada
    pagina_id = paginas[pagina_selecionada]
    
    if pagina_id == "dashboard":
        st.write("### 🏠 Dashboard Principal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total de Blocos",
                len(st.session_state.blockchain.cadeia),
                delta=len(st.session_state.blockchain.cadeia) - 1
            )
            st.metric(
                "Usuários Ativos",
                len(st.session_state.usuarios)
            )
        
        with col2:
            st.metric(
                "Transações Pendentes",
                transacoes_pendentes
            )
            st.metric(
                "Conexões na Rede",
                sum(len(conexoes) for conexoes in st.session_state.blockchain.comunidade.values()) // 2
            )
        
        # Resumo recente
        st.subheader("📈 Atividade Recente")
        if len(st.session_state.blockchain.cadeia) > 1:
            ultimo_bloco = st.session_state.blockchain.ultimo_bloco()
            st.info(f"Último bloco minerado: {ultimo_bloco.timestamp.strftime('%H:%M:%S')} por {ultimo_bloco.minerador}")
        else:
            st.info("Apenas o bloco gênesis existe na cadeia.")
    
    elif pagina_id == "grafo":
        exibir_grafo_comunidade()
    
    elif pagina_id == "blockchain":
        exibir_blockchain()
    
    elif pagina_id == "transacao":
        criar_transacao()
    
    elif pagina_id == "minerar":
        minerar_bloco()
    
    elif pagina_id == "consenso":
        exibir_log_consenso()
    
    elif pagina_id == "usuarios":
        gerenciar_usuarios()
    
    # Botão para verificar integridade da blockchain
    st.sidebar.markdown("---")
    if st.sidebar.button("🔍 Verificar Integridade"):
        try:
            st.session_state.blockchain.verificar()
            st.sidebar.success("✅ Blockchain íntegra!")
        except Exception as e:
            st.sidebar.error(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()