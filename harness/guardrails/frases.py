"""Frases fixas da Seri (spec §6, §7, §9–§13). O modelo não escreve nenhuma destas."""

LIGUE_192 = "Isso pode ser um sinal de alarme. Ligue agora para o SAMU: 192."
BLOQUEIO = "Não posso orientar sobre doses ou troca de remédios. Leve essa dúvida ao farmacêutico ou médico."
INDISPONIVEL = "Estou com um problema técnico agora. Tente de novo em alguns minutos."
LIMITE = "Vou precisar de um pouco mais de informação. Pode me contar de outro jeito?"
NAO_ENTENDI = "Não entendi bem. Você quer falar dos remédios, dos horários, de uma consulta ou de como ela está?"
NAO_OUVI = "Não consegui ouvir. Pode gravar de novo, mais perto do celular?"
JA_RESOLVIDO = "Isso já foi resolvido."
RECUSADO = "Tudo bem, não mudei nada."

# conduta por nível (§9)
CONDUTA_24H = "Isso precisa ser visto por um profissional em até 24 horas."
CONDUTA_OBSERVAR = "Anotei. Se piorar ou aparecer algo novo, me conte na hora."

# leitura (§6)
LEITURA_BAIXA_1 = "Não consegui ler bem {nome}. Pode tirar outra foto, com mais luz e sem dobras?"
LEITURA_BAIXA_2 = "Ainda não consegui ler {nome}. Pode mandar a foto da caixa ou me dizer o nome?"
ILEGIVEL = "Confirme este remédio com o farmacêutico."
NADA_LIDO = "Não encontrei remédios nesta imagem. Pode tirar outra foto, com a receita ou a caixa inteira aparecendo?"
CAIXA_JA_NA_LISTA = "Essa é a caixa de {nome}, que já está na lista."
PROPOSTA = "Encontrei estes remédios. Confira com calma e confirme se está tudo certo."
LISTA_SALVA = "Pronto! A lista foi salva. Os horários já estão na Rotina."
OFERTA_ESTOQUE = "Se quiser que eu avise antes de algum remédio acabar, me diga quantos comprimidos você tem de cada um."

# conciliação (§7)
ESCOPO = "Esta receita é {de_quem}. Ela substitui:"
ESCOPO_ALTA = "Parece uma receita de alta do hospital. Ela substitui:"
ESCOPO_SEM_MEDICO = "Algum remédio da lista é de outro médico?"
RESUMO_CONCILIACAO = "Comparei com a lista de antes: {novos} novo(s), {alterados} com dose ou horário diferente e {ausentes} que não aparece(m) nesta receita."
AUSENTE = "{nome} não está nesta receita. O médico tirou, ou ela continua tomando?"
MESMO_REMEDIO = "Mesmo remédio, com outro nome."
DECISAO = {"continua": "continua na lista", "medico_tirou": "sai da lista, porque o médico tirou",
           "nao_sei": "continua na lista e vira pergunta para a próxima consulta"}

# para que serve (§10)
PARA_QUE_SERVE = "A {nome} costuma ser usada para {uso}. O motivo exato para ela, só o médico que receitou pode dizer."
NA_RECEITA = "Na receita está escrito: {indicacao}."
SEM_INFO = "Ainda não tenho essa informação. O farmacêutico pode explicar para que ele serve."

# alerta (§13.4)
ALERTA = "{descricao}. Fonte: {fonte}. Leve ao farmacêutico ou médico antes de mudar qualquer coisa."

# consulta (§11)
CONSULTA_CONFIRMAR = "Anotei: {profissional}, {quando}. Está certo?"
CONSULTA_SALVA = "Combinado. Na véspera eu preparo uma página com o que levar e perguntar."
CONSULTA_PREPARADA = "Amanhã tem consulta com {profissional} às {hora}. Preparei uma página com os remédios, o que aconteceu e o que perguntar."
POS_CONSULTA = "Como foi a consulta com {profissional}? Pode me mandar um áudio com o que o médico disse. Se ele mudou algum remédio, mande também a foto da receita nova."
RELATO_SALVO = "Anotei o que o médico disse."
RELATO_RECEITA = "Para eu atualizar a lista, mande a foto da receita nova. Até lá, a lista continua como está."

# estoque e receita (§12)
ESTOQUE_ACABANDO = "A {nome} deve acabar por volta de {dia}."
RECEITA_VENCENDO = "A receita da {nome} vence em {dia}. Se ela for continuar, peça uma receita nova ao médico."
FARMACIA_POPULAR = "Pelo programa Farmácia Popular, a {nome} sai de graça nas farmácias credenciadas. Leve {documentos}."
OUTRA_MARCA = "A farmácia pode entregar outra marca do mesmo remédio. Confirme com o farmacêutico."
ESTOQUE_REGISTRADO = "Anotei: {quantidade} de {nome}."


def juntar(itens: list[str]) -> str:
    if len(itens) <= 1:
        return "".join(itens)
    return ", ".join(itens[:-1]) + " e " + itens[-1]
