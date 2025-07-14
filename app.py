import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import pandas as pd
import json
import time
import random
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Dict, Any
import faker

from src.bloco import Bloco
from src.usuario import Usuario
from src.transacao import Transacao
from src.blockchain import Blockchain

# Configuração da página
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
        fake = faker.Faker()
        st.session_state.usuarios = []
        for _ in range(8):
            nome = fake.name()
            usuario = Usuario(nome, st.session_state.blockchain)
            st.session_state.usuarios.append(usuario)
        
        st.session_state.usuario_atual = st.session_state.usuarios[0]
        st.session_state.transacoes_pendentes = []
        st.session_state.verificacao_log = []

def exibir_grafo():
    """Visualiza o grafo de relacionamento da comunidade"""
    st.subheader("🌐 Grafo da Comunidade")
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
    st.subheader("⛓️ Blockchain")
    
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
        
    bloco = blockchain.cadeia[bloco_selecionado]

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
    st.write(f"- **Conteúdo:** {bloco.transacao.conteudo}")
    
    # Encontrar nome do minerador
    nome_minerador = "Sistema"
    if bloco.minerador != UUID(int=0):
        for usuario in st.session_state.usuarios:
            if usuario.id == bloco.minerador:
                nome_minerador = usuario.nome
                break
    st.write(f"**Minerador do bloco:** {nome_minerador}")

def criar_e_minerar_transacao():
    """Interface combinada para criar transação e minerar bloco"""
    st.subheader("💰 Criar e Minerar Transação")
    
    # Seleção do usuário ativo
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Usuário Ativo:**")
        nomes_usuarios = [f"{u.nome}" for u in st.session_state.usuarios]
        indice_atual = st.session_state.usuarios.index(st.session_state.usuario_atual)
        
        novo_indice = st.selectbox(
            "Selecionar usuário:",
            range(len(st.session_state.usuarios)),
            index=indice_atual,
            format_func=lambda i: nomes_usuarios[i]
        )
        
        if novo_indice != indice_atual:
            st.session_state.usuario_atual = st.session_state.usuarios[novo_indice]
            st.rerun()
    
    with col2:
        st.write("**Destinatário:**")
        usuarios_disponiveis = [u for u in st.session_state.usuarios if u.id != st.session_state.usuario_atual.id]
        
        if not usuarios_disponiveis:
            st.warning("Nenhum outro usuário disponível para transação.")
            return
        
        nomes_destinatarios = [f"{u.nome}" for u in usuarios_disponiveis]
        indice_destinatario = st.selectbox(
            "Selecionar destinatário:",
            range(len(usuarios_disponiveis)),
            format_func=lambda i: nomes_destinatarios[i]
        )
        
        destinatario = usuarios_disponiveis[indice_destinatario]
    
    # Conteúdo da transação
    conteudo = st.text_area(
        "Conteúdo da transação:",
        placeholder="Digite o conteúdo da transação...",
        height=100
    )
    
    # Container para o log de verificação
    verification_container = st.container()
    
    # Botão para criar e minerar
    if st.button("🚀 Criar e Minerar Transação", type="primary"):
        if conteudo.strip():
            try:
                # Limpar log anterior
                st.session_state.verificacao_log = []
                
                # Criar transação
                transacao = st.session_state.usuario_atual.criar_transacao(
                    destinatario.id,
                    conteudo.strip()
                )
                
                st.success(f"✅ Transação criada: {st.session_state.usuario_atual.nome} → {destinatario.nome}")
                
                # Simular processo de mineração com verificação
                with verification_container:
                    st.subheader("🔍 Processo de Verificação")
                    
                    # Placeholder para atualizações em tempo real
                    status_placeholder = st.empty()
                    
                    # Simular verificação por cada usuário
                    for i, usuario in enumerate(st.session_state.usuarios):
                        time.sleep(0.5)  # Simular tempo de processamento
                        
                        # Verificar se o usuário aprova a transação
                        aprovado = random.choice([True, True, True, False])  # 75% de aprovação
                        
                        if aprovado:
                            status_placeholder.success(f"✅ {usuario.nome} aprovou a transação")
                        else:
                            status_placeholder.error(f"❌ {usuario.nome} rejeitou a transação")
                        
                        # Atualizar log
                        st.session_state.verificacao_log.append({
                            'usuario': usuario.nome,
                            'aprovado': aprovado,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                    
                    # Verificar consenso (maioria simples)
                    aprovacoes = sum(1 for entry in st.session_state.verificacao_log if entry['aprovado'])
                    total_usuarios = len(st.session_state.usuarios)
                    consenso_alcancado = aprovacoes > total_usuarios // 2
                    
                    time.sleep(1)
                    
                    if consenso_alcancado:
                        # Minerar o bloco
                        bloco_minerado = st.session_state.usuario_atual.minerar_bloco(transacao)
                        
                        if bloco_minerado:
                            st.markdown(f"""
                            <div class="success-box">
                                ✅ <b>Bloco minerado e adicionado com sucesso!</b><br>
                                <b>Consenso:</b> {aprovacoes}/{total_usuarios} usuários aprovaram<br>
                                <b>Minerador:</b> {st.session_state.usuario_atual.nome}<br>
                                <b>ID do Bloco:</b> {str(bloco_minerado.id)[:8]}...<br>
                                <b>Hash:</b> {bloco_minerado.hash.hex()[:16]}...
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("❌ Erro na mineração do bloco")
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            ❌ <b>Transação rejeitada pela rede!</b><br>
                            <b>Consenso:</b> {aprovacoes}/{total_usuarios} usuários aprovaram<br>
                            Consenso mínimo não alcançado ({total_usuarios//2 + 1} aprovações necessárias)
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Mostrar log detalhado
                    st.subheader("📊 Log de Verificação")
                    for entry in st.session_state.verificacao_log:
                        status = "✅ Aprovado" if entry['aprovado'] else "❌ Rejeitado"
                        st.markdown(f"""
                        <div class="verification-box">
                            <b>[{entry['timestamp']}]</b> {entry['usuario']}: {status}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Atualizar a página após mineração
                    time.sleep(2)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erro ao processar transação: {str(e)}")
        else:
            st.warning("Por favor, insira o conteúdo da transação.")

def main():
    """Função principal da aplicação"""
    iniciar_demo()
    
    # Cabeçalho principal
    st.markdown('<h1 class="main-header">⛓️ Blockchain Educacional</h1>', unsafe_allow_html=True)
    
    # Navegação simplificada
    st.sidebar.title("🧭 Navegação")
    
    paginas = {
        "🌐 Grafo da Comunidade": "grafo",
        "⛓️ Blockchain": "blockchain",
        "💰 Criar Transação": "transacao"
    }
    
    pagina_selecionada = st.sidebar.radio(
        "Selecione uma página:",
        list(paginas.keys())
    )
    
    # Estatísticas na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Estatísticas:**")
    st.sidebar.metric("Blocos na Cadeia", len(st.session_state.blockchain.cadeia))
    st.sidebar.metric("Usuários na Rede", len(st.session_state.usuarios))
    st.sidebar.metric("Conexões", sum(len(conexoes) for conexoes in st.session_state.blockchain.comunidade.values()) // 2)
    
    # Informações do usuário atual
    st.sidebar.markdown("---")
    st.sidebar.markdown("**👤 Usuário Ativo:**")
    st.sidebar.info(f"**{st.session_state.usuario_atual.nome}**")
    
    # Renderizar página selecionada
    pagina_id = paginas[pagina_selecionada]
    
    if pagina_id == "grafo":
        exibir_grafo()
    elif pagina_id == "blockchain":
        exibir_blockchain()
    elif pagina_id == "transacao":
        criar_e_minerar_transacao()
    
    # Botão para verificar integridade
    st.sidebar.markdown("---")
    if st.sidebar.button("🔍 Verificar Integridade"):
        try:
            st.session_state.blockchain.verificar()
            st.sidebar.success("✅ Blockchain íntegra!")
        except Exception as e:
            st.sidebar.error(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()















