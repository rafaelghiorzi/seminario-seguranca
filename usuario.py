from bloco import Bloco
from typing import Optional
from uuid import uuid4, UUID
from transacao import Transacao
from blockchain import Blockchain
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
import datetime

class Usuario:
    """
    Classe que representa um usário na blockchain.
    """
    def __init__(self, nome: str, blockchain: Blockchain) -> None:
        self.id = uuid4()
        self.nome = nome
        self.blockchain = blockchain

        self.chave_privada: RSAPrivateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.chave_publica: RSAPublicKey = self.chave_privada.public_key()

        self.blockchain.registrar_usuario(self)

    def criar_transacao(
        self,
        destinatario_id: UUID,
        conteudo: str,
    ) -> Transacao:
        """
        Cria uma nova transação e a assina com a chave privada do usuário.
        """
        if not isinstance(destinatario_id, UUID):
            raise ValueError("O destinatário deve ser um UUID válido")
        if not conteudo or not isinstance(conteudo, str):
            raise ValueError("O conteúdo da transação deve ser uma string não vazia")

        transacao = Transacao(
            remetente=self.id,
            destinatario=destinatario_id,
            conteudo=conteudo
        )
        transacao.assinar(self.chave_privada)
        return transacao

    def minerar_bloco(
        self,
        transacao: Transacao,
    ) -> Optional[Bloco]:
        """
        Cria um novo bloco, o assina e o propõe para a blockchain.
        """
        hash_anterior = self.blockchain.ultimo_bloco().hash
        if hash_anterior is None:
            raise ValueError("Blockchain vazia, não é possível minerar um bloco")

        bloco = Bloco(
            transacao=transacao,
            hash_anterior=hash_anterior,
            minerador=self.id
        )

        bloco.assinar(self.chave_privada)

        # Propõe o bloco para a rede (a classe Blockchain)
        if self.blockchain.adicionar_bloco(bloco):
            return bloco
        else:
            print(f"FALHA: Bloco minerado por {self.nome} foi rejeitado pela rede.")
            return None

    def consentir(self, bloco: Bloco) -> bool:
        """
        Função de validação chamada pelo mecanismo de consenso da blockchain.
        O usuário verifica se o bloco proposto é válido de acordo com sua visão da cadeia.
        """
        # Registrar no log de consenso (se disponível)
        import streamlit as st
        if hasattr(st, 'session_state') and 'log_consenso' in st.session_state:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Um usuário sempre confia na sua própria visão do último bloco.
        if bloco.hash_anterior != self.blockchain.ultimo_bloco().hash:
            mensagem = f"{self.nome}: Rejeitando bloco - hash anterior não confere"
            print(f"DEBUG ({self.nome}): Rejeitando, hash anterior não bate.")
            
            if hasattr(st, 'session_state') and 'log_consenso' in st.session_state:
                st.session_state.log_consenso.append({
                    'timestamp': timestamp,
                    'nivel': 'WARNING',
                    'mensagem': mensagem
                })
            return False

        chave_minerador = self.blockchain.get_chave(bloco.minerador)
        if not chave_minerador or not bloco.validar(chave_minerador):
            mensagem = f"{self.nome}: Rejeitando bloco - assinatura inválida"
            print(f"DEBUG ({self.nome}): Rejeitando, assinatura do minerador inválida.")
            
            if hasattr(st, 'session_state') and 'log_consenso' in st.session_state:
                st.session_state.log_consenso.append({
                    'timestamp': timestamp,
                    'nivel': 'WARNING',
                    'mensagem': mensagem
                })
            return False

        # Voto favorável
        mensagem = f"{self.nome}: Aprovando bloco {str(bloco.id)[:8]}..."
        if hasattr(st, 'session_state') and 'log_consenso' in st.session_state:
            st.session_state.log_consenso.append({
                'timestamp': timestamp,
                'nivel': 'SUCCESS',
                'mensagem': mensagem
            })
        
        return True