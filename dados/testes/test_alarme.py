import pytest

from dados.gravidade import detectar_alarme

# Variações da spec dados §7.1 (e outras formas comuns de fala).
COM_ALARME = [
    ("alarme_queda_cabeca", "ela caiu no banheiro e bateu a cabeça"),
    ("alarme_queda_cabeca", "bateu com a cabeça"),
    ("alarme_queda_cabeca", "levou um tombo e bateu a cabeça"),
    ("alarme_queda_cabeca", "escorregou e machucou a cabeça"),
    ("alarme_queda_cabeca", "Caiu da cama e bateu a cabeça no chão"),
    ("alarme_dor_peito", "dor no peito"),
    ("alarme_dor_peito", "aperto no peito"),
    ("alarme_dor_peito", "dor forte no peito"),
    ("alarme_dor_peito", "o peito está doendo"),
    ("alarme_dor_peito", "reclamou de uma pressão no peito"),
    ("alarme_falta_ar", "falta de ar"),
    ("alarme_falta_ar", "não consegue respirar"),
    ("alarme_falta_ar", "respirando com dificuldade"),
    ("alarme_falta_ar", "sem ar"),
    ("alarme_falta_ar", "ficou ofegante depois de andar"),
    ("alarme_confusao", "ficou confuso de repente"),
    ("alarme_confusao", "não reconhece ninguém"),
    ("alarme_confusao", "falando coisa sem sentido"),
    ("alarme_confusao", "está desorientada desde cedo"),
]

SEM_ALARME = [
    "dor de cabeça forte",
    "dor nas costas",
    "tomou o remédio e está bem",
    "teve tontura de manhã",
    "bateu o pé na mesa",
    "sem arroz em casa",
    "caiu a pressão e tem dor de cabeça",
    "",
]

# DA-D2 (conservador): negação NÃO desliga o alarme. O falso alarme só mostra um cartão
# que a cuidadora pode ignorar; perder um alarme verdadeiro custa muito mais.
COM_NEGACAO = [
    ("alarme_dor_peito", "não teve dor no peito"),
    ("alarme_dor_peito", "não sei se é dor no peito, mas está apertando"),
    ("alarme_falta_ar", "sem falta de ar hoje"),
    ("alarme_queda_cabeca", "não bateu a cabeça"),
    ("alarme_confusao", "não está confusa"),
]


@pytest.mark.parametrize("regra,texto", COM_ALARME + COM_NEGACAO)
def test_dispara_o_192(regra, texto):
    conduta = detectar_alarme(texto)
    assert conduta is not None, texto
    assert conduta.nivel == "ligue_192"
    assert conduta.regra_id == regra
    assert conduta.motivo and conduta.fonte


@pytest.mark.parametrize("texto", SEM_ALARME)
def test_nao_dispara(texto):
    assert detectar_alarme(texto) is None


def test_acento_e_maiuscula_nao_importam():
    assert detectar_alarme("DOR NO PEITO!!!").regra_id == "alarme_dor_peito"
    assert detectar_alarme("Falta de AR").regra_id == "alarme_falta_ar"


def test_os_quatro_sinais_existem():
    regras = {r for r, _ in COM_ALARME}
    assert regras == {"alarme_queda_cabeca", "alarme_dor_peito", "alarme_falta_ar", "alarme_confusao"}


# Frases que a revisão independente (subagente Sonnet 5.5) apontou como falsos negativos.
FALSOS_NEGATIVOS = {
    "alarme_queda_cabeca": [
        "caiu e está com um galo na cabeça", "caiu e saiu sangue da cabeça",
        "ele caiu e ficou com a cabeça machucada", "bateu a nuca no chão quando caiu",
        "meu pai caiu hoje de manhã, bateu a testa no armário", "caiu no chuveiro e deu uma cabeçada na parede",
        "ele escorregou e bateu o crânio no chão",
    ],
    "alarme_dor_peito": [
        "ela está com o peito apertado", "reclama que o peito está pesado", "dor torácica",
        "está sentindo dor no tórax", "ela diz que o coração está doendo", "sente um aperto no coração",
        "uma facada no peito",
    ],
    "alarme_falta_ar": [
        "a vó está cansada pra respirar", "respiração curta e rápida", "ele tá puxando o ar com força",
        "ela está respirando muito rápido", "a respiração dela está pesada", "ficou com a boca roxa e sem fôlego",
        "tá sem fôlego até sentada", "está com chiado no peito e cansada pra respirar", "ele fica arfando",
        "minha vó está com a respiração difícil", "parece que o ar não entra", "o vô está respirando mal",
        "ela está com um barulho no peito pra respirar", "ele está respirando pela boca, com esforço",
    ],
    "alarme_confusao": [
        "a vó não conhece mais os filhos", "ele não sabe onde está", "ela perguntou quem eu era",
        "ela não sabe que dia é hoje de repente", "ele está muito perdido, não sabe onde está",
        "vovô acordou todo atrapalhado, falando coisa com coisa", "minha mãe começou a ver coisas que não existem",
        "a vó ficou desnorteada", "ele está variando", "tá variando da cabeça desde cedo",
        "não reconhece a própria casa", "ficou esquisito, não responde direito e olha pro nada",
        "começou a falar bobagem de repente", "está dizendo coisas sem pé nem cabeça",
        "ele não me reconheceu hoje", "acordou perdida, não sabe onde está",
    ],
}

# Emergências comuns em idosos que não estavam na lista de 4 sinais (acrescentadas por C após a revisão).
EXTRAS = {
    "alarme_avc": ["a boca ficou torta", "a fala está enrolada", "o braço ficou caído", "sente fraqueza do lado direito",
                   "a pior dor de cabeça da vida", "perdeu a visão de repente"],
    "alarme_desmaio": ["ela desmaiou", "teve uma convulsão", "apagou na cadeira", "não acorda"],
    "alarme_sangramento_grave": ["vomitou sangue", "está tossindo sangue", "o nariz não para de sangrar",
                                 "fezes pretas e muita tontura"],
}

# Frases comuns sem relação; antes disparavam por engano.
FALSOS_POSITIVOS = [
    "sem ar condicionado no quarto", "sem ar no pneu da cadeira de rodas", "foi um sufoco de manhã com o trânsito",
    "o calor está sufocante", "ela ficou confusa com o troco do mercado", "confusa com o controle da tv",
    "a conta de luz está sem sentido", "ele bateu palmas e balançou a cabeça", "a porta bateu e ela balançou a cabeça",
    "bateu a mão na mesa e a cabeça dela doeu", "dor no peito do pé", "dor de barriga, comeu peito de frango",
]


@pytest.mark.parametrize("regra,texto", [(r, t) for r, ts in {**FALSOS_NEGATIVOS, **EXTRAS}.items() for t in ts])
def test_frases_da_revisao_disparam(regra, texto):
    conduta = detectar_alarme(texto)
    assert conduta is not None and conduta.nivel == "ligue_192", texto


@pytest.mark.parametrize("texto", FALSOS_POSITIVOS)
def test_falsos_positivos_da_revisao_nao_disparam(texto):
    assert detectar_alarme(texto) is None, texto
