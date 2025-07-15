import time
import faker
import random
import pandas as pd
from uuid import UUID
import networkx as nx
import streamlit as st
from src.bloco import Bloco
from src.usuario import Usuario
import plotly.graph_objects as go
from src.transacao import Transacao
from src.blockchain import Blockchain

st.set_page_config(
    page_title="Blockchain Educacional",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def iniciar_demo():
    """Inicia a demonstração da blockchain com dados de exemplo"""
    if "blockchain" not in st.session_state:
        st.session_state.blockchain = Blockchain()
        
        # Criar usuários demonstrativos
        fake = faker.Faker('pt_BR')
        st.session_state.usuarios = []
        for _ in range(15):
            nome = fake.name()
            usuario = Usuario(nome, st.session_state.blockchain, random.uniform(10, 100))
            st.session_state.usuarios.append(usuario)
        
        st.session_state.transacoes_pendentes = []

def exibir_grafo():
    """Visualiza o grafo de relacionamento da comunidade"""
    st.subheader("Grafo da Comunidade")
    blockchain = st.session_state.blockchain

    if not blockchain.comunidade:
        st.info("Nenhuma transação registrada. O grafo está vazio.")
        return

    G = nx.Graph()
    
    # Adicionar nós (usuários)
    for usuario in st.session_state.usuarios:
        G.add_node(str(usuario.id), label=usuario.nome, color="lightblue")
    
    # Adicionar arestas (transações)
    for remetente, destinatarios in blockchain.comunidade.items():
        for destinatario in destinatarios:
            if remetente != UUID(int=0):  # Ignorar o bloco genesis
                G.add_edge(str(remetente), str(destinatario))

    if len(G.edges()) == 0:
        st.info("Nenhuma conexão entre usuários registradas.")
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
            annotations=[dict(
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
    """Visualiza a cadeia de blocos e informações detalhadas"""
    st.subheader("Blockchain")
    
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
            "Pontos": f"{bloco.transacao.pontos:.2f}" if i > 0 else "N/A",
            "Timestamp": bloco.timestamp.strftime("%H:%M:%S"),
            "Hash": bloco.hash.hex()[:16] + "..." if bloco.hash else "N/A"
        })
    
    df = pd.DataFrame(dados_blocos)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Visualização gráfica da cadeia
    st.subheader("📊 Visualização da Cadeia")
    
    fig = go.Figure()
    
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

    # Seção de informações detalhadas dos blocos
    st.subheader("📋 Informações Detalhadas dos Blocos")
    
    if len(blockchain.cadeia) > 1:
        bloco_selecionado = st.selectbox(
            "Selecione um bloco para ver detalhes:",
            range(len(blockchain.cadeia)),
            format_func=lambda i: f"Bloco {i} - {'Gênesis' if i == 0 else 'Transação'}"
        )
        
    bloco: Bloco = blockchain.cadeia[bloco_selecionado]

    st.write("**Informações do Bloco:**")
    st.write(f"- **Índice:** {bloco_selecionado}")
    st.write(f"- **ID:** {str(bloco.id)}")
    st.write(f"- **Timestamp:** {bloco.timestamp}")
    st.write(f"- **Hash:** {bloco.hash.hex() if bloco.hash else 'N/A'}")
    st.write(f"- **Hash Anterior:** {bloco.hash_anterior.hex() if bloco.hash_anterior else 'N/A'}")

    st.write("**Informações da Transação:**")
    st.write(f"- **ID da Transação:** {str(bloco.transacao.id)}")
    st.write(f"- **Remetente:** {bloco.transacao.remetente}")
    st.write(f"- **Destinatário:** {bloco.transacao.destinatario}")
    st.write(f"- **Pontos:** {bloco.transacao.pontos:.2f}")
    
    # Encontrar nome do minerador
    nome_minerador = "Sistema"
    if bloco.minerador != UUID(int=0):
        for usuario in st.session_state.usuarios:
            if usuario.id == bloco.minerador:
                nome_minerador = usuario.nome
                break
    st.write(f"**Minerador do bloco:** {nome_minerador}")

def criar_e_minerar_transacao():
    """
    Interface para criar e minerar um bloco com uma transação.
    """
    st.subheader("Criar e Minerar Transação")

    # Seleção de remetente e destinatário
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Remetente:**")
        nomes = [f"{u.nome} ({u.pontos:.2f} pontos)" for u in st.session_state.usuarios]
        
        indice = st.selectbox(
            "Selecione o remetente:",
            range(len(st.session_state.usuarios)),
            format_func=lambda i: nomes[i]
        )

        remetente: Usuario = st.session_state.usuarios[indice]

    with col2:
        st.write("**Destinatário:**")
        # Filtrar usuários disponíveis (excluindo o remetente)
        usuarios_disponiveis = [u for u in st.session_state.usuarios if u.id != remetente.id]
        
        if not usuarios_disponiveis:
            st.warning("Nenhum destinatário disponível.")
            return
        
        nomes_destinatarios = [f"{u.nome} ({u.pontos:.2f} pontos)" for u in usuarios_disponiveis]
        
        indice_destinatario = st.selectbox(
            "Selecione o destinatário:",
            range(len(usuarios_disponiveis)),
            format_func=lambda i: nomes_destinatarios[i]
        )

        destinatario: Usuario = usuarios_disponiveis[indice_destinatario]

    # Valor da transação
    st.write("**Valor da Transação:**")
    pontos = st.number_input(
        "Digite o valor em pontos:",
        step=0.01,
        format="%.2f"
    )

    botao_desabilitado = pontos <= 0
    if st.button("Criar e minerar transação", type="primary", disabled=botao_desabilitado):
        if pontos <= 0:
            st.error("O valor da transação deve ser maior que zero.")
            return
        
        try:
            with st.container():
                st.subheader("Processo de Mineração e Consenso")
                
                # Informações da transação
                st.info(f"**Transação:** {remetente.nome} → {destinatario.nome} | **Valor:** {pontos:.2f} pontos")
                
                # Container para logs em tempo real
                log_container = st.empty()
                logs = []
                
                def log_callback(message):
                    logs.append(message)
                    log_text = "\n".join(logs)
                    log_container.text_area("Log do Processo:", value=log_text, height=300, disabled=True)
                
                # Criar e minerar transação
                transacao = remetente.criar_transacao(destinatario.id, pontos)
                bloco = remetente.minerar_bloco(transacao, log_callback)

                if bloco:
                    st.success(f"Transação concluída com sucesso! Bloco ID: {str(bloco.id)[:8]}...")
                    
                    # Mostrar sumário final
                    st.subheader("Sumário Final")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Status", "Sucesso")
                        st.metric("Bloco ID", str(bloco.id)[:8])
                    
                    with col2:
                        st.metric("Novo saldo - Remetente", f"{remetente.pontos:.2f}")
                        st.metric("Novo saldo - Destinatário", f"{destinatario.pontos:.2f}")
                        
                    st.session_state.blockchain.verificar()
                else:
                    st.error("Transação falhou - Bloco rejeitado pela rede")
                    
                    # Mostrar sumário de falha
                    st.subheader("Sumário da Falha")
                    st.warning("A transação não foi aprovada pelo consenso da rede.")
            
            time.sleep(10)
            st.rerun()

        except Exception as e:
            st.error(f"Erro ao processar transação: {str(e)}")
            st.exception(e)
            time.sleep(5)
            st.rerun()

def criar_bloco_falho():
    """
    Cria um bloco falho para testar a verificação da blockchain.
    """
    transacao = Transacao(
        remetente=UUID(int=2),
        destinatario=UUID(int=3),
        pontos=5.0
    )

    bloco = Bloco(
        transacao=transacao,
        hash_anterior=UUID(int=0).bytes,
        minerador=UUID(int=1)
    )

    st.session_state.blockchain.cadeia.append(bloco)

def main():
    iniciar_demo()

    st.markdown("# Blockchain Educacional")
    st.sidebar.title("Navegação")

    paginas = {
        "Grafo da Comunidade": "grafo",
        "Blockchain": "blockchain",
        "Criar e Minerar Transação": "transacao"
    }

    pagina_selecionada = st.sidebar.radio("Selecione uma página:", list(paginas.keys()))
    
    # Mostrar saldos de todos os usuários
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Saldos da Rede:**")
    for usuario in st.session_state.usuarios:
        st.sidebar.text(f"{usuario.nome}: {usuario.pontos:.2f}")

    pagina_id = paginas[pagina_selecionada]
    
    if pagina_id == "grafo":
        exibir_grafo()
    elif pagina_id == "blockchain":
        exibir_blockchain()
    elif pagina_id == "transacao":
        criar_e_minerar_transacao()
    
    # Botão para verificar integridade
    st.sidebar.markdown("---")
    if st.sidebar.button("Verificar Integridade"):
        try:
            st.session_state.blockchain.verificar()
            st.sidebar.success("Blockchain íntegra!")
        except Exception as e:
            st.sidebar.error(f"Erro: {str(e)}")         

    st.sidebar.markdown("---")
    if st.sidebar.button("Destrutivo: Criar um bloco falho"):
        criar_bloco_falho() 

if __name__ == "__main__":
    main()







