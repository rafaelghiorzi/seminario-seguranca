import datetime
from uuid import uuid4, UUID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey

class Transacao:
    """
    Classe que representa uma transação
    """
    def __init__(self, remetente: UUID, destinatario: UUID, conteudo: str) -> None:
        self.remetente = remetente
        self.destinatario = destinatario
        self.conteudo = conteudo
        self.timestamp = datetime.datetime.now()
        self.id = uuid4()
        self.assinatura = None

        self.mensagem = f"{self.remetente}-{self.destinatario}-{self.conteudo}-{self.timestamp}".encode('utf-8')

    def assinar(self, chave_privada: RSAPrivateKey) -> None:
        """
        Assina a transação com a chave privada do remetente
        """
        self.assinatura = chave_privada.sign(
            self.mensagem,
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
        try:
            chave_publica.verify(
                self.assinatura,
                self.mensagem,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
