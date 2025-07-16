import hashlib
from uuid import uuid4, UUID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey


class Transacao:
    """
    Classe que representa uma transação
    """
    def __init__(self, remetente: UUID, destinatario: UUID, pontos: float) -> None:
        self.remetente = remetente
        self.destinatario = destinatario
        self.pontos = pontos
        self.id = uuid4()

        self.assinatura = None
        self.hash = None

    def calcular_hash(self) -> bytes:
        digest = hashlib.sha256()
        digest.update(self.remetente.bytes)
        digest.update(self.destinatario.bytes)
        digest.update(str(self.pontos).encode('utf-8'))
        digest.update(str(self.id).encode('utf-8'))
        return digest.digest()

    def assinar(self, chave_privada: RSAPrivateKey) -> None:
        """
        Assina o hash da transação com a chave privada do remetente
        """
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
        Verifica a assinatura da transação
        """
        if not self.assinatura:
            return False
        if not self.hash or not self.assinatura:
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