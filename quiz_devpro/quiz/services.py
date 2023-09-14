import redis
from dataclasses import dataclass

from django.conf import settings

_redis_client = redis.Redis.from_url(settings.REDIS_URL)
CLASSIFICACAO_KEY = "devpro:classificacao"


def salvar_pontos(aluno, pontos) -> None:
    _redis_client.zadd(
        CLASSIFICACAO_KEY,
        {f"{aluno.pk}:{aluno.nome}": pontos},
        incr=True,
    )


@dataclass(frozen=True)
class Aluno:
    nome: str
    pontos: int
    posicao_ranking: int


def classificacao(top=5) -> list[Aluno]:
    result = _redis_client.zrevrange(
        CLASSIFICACAO_KEY,
        0,
        top - 1,
        withscores=True,
        score_cast_func=int,
    )
    ranking = []
    for posicao, (membro, pontos) in enumerate(result, start=1):
        _, aluno_nome = membro.decode().split(":")
        ranking.append(
            Aluno(nome=aluno_nome, pontos=pontos, posicao_ranking=posicao),
        )

    return ranking


def get_posicao(aluno) -> tuple[int, int]:
    result = _redis_client.zrevrank(
        CLASSIFICACAO_KEY,
        f"{aluno.pk}:{aluno.nome}",
        withscore=True,
    )
    if result:
        posicao, pontos = result
    else:
        posicao = _redis_client.zcount(CLASSIFICACAO_KEY, min=0, max=float("+inf"))
        pontos = 0

    return posicao + 1, int(pontos)
