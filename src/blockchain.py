from uuid import UUID
from src.bloco import Bloco
from src.transacao import Transacao
from collections import defaultdict
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing import List, Dict, Set, Optional, DefaultDict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.usuario import Usuario

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
        # Lista de usuários para o mecanismo de consenso.
        self.usuarios_registrados: List["Usuario"] = []
        # Mapeando usuários para seus ids
        self.usuarios_por_id: Dict[UUID, "Usuario"] = {}
        # Lista completa de todos os usuários (ativos e banidos)
        self.todos_usuarios: List["Usuario"] = []

        self._genesis_block()

    def _genesis_block(self):
        """
        Cria o bloco gênesis
        """
        genesis_id = UUID(int=0)
        transacao = Transacao(remetente=genesis_id, destinatario=genesis_id, pontos=0.0)

        bloco = Bloco(
            transacao=transacao, hash_anterior=b"0" * 32, minerador=genesis_id
        )

        bloco.hash = bloco.calcular_hash()
        bloco.assinatura = None
        self.cadeia.append(bloco)
        self.tamanho = 1

    def registrar_usuario(self, usuario: "Usuario") -> None:
        """Registra a chave pública de um usuário na blockchain."""
        self.chaves_publicas[usuario.id] = usuario.chave_publica
        self.usuarios_registrados.append(usuario)
        self.usuarios_por_id[usuario.id] = usuario
        if usuario not in self.todos_usuarios:
            self.todos_usuarios.append(usuario)

    def banir(self, usuario_id: UUID) -> None:
        """
        Banir um usuário da blockchain.
        Remove o usuário da lista de usuários registrados e limpa sua chave pública.
        """
        if usuario_id in self.usuarios_por_id:
            usuario = self.usuarios_por_id[usuario_id]
            if usuario in self.usuarios_registrados:
                self.usuarios_registrados.remove(usuario)
                del self.chaves_publicas[usuario_id]
                del self.usuarios_por_id[usuario_id]
                print(f"Usuário {usuario.nome} banido com sucesso.")
            else:
                print(f"Usuário {usuario.nome} já está banido.")
        else:
            print("Usuário não encontrado na blockchain.")

    def desbanir(self, usuario_id: UUID) -> bool:
        """
        Desbane um usuário da blockchain, permitindo que ele volte a participar.
        """
        for usuario in self.todos_usuarios:
            if usuario.id == usuario_id and usuario_id not in self.usuarios_por_id:
                self.usuarios_registrados.append(usuario)
                self.usuarios_por_id[usuario_id] = usuario
                self.chaves_publicas[usuario_id] = usuario.chave_publica
                print(f"Usuário {usuario.nome} foi desbanido com sucesso.")
                return True
        return False

    def compare_pontos(self, usuario_id: UUID, pontos: float) -> bool:
        """
        Compara os pontos de um usuário com um valor fornecido.
        Retorna True se o usuário tiver pontos suficientes, False caso contrário.
        """
        usuario = self.usuarios_por_id.get(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado na blockchain")

        return usuario.pontos >= pontos

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

    def adicionar_bloco(self, bloco: Bloco, log_callback=None) -> bool:
        """
        Adiciona um novo bloco à blockchain apenas após
        validação completa e consenso entre os usuários.
        """

        # Cada usuário deve consentir com a adição do bloco
        if len(self.usuarios_registrados) > 1:
            favoraveis = 0
            total_usuarios = len(
                [u for u in self.usuarios_registrados if u.id != bloco.minerador]
            )
            votos = []

            # 1/3 dos usuários devem aprovar
            necessario = total_usuarios // 3 + 1

            if log_callback:
                log_callback(
                    f"🗳️ Iniciando processo de consenso com {total_usuarios} usuários votantes..."
                )
                log_callback(
                    f"📊 Necessário: {necessario} votos favoráveis para aprovação"
                )

            for usuario in self.usuarios_registrados:
                if usuario.id != bloco.minerador:
                    if log_callback:
                        log_callback(f"⏳ {usuario.nome} está analisando o bloco...")

                    decisao, motivo = usuario.consentir(bloco)
                    votos.append((usuario.nome, decisao, motivo))

                    if decisao:
                        favoraveis += 1
                        if log_callback:
                            log_callback(f"✅ {usuario.nome}: APROVOU - {motivo}")

                        # Parada brusca: se alcançou o necessário, pare imediatamente
                        if favoraveis >= necessario:
                            if log_callback:
                                log_callback(
                                    f"Consenso de 1/3 alcançado: {favoraveis}/{total_usuarios} votos favoráveis!"
                                )
                            print(
                                f"Bloco {bloco.id} minerado por {bloco.minerador} com sucesso!"
                            )
                            break
                    else:
                        if log_callback:
                            log_callback(f"❌ {usuario.nome}: REJEITOU - {motivo}")

            # Verificar se obteve consenso (1/3 dos usuários)
            if favoraveis < necessario:
                if log_callback:
                    log_callback(
                        f"🚫 CONSENSO FALHOU: {favoraveis}/{total_usuarios} votos favoráveis (necessário: {necessario})"
                    )
                print(
                    f"FALHA: Bloco minerado por {bloco.minerador} não obteve consenso."
                )
                return False

        # Atualizar saldos dos usuários envolvidos na transação (se não for genesis)
        if bloco.transacao.remetente != UUID(int=0):
            remetente_usuario = self.usuarios_por_id.get(
                bloco.transacao.remetente, None
            )
            destinatario_usuario = self.usuarios_por_id.get(
                bloco.transacao.destinatario, None
            )

            if remetente_usuario and destinatario_usuario:
                # Verificar novamente o saldo antes de atualizar
                if remetente_usuario.pontos >= bloco.transacao.pontos:
                    remetente_usuario.pontos -= bloco.transacao.pontos
                    destinatario_usuario.pontos += bloco.transacao.pontos
                    if log_callback:
                        log_callback(
                            f"💰 Saldos atualizados: {remetente_usuario.nome} (-{bloco.transacao.pontos:.2f}) → {destinatario_usuario.nome} (+{bloco.transacao.pontos:.2f})"
                        )
                    print(
                        f"Saldos atualizados: {remetente_usuario.nome} (-{bloco.transacao.pontos}) -> {destinatario_usuario.nome} (+{bloco.transacao.pontos})"
                    )
                else:
                    if log_callback:
                        log_callback(
                            f"❌ ERRO: Saldo insuficiente no momento da execução!"
                        )
                    print(f"ERRO: Saldo insuficiente no momento da execução!")
                    return False

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
                raise ValueError(
                    f"Bloco {bloco_atual.id} inválido: hash anterior incorreto"
                )

        print("Blockchain verificada com sucesso! Todos os blocos são válidos.")
