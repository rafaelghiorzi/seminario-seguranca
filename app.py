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
    page_title="Blockchain",
    page_icon="⛓️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def iniciar_demo():
    """Inicia a demonstração da blockchain com dados de exemplo"""
    if "blockchain" not in st.session_state:
        st.session_state.blockchain = Blockchain()

        fake = faker.Faker("pt_BR")
        st.session_state.usuarios = []
        for _ in range(15):
            nome = fake.name()
            usuario = Usuario(
                nome, st.session_state.blockchain, random.uniform(10, 100)
            )
            st.session_state.usuarios.append(usuario)

        st.session_state.transacoes_pendentes = []


def exibir_blockchain():
    """Visualiza a cadeia de blocos e informações detalhadas"""
    st.subheader("Blockchain")

    blockchain = st.session_state.blockchain

    if len(blockchain.cadeia) <= 1:
        st.info("Apenas o bloco gênesis existe na cadeia.")
        return

    dados_blocos = []
    for i, bloco in enumerate(blockchain.cadeia):
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

        dados_blocos.append(
            {
                "Índice": i,
                "ID do Bloco": str(bloco.id)[:8] + "...",
                "Minerador": nome_minerador,
                "Transação": f"{nome_remetente} → {nome_destinatario}",
                "Pontos": f"{bloco.transacao.pontos:.2f}" if i > 0 else "N/A",
                "Timestamp": bloco.timestamp.strftime("%H:%M:%S"),
                "Hash": bloco.hash.hex()[:16] + "..." if bloco.hash else "N/A",
            }
        )

    df = pd.DataFrame(dados_blocos)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Visualização da Blockchain")

    #apresenta todos os blocos presentes na blockchain, encadeados
    fig = go.Figure()

    for i, bloco in enumerate(blockchain.cadeia):
        cor = "red" if i == 0 else "lightblue"
        nome = "Gênesis" if i == 0 else f"Bloco {i}"

        fig.add_trace(
            go.Scatter(
                x=[i],
                y=[0],
                mode="markers+text",
                text=[nome],
                textposition="top center",
                marker=dict(size=60, color=cor, line=dict(width=2, color="darkblue")),
                hovertext=f"ID: {str(bloco.id)[:8]}...<br>Hash: {bloco.hash.hex()[:16] if bloco.hash else 'N/A'}...",
                hoverinfo="text",
                showlegend=False,
            )
        )

    for i in range(len(blockchain.cadeia) - 1):
        fig.add_trace(
            go.Scatter(
                x=[i, i + 1],
                y=[0, 0],
                mode="lines",
                line=dict(width=3, color="gray"),
                showlegend=False,
                hoverinfo="none",
            )
        )

    fig.update_layout(
        title="Estrutura da Blockchain",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 0.5]
        ),
        height=200,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Informações detalhadas dos Blocos")

    if len(blockchain.cadeia) > 1:
        bloco_selecionado = st.selectbox(
            "Selecione um bloco para ver detalhes:",
            range(len(blockchain.cadeia)),
            format_func=lambda i: f"Bloco {i} - {'Gênesis' if i == 0 else 'Transação'}",
        )

    bloco: Bloco = blockchain.cadeia[bloco_selecionado]

    st.write("**Informações do Bloco:**")
    st.write(f"- **Índice:** {bloco_selecionado}")
    st.write(f"- **ID:** {str(bloco.id)}")
    st.write(f"- **Timestamp:** {bloco.timestamp}")
    st.write(f"- **Hash:** {bloco.hash.hex() if bloco.hash else 'N/A'}")
    st.write(
        f"- **Hash Anterior:** {bloco.hash_anterior.hex() if bloco.hash_anterior else 'N/A'}"
    )

    st.write("**Informações da Transação:**")
    st.write(f"- **ID da Transação:** {str(bloco.transacao.id)}")

    nome_remetente = (
        "Sistema"
    )
    nome_destinatario = (
        "Sistema"
    )

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

    st.write(f"- **Remetente:** {bloco.transacao.remetente} ({nome_remetente})")
    st.write(
            f"- **Destinatário:** {bloco.transacao.destinatario} ({nome_destinatario})"
        )
    st.write(f"- **Pontos:** {bloco.transacao.pontos:.2f}")

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
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Remetente:**")
        nomes = [f"{u.nome} ({u.pontos:.2f} pontos)" for u in st.session_state.usuarios]

        indice = st.selectbox(
            "Selecione o remetente:",
            range(len(st.session_state.usuarios)),
            format_func=lambda i: nomes[i],
        )

        remetente: Usuario = st.session_state.usuarios[indice]

    with col2:
        st.write("**Destinatário:**")
        usuarios_disponiveis = [
            u for u in st.session_state.usuarios if u.id != remetente.id
        ]

        if not usuarios_disponiveis:
            st.warning("Nenhum destinatário disponível.")
            return

        nomes_destinatarios = [
            f"{u.nome} ({u.pontos:.2f} pontos)" for u in usuarios_disponiveis
        ]

        indice_destinatario = st.selectbox(
            "Selecione o destinatário:",
            range(len(usuarios_disponiveis)),
            format_func=lambda i: nomes_destinatarios[i],
        )

        destinatario: Usuario = usuarios_disponiveis[indice_destinatario]

    st.write("**Valor da Transação:**")
    pontos = st.number_input("Digite o valor em pontos:", step=0.01, format="%.2f")

    botao_desabilitado = pontos <= 0
    if st.button(
        "Criar e minerar transação", type="primary", disabled=botao_desabilitado
    ):
        if pontos <= 0:
            st.error("O valor da transação deve ser maior que zero.")
            return

        try:
            with st.container():
                st.subheader("Processo de Mineração e Consenso")

                st.info(
                    f"**Transação:** {remetente.nome} → {destinatario.nome} | **Valor:** {pontos:.2f} pontos"
                )

                log_container = st.empty()
                logs = []

                def log_callback(message):
                    logs.append(message)
                    log_text = "\n".join(logs)
                    log_container.text_area(
                        "Log do Processo:", value=log_text, height=500, disabled=True
                    )

                transacao = remetente.criar_transacao(destinatario.id, pontos)
                bloco = remetente.minerar_bloco(transacao, log_callback)

                if bloco:
                    st.success(
                        f"Transação concluída com sucesso! Bloco ID: {str(bloco.id)[:8]}..."
                    )

                    st.subheader("Sumário Final")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Status", "Sucesso")
                        st.metric("Bloco ID", str(bloco.id)[:8])

                    with col2:
                        st.metric("Novo saldo - Remetente", f"{remetente.pontos:.2f}")
                        st.metric(
                            "Novo saldo - Destinatário", f"{destinatario.pontos:.2f}"
                        )

                    st.session_state.blockchain.verificar()
                else:
                    st.error("Transação falhou - Bloco rejeitado pela rede")
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
    transacao = Transacao(remetente=UUID(int=2), destinatario=UUID(int=3), pontos=5.0)

    bloco = Bloco(
        transacao=transacao, hash_anterior=UUID(int=0).bytes, minerador=UUID(int=1)
    )

    st.session_state.blockchain.cadeia.append(bloco)


def exibir_comunidade():
    """Visualiza o grafo de relacionamento da comunidade e informações dos usuários"""
    st.subheader("Comunidade da Rede")

    blockchain = st.session_state.blockchain

    st.subheader("Grafo da Comunidade")

    if not blockchain.comunidade:
        st.info("Nenhuma transação registrada. O grafo está vazio.")
    else:
        #cria grafo da relação entre os usuários
        G = nx.Graph()

        for usuario in st.session_state.usuarios:
            status = "ativo" if usuario.id in blockchain.usuarios_por_id else "banido"
            cor = "black" if status == "ativo" else "red"
            G.add_node(str(usuario.id), label=usuario.nome, color=cor, status=status)

        for remetente, destinatarios in blockchain.comunidade.items():
            for destinatario in destinatarios:
                if remetente != UUID(int=0):  
                    G.add_edge(str(remetente), str(destinatario))

        if len(G.edges()) == 0:
            st.info("Nenhuma conexão entre usuários registradas.")
        else:
            pos = nx.spring_layout(G, k=3, iterations=50)

            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=2, color="#888"),
                hoverinfo="none",
                mode="lines",
                showlegend=False,
            )

            node_x_ativo = []
            node_y_ativo = []
            node_text_ativo = []
            node_info_ativo = []

            node_x_banido = []
            node_y_banido = []
            node_text_banido = []
            node_info_banido = []

            for node in G.nodes():
                x, y = pos[node]

                nome = "Desconhecido"
                status = "ativo"
                for usuario in st.session_state.usuarios:
                    if str(usuario.id) == node:
                        nome = usuario.nome
                        status = (
                            "ativo"
                            if usuario.id in blockchain.usuarios_por_id
                            else "banido"
                        )
                        break

                node_text = nome
                node_info = (
                    f"Usuário: {nome}<br>ID: {node[:8]}...<br>Status: {status.title()}"
                )

                if status == "ativo":
                    node_x_ativo.append(x)
                    node_y_ativo.append(y)
                    node_text_ativo.append(node_text)
                    node_info_ativo.append(node_info)
                else:
                    node_x_banido.append(x)
                    node_y_banido.append(y)
                    node_text_banido.append(node_text)
                    node_info_banido.append(node_info)

            traces = [edge_trace]

            if node_x_ativo:
                node_trace_ativo = go.Scatter(
                    x=node_x_ativo,
                    y=node_y_ativo,
                    mode="markers+text",
                    text=node_text_ativo,
                    textposition="middle center",
                    textfont=dict(color="white", size=12),
                    hovertext=node_info_ativo,
                    hoverinfo="text",
                    name="Usuários Ativos",
                    marker=dict(
                        size=60,
                        color="darkgreen",
                        line=dict(width=2, color="green"),
                    ),
                )
                traces.append(node_trace_ativo)

            if node_x_banido:
                node_trace_banido = go.Scatter(
                    x=node_x_banido,
                    y=node_y_banido,
                    mode="markers+text",
                    text=node_text_banido,
                    textposition="middle center",
                    textfont=dict(color="white", size=12),
                    hovertext=node_info_banido,
                    hoverinfo="text",
                    name="Usuários Banidos",
                    marker=dict(
                        size=60, color="darkred", line=dict(width=2, color="red")
                    ),
                )
                traces.append(node_trace_banido)

            fig = go.Figure(
                data=traces,
                layout=go.Layout(
                    title=dict(
                        text="Relacionamentos entre Usuários", font=dict(size=16)
                    ),
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[
                        dict(
                            text="🟢 Ativo | 🔴 Banido | Conexões baseadas em transações",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.005,
                            y=-0.002,
                            xanchor="left",
                            yanchor="bottom",
                            font=dict(color="gray", size=12),
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Usuários da Rede")

    if not st.session_state.usuarios:
        st.info("Nenhum usuário registrado na rede.")
        return

    dados_usuarios = []

    #dados de todos os usuários da rede
    for usuario in st.session_state.usuarios:
        status = "Ativo" if usuario.id in blockchain.usuarios_por_id else "Banido"
        dados_usuarios.append(
            {
                "Nome": usuario.nome,
                "ID": str(usuario.id)[:8] + "...",
                "Saldo": f"{usuario.pontos:.2f}",
                "Status": status,
            }
        )

    df = pd.DataFrame(dados_usuarios)

    def highlight_status(row):
        if row["Status"] == "Ativo":
            return ["background-color: #11181a"] * len(row)
        else:
            return ["background-color: #290707"] * len(row)

    styled_df = df.style.apply(highlight_status, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.subheader("Gerenciar Usuários")

    col1, col2 = st.columns(2)

    #banir usuario
    with col1:
        st.write("**Banir Usuário**")
        usuarios_ativos = [
            u for u in st.session_state.usuarios if u.id in blockchain.usuarios_por_id
        ]

        if usuarios_ativos:
            nomes_ativos = [
                f"{u.nome} ({u.pontos:.2f} pontos)" for u in usuarios_ativos
            ]

            indice_usuario = st.selectbox(
                "Selecione um usuário para banir:",
                range(len(usuarios_ativos)),
                format_func=lambda i: nomes_ativos[i],
            )

            usuario_selecionado = usuarios_ativos[indice_usuario]

            if st.button("Banir Usuário", type="secondary"):
                blockchain.banir(usuario_selecionado.id)
                st.success(f"Usuário {usuario_selecionado.nome} foi banido da rede.")
                st.rerun()
        else:
            st.info("Nenhum usuário ativo para banir.")

    #desbanir usuário
    with col2:
        st.write("**Desbanir Usuário**")
        usuarios_banidos = [
            u
            for u in st.session_state.usuarios
            if u.id not in blockchain.usuarios_por_id
        ]

        if usuarios_banidos:
            nomes_banidos = [
                f"{u.nome} ({u.pontos:.2f} pontos)" for u in usuarios_banidos
            ]

            indice_usuario_banido = st.selectbox(
                "Selecione um usuário para desbanir:",
                range(len(usuarios_banidos)),
                format_func=lambda i: nomes_banidos[i],
            )

            usuario_selecionado = usuarios_banidos[indice_usuario_banido]

            if st.button("Desbanir Usuário", type="primary"):
                if blockchain.desbanir(usuario_selecionado.id):
                    st.success(
                        f"Usuário {usuario_selecionado.nome} foi desbanido com sucesso!"
                    )
                    st.rerun()
                else:
                    st.error("Não foi possível desbanir o usuário.")
        else:
            st.info("Nenhum usuário banido para desbanir.")


def main():
    iniciar_demo()

    st.markdown("# Blockchain")
    st.sidebar.title("Navegação")

    paginas = {
        "Comunidade": "comunidade",
        "Blockchain": "blockchain",
        "Criar e Minerar Transação": "transacao",
    }

    pagina_selecionada = st.sidebar.radio("Selecione uma página:", list(paginas.keys()))

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Resumo da Rede:**")
    usuarios_ativos = [
        u
        for u in st.session_state.usuarios
        if u.id in st.session_state.blockchain.usuarios_por_id
    ]
    usuarios_banidos = len(st.session_state.usuarios) - len(usuarios_ativos)

    st.sidebar.metric("Usuários Ativos", len(usuarios_ativos))
    st.sidebar.metric("Usuários Banidos", usuarios_banidos)

    total_pontos = sum(u.pontos for u in usuarios_ativos)
    st.sidebar.metric("Total de Pontos", f"{total_pontos:.2f}")

    pagina_id = paginas[pagina_selecionada]

    if pagina_id == "comunidade":
        exibir_comunidade()
    elif pagina_id == "blockchain":
        exibir_blockchain()
    elif pagina_id == "transacao":
        criar_e_minerar_transacao()

    #verifica se todos os blocos estão corretos
    st.sidebar.markdown("---")
    if st.sidebar.button("Verificar Integridade"):
        try:
            st.session_state.blockchain.verificar()
            st.sidebar.success("Blockchain íntegra!")
        except Exception as e:
            st.sidebar.error(f"Erro: {str(e)}")

    #cria bloco falho para dar erro na blockchain
    if st.sidebar.button("Destrutivo: Criar um bloco falho"):
        criar_bloco_falho()


if __name__ == "__main__":
    main()
