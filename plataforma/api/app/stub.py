import re

from app import db

ALARME = re.compile(
    r"queda|bateu a cabe[cç]a|batida na cabe[cç]a|dor no peito|falta de ar|confus[aã]o",
    re.IGNORECASE,
)

TEXTO_LEMBRETE = (
    "Hora de olhar a lista de remédios. A dose é a da receita que você confirmou. "
    "A Seriema não escolhe dose."
)


def estado(conta_id: int) -> dict:
    lista = db.lista_atual(conta_id)
    return {
        "mensagens": db.listar_mensagens(conta_id),
        "lembrete": db.lembrete_aberto(conta_id),
        "pode_confirmar": bool(lista and not lista["confirmada"]),
        "lista": lista,
    }


def tratar(conta_id: int, texto: str, arquivo: dict | None) -> dict:
    db.garantir_boas_vindas(conta_id)
    texto = texto.strip()
    tipo_usuario = arquivo["tipo"] if arquivo else "texto"
    if not texto and arquivo is None:
        raise ValueError("vazio")

    legenda = texto
    if not legenda:
        legenda = {"foto": "Enviei uma foto.", "pdf": "Enviei um PDF.", "audio": "Enviei um áudio."}[
            tipo_usuario
        ]
    db.adicionar_mensagem(
        conta_id,
        "cuidadora",
        tipo_usuario,
        legenda,
        arquivo["id"] if arquivo else None,
    )

    if texto and ALARME.search(texto):
        db.adicionar_mensagem(
            conta_id,
            "agente",
            "alarme",
            "Isso pode ser sinal de alarme. Ligue 192 agora. A Seriema não avalia emergência.",
            extra={"acoes": [{"id": "ligar_192", "rotulo": "Ligar 192"}]},
        )
        return estado(conta_id)

    if arquivo and arquivo["tipo"] in {"foto", "pdf"}:
        lista = db.criar_lista_demo(conta_id)
        db.adicionar_mensagem(
            conta_id,
            "agente",
            "lista",
            "Separei uma lista para você conferir. A leitura automática da foto ainda não está ligada: esta é a lista da demonstração. Nada entra na rotina até você confirmar.",
            extra={"itens": lista["itens"], "alertas": lista["alertas"], "acoes": []},
        )
        return estado(conta_id)

    if arquivo and arquivo["tipo"] == "audio":
        db.adicionar_mensagem(
            conta_id,
            "agente",
            "resumo",
            "Guardei o áudio do dia e montei um resumo para a consulta. Quem decide é o profissional. O áudio ainda não é transcrito.",
            extra={"acoes": [{"id": "baixar_resumo", "rotulo": "Baixar resumo em PDF"}]},
        )
        return estado(conta_id)

    if texto.lower() in {"confirmo", "confirmo a lista"}:
        return _confirmar(conta_id)

    db.adicionar_mensagem(
        conta_id,
        "agente",
        "texto",
        "Pode mandar a foto da receita, da caixa ou um PDF. Se a lista já apareceu, toque em Confirmar lista. Um áudio do dia gera o resumo. Eu não sugiro dose, troca nem suspensão.",
    )
    return estado(conta_id)


def confirmar(conta_id: int) -> dict:
    db.garantir_boas_vindas(conta_id)
    db.adicionar_mensagem(conta_id, "cuidadora", "texto", "Confirmo a lista.")
    return _confirmar(conta_id)


def _confirmar(conta_id: int) -> dict:
    if not db.confirmar_lista_atual(conta_id):
        db.adicionar_mensagem(
            conta_id,
            "agente",
            "texto",
            "Ainda não há lista nova para confirmar. Mande a foto da receita, da caixa ou o PDF.",
        )
        return estado(conta_id)
    db.criar_lembrete(conta_id, TEXTO_LEMBRETE)
    db.adicionar_mensagem(
        conta_id,
        "agente",
        "lembrete",
        "Lista confirmada. O lembrete está na tela. Nada mudou sem o seu ok.",
    )
    return estado(conta_id)
