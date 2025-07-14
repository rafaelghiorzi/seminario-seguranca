from uuid import UUID
from bloco import Bloco
from usuario import Usuario
from transacao import Transacao
from collections import defaultdict
from typing import List, Dict, Set, Optional, DefaultDict
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

class Blockchain:
    """
    Classe principal que representa a blockchain.
    Administra a cadeia de blocos, transações e chaves públicas.
    A cadeia de blocos é administrada pelos próprios blocos
    """

    def __init__(self) -> None:
        self.cadeia: List[Bloco] = []
        self.tamanho = 0

        # Grafo dos usuários.
        self.comunidade: DefaultDict[UUID, Set[UUID]] = defaultdict(set)
        # Mapeamento das chaves públicas.
        self.chaves_publicas: Dict[UUID, RSAPublicKey] = {}
        # [NOVO] Lista de usuários para o mecanismo de consenso.
        self.usuarios_registrados: List['Usuario'] = []

        self._genesis_block()

    def _genesis_block(self):
        """
        Cria o bloco gênesis
        """
        genesis_id = UUID(int=0)
        transacao = Transacao(
            remetente=genesis_id,
            destinatario=genesis_id,
            conteudo="Bloco Gênesis"
        )

        bloco = Bloco(
            transacao=transacao,
            hash_anterior=b"0" * 32,
            minerador=genesis_id
        )

        bloco.hash = bloco.calcular_hash()
        self.cadeia.append(bloco)
        self.tamanho = 1

    def registrar_usuario(self, usuario: 'Usuario') -> None:
        """Registra a chave pública de um usuário na blockchain."""
        self.chaves_publicas[usuario.id] = usuario.chave_publica
        self.usuarios_registrados.append(usuario)

    def get_chave(self, uuid: UUID) -> Optional[RSAPublicKey]:
        """
        Retorna a chave pública de um usuário.
        Se o usuário não existir, retorna None.
        """
        return self.chaves_publicas.get(uuid)

    def ultimo_bloco(self) -> Bloco:
        """
        Retorna o último bloco da cadeia.
        Se a cadeia estiver vazia, retorna None.
        """
        return self.cadeia[-1]

    def adicionar_bloco(self, bloco: Bloco) -> bool:
        """
        Adiciona um novo bloco à blockchain apenas após
        validação completa e consenso entre os usuários.
        """

        # Essa é a lógica mais importante do projeto
        # 1. Validação do bloco
        chave_minerador = self.get_chave(bloco.minerador)
        if not chave_minerador:
            return False

        if not bloco.validar(chave_minerador):
            return False

        # 2. validação da transação do bloco
        remetente = bloco.transacao.remetente
        chave_remetente = self.get_chave(remetente)
        if not chave_remetente:
            # Checa se o primeiro bloco é o gênesis
            if remetente != UUID(int=0):
                return False
        elif not bloco.transacao.validar(chave_remetente):
            return False

        # 3. Verifica o hash anterior
        hash_anterior = self.ultimo_bloco().hash
        if bloco.hash_anterior != hash_anterior:
            return False

        # 4. Verifica se o bloco já existe
        if bloco.id in [b.id for b in self.cadeia]:
            return False

        # 5. Checando consenso dos usuários
        if len(self.usuarios_registrados) > 1:
            for usuario in self.usuarios_registrados:
                if usuario.id != bloco.minerador:
                    if not usuario.consentir(bloco):
                        return False
            print(f"Bloco {bloco.id} minerado por {bloco.minerador} com sucesso!")

        self.cadeia.append(bloco)
        self.tamanho += 1

        # Conectando dois usuários no grafo da comunidade
        remetente = bloco.transacao.remetente
        destinatario = bloco.transacao.destinatario
        if remetente != UUID(int=0):
            self.comunidade[remetente].add(destinatario)
            self.comunidade[destinatario].add(remetente)

        return True

    def verificar(self) -> None:
        """Verifica a integridade da blockchain"""
        for i in range(1, len(self.cadeia)):
            bloco_atual = self.cadeia[i]
            bloco_anterior = self.cadeia[i - 1]

            # Verifica o hash do bloco atual
            if bloco_atual.hash != bloco_atual.calcular_hash():
                raise ValueError(f"Bloco {bloco_atual.id} inválido: hash incorreto")

            # Verifica o hash anterior
            if bloco_atual.hash_anterior != bloco_anterior.hash:
                raise ValueError(f"Bloco {bloco_atual.id} inválido: hash anterior incorreto")

        print("Blockchain verificada com sucesso! Todos os blocos são válidos.")