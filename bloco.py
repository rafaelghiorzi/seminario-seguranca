import hashlib
import datetime
from uuid import uuid4, UUID
from transacao import Transacao
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

class Bloco:
    """
    Classe que representa um bloco
    """
    def __init__(self, transacao: Transacao, hash_anterior: bytes, minerador: UUID) -> None:
        self.transacao = transacao
        self.minerador = minerador
        self.hash_anterior = hash_anterior
        self.timestamp: datetime.datetime = datetime.datetime.now()
        self.id: UUID = uuid4()

        self.assinatura = None
        self.hash = None

    def calcular_hash(self) -> bytes:
        digest = hashlib.sha256()
        digest.update(str(self.transacao.id).encode('utf-8'))
        digest.update(self.hash_anterior)
        digest.update(str(self.timestamp).encode('utf-8'))
        digest.update(str(self.minerador).encode('utf-8'))
        return digest.digest()

    def assinar(self, chave_privada: RSAPrivateKey) -> None:
        """Assina o bloco e gera o hash"""
        self.hash = self.calcular_hash()
        self.assinatura = chave_privada.sign(
            self.hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def validar(self, chave_publica: RSAPublicKey) -> bool:
        """
        Verifica a assinatura do bloco
        """
        if self.assinatura is None or self.hash is None:
            return False
        if self.hash != self.calcular_hash():
            return False

        try:
            chave_publica.verify(
                self.assinatura,
                self.hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False