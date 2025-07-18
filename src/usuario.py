import time
import random
from src.bloco import Bloco
from typing import Optional
from uuid import uuid4, UUID
from src.transacao import Transacao
from src.blockchain import Blockchain
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey


class Usuario:
    """
    Classe que representa um usário na blockchain.
    """

    def __init__(self, nome: str, blockchain: Blockchain, pontos: float) -> None:
        self.id = uuid4()
        self.nome = nome
        self.blockchain = blockchain
        self.pontos = pontos

        self.chave_privada: RSAPrivateKey = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        self.chave_publica: RSAPublicKey = self.chave_privada.public_key()

        self.blockchain.registrar_usuario(self)

    def criar_transacao(self, destinatario_id: UUID, pontos: float) -> Transacao:
        """
        Cria uma nova transação e a assina com a chave privada do usuário.
        """
        if not isinstance(destinatario_id, UUID):
            raise ValueError("O destinatário deve ser um UUID válido")
        if not pontos or not isinstance(pontos, float):
            raise ValueError("O conteúdo da transação deve ser um número não vazio")

        transacao = Transacao(
            remetente=self.id, destinatario=destinatario_id, pontos=pontos
        )
        transacao.assinar(self.chave_privada)
        return transacao

    def minerar_bloco(self, transacao: Transacao, log_callback=None) -> Optional[Bloco]:
        """
        Cria um novo bloco, o assina e o propõe para a blockchain.
        """
        hash_anterior = self.blockchain.ultimo_bloco().hash
        if hash_anterior is None:
            raise ValueError("Blockchain vazia, não é possível minerar um bloco")

        if log_callback:
            log_callback(f"{self.nome} está minerando um novo bloco...")

        bloco = Bloco(
            transacao=transacao, hash_anterior=hash_anterior, minerador=self.id
        )
        bloco.assinar(self.chave_privada)

        if log_callback:
            log_callback(f"Bloco assinado e pronto para validação da rede...")

        if self.blockchain.adicionar_bloco(bloco, log_callback):
            if log_callback:
                log_callback(f"Bloco adicionado à blockchain com sucesso!")
            return bloco
        else:
            if log_callback:
                log_callback(f"Falha ao adicionar bloco à blockchain!")
            return None

    def consentir(self, bloco: Bloco) -> tuple[bool, str]:
        #Retorna uma tupla: caso ocorra algum erro, False e o motivo do erro, caso nao, True e mensagem de sucesso
        time.sleep(random.uniform(0.5, 1))
        if random.random() < 0.1: #Simula decisao maliciosa
            return False, "Decisão aleatória de não consentir"
        if bloco.hash_anterior != self.blockchain.ultimo_bloco().hash:
            return False, "Hash anterior inválido" #Verifica hash anterior
        if bloco.transacao.remetente not in self.blockchain.usuarios_por_id or bloco.transacao.destinatario not in self.blockchain.usuarios_por_id:
            return False, "Algum participante da transação está banido da blockchain"
        chave_minerador = self.blockchain.get_chave(bloco.minerador)
        chave_emitente = self.blockchain.get_chave(bloco.transacao.remetente)
        if not chave_minerador or not bloco.validar(chave_minerador) or not bloco.validar(chave_emitente): #Verifica assinaturas
            return False, "Validação criptográfica falhou"
        if bloco.transacao.pontos <= 0: #Verifica se foi passado um valor invalido
            return False, "Valor da transação inválido"
        if bloco.transacao.remetente == UUID(int=0): #Aprova bloco genesis
            return True, "Transação gênesis aprovada"
        if not self.blockchain.compare_pontos(bloco.transacao.remetente, bloco.transacao.pontos): #Verifica se remetente tem saldo suficiente
            return False, "Saldo insuficiente do remetente"
        return True, "Bloco válido e aprovado"
