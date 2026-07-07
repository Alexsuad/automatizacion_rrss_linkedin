import re
import unicodedata
from typing import Iterable, Optional

from linkedin_content_system.contracts import EntradaContenido
from linkedin_content_system.contracts.idea_central import IdeaCentral
from linkedin_content_system.contracts.salida import PostCandidato
from linkedin_content_system.contracts.trazabilidad import (
    DiagnosticoTrazabilidad,
    EstadoTrazabilidad,
    HallazgoTrazabilidad,
    TipoHallazgoTrazabilidad,
)


_PATRON_CIFRA = re.compile(r"\b\d+(?:[.,]\d+)?%?")
_PATRONES_AUTORIDAD = (
    "soy experto",
    "somos expertos",
    "somos lideres",
    "somos líderes",
    "lider del mercado",
    "líder del mercado",
    "lideres del mercado",
    "líderes del mercado",
    "referente",
    "certificado",
    "certificada",
    "premiado",
    "premiada",
    "mas de",
    "más de",
)
_PATRONES_ANECDOTA = (
    "me paso",
    "me pasó",
    "nos pasó",
    "cuando trabaje",
    "cuando trabajé",
    "cuando trabajaba",
    "en mi experiencia",
    "un cliente",
    "una cliente",
    "recuerdo que",
)
_PATRONES_PROMESA = (
    "garantiza",
    "garantizado",
    "garantizada",
    "asegura",
    "sin riesgo",
    "resultados garantizados",
    "te prometo",
    "100% seguro",
)
_PATRONES_CLAIM = (
    "estudios demuestran",
    "los datos indican",
    "la mayoría",
    "el mercado confirma",
    "según datos",
    "según estudios",
)
_PATRONES_INFERENCIA_DEBIL = (
    "quizá",
    "quizas",
    "podría",
    "podria",
    "posiblemente",
    "probablemente",
    "tal vez",
    "parece que",
    "puede que",
)
_PATRONES_CONTEXTO_NEGADO = {
    "cifra": ("sin cifras", "sin numeros", "sin números", "no mencionar cifras", "sin datos numéricos", "sin datos numericos"),
    "autoridad": ("sin autoridad", "sin credenciales", "no mencionar autoridad"),
    "anecdota": ("sin anécdotas", "sin anecdotas", "no mencionar experiencia", "sin experiencia personal"),
    "promesa": ("sin promesas", "no prometer", "sin garantías", "sin garantias"),
    "claim": ("sin claims", "sin fuentes", "no citar fuentes", "sin fuente"),
    "hechos": ("sin hechos nuevos", "no inventar", "sin inventar"),
    "datos_reales": ("datos reales", "dato real", "clientes reales", "cliente real", "casos reales", "caso real", "fuente real"),
}
_PALABRAS_VACIAS = {"la", "el", "los", "las", "un", "una", "de", "del", "y", "o"}


def _normalizar(texto: str) -> str:
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    texto_sin_acentos = "".join(
        caracter for caracter in texto_normalizado if not unicodedata.combining(caracter)
    )
    return re.sub(r"\s+", " ", texto_sin_acentos.lower()).strip()


def _sentencias(texto_original: str) -> list[str]:
    return [segmento.strip() for segmento in re.split(r"(?<=[.!?])\s+", texto_original) if segmento.strip()]


def _fragmento_por_patron(texto_original: str, patron: str) -> str:
    patron_normalizado = _normalizar(patron)
    for sentencia in _sentencias(texto_original):
        if patron_normalizado in _normalizar(sentencia):
            return sentencia.strip()
    return texto_original.strip()


def _corpus_soporte(
    entrada: EntradaContenido,
    idea_central: IdeaCentral | str,
    contexto_permitido: Optional[Iterable[str] | str],
) -> str:
    partes: list[str] = [
        entrada.texto_base,
        entrada.intencion_editorial.idea_central or "",
        entrada.intencion_editorial.audiencia_objetivo or "",
        entrada.intencion_editorial.objetivo_del_post or "",
        entrada.intencion_editorial.pilar_contenido or "",
        entrada.intencion_editorial.tipo_de_post or "",
        entrada.intencion_editorial.dolor_o_tension or "",
        entrada.intencion_editorial.cta_intencionado or "",
    ]

    if isinstance(idea_central, IdeaCentral):
        partes.extend(
            [
                idea_central.idea_central,
                idea_central.resumen_operativo,
                *idea_central.puntos_de_soporte,
                *idea_central.limites_de_inferencia,
            ]
        )
    else:
        partes.append(str(idea_central))

    if contexto_permitido is not None:
        if isinstance(contexto_permitido, str):
            partes.append(contexto_permitido)
        else:
            partes.extend(str(item) for item in contexto_permitido)

    return _normalizar(" ".join(partes))


def _soporte_explicito(fragmento: str, corpus: str) -> bool:
    fragmento_normalizado = _normalizar(fragmento)
    if not fragmento_normalizado:
        return False
    if fragmento_normalizado in corpus:
        return True
    tokens = [
        token
        for token in fragmento_normalizado.split()
        if token not in _PALABRAS_VACIAS
    ]
    return bool(tokens) and all(token in corpus for token in tokens)


def _contiene_patron(texto_normalizado: str, patron: str) -> bool:
    return _normalizar(patron) in texto_normalizado


def _agregar_hallazgo(
    hallazgos: list[HallazgoTrazabilidad],
    tipo: TipoHallazgoTrazabilidad,
    fragmento_post: str,
    descripcion: str,
    soporte_encontrado: Optional[str] = None,
) -> None:
    hallazgos.append(
        HallazgoTrazabilidad(
            tipo=tipo,
            fragmento_post=fragmento_post,
            descripcion=descripcion,
            soporte_encontrado=soporte_encontrado,
        )
    )


def resolver_estado_trazabilidad(hallazgos: list[HallazgoTrazabilidad]) -> EstadoTrazabilidad:
    if not hallazgos:
        return EstadoTrazabilidad.PASS
    if any(hallazgo.bloqueante for hallazgo in hallazgos):
        return EstadoTrazabilidad.FAIL
    return EstadoTrazabilidad.WARN


def validar_trazabilidad_fuerte(
    entrada: EntradaContenido,
    idea_central: IdeaCentral | str,
    post: PostCandidato | str,
    contexto_permitido: Optional[Iterable[str] | str] = None,
) -> DiagnosticoTrazabilidad:
    if entrada is None:
        raise ValueError("La entrada no puede ser None.")
    if idea_central is None:
        raise ValueError("La idea central no puede ser None.")
    if post is None:
        raise ValueError("El post no puede ser None.")

    texto_post = post.texto if isinstance(post, PostCandidato) else str(post)
    if not texto_post or not texto_post.strip():
        raise ValueError("El post no puede estar vacío.")

    texto_post_normalizado = _normalizar(texto_post)
    corpus_soporte = _corpus_soporte(entrada, idea_central, contexto_permitido)
    hallazgos: list[HallazgoTrazabilidad] = []

    if contexto_permitido is not None:
        contexto_texto = contexto_permitido if isinstance(contexto_permitido, str) else " ".join(
            str(item) for item in contexto_permitido if item is not None
        )
        contexto_normalizado = _normalizar(contexto_texto)
        if contexto_normalizado:
            for categoria, patrones_contexto in _PATRONES_CONTEXTO_NEGADO.items():
                if not any(_contiene_patron(contexto_normalizado, patron) for patron in patrones_contexto):
                    continue

                if categoria == "cifra" and _PATRON_CIFRA.search(texto_post):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        _fragmento_por_patron(texto_post, _PATRON_CIFRA.search(texto_post).group(0)),
                        "El contexto permitido prohíbe cifras, pero el post las introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "autoridad" and any(_contiene_patron(texto_post_normalizado, patron) for patron in _PATRONES_AUTORIDAD):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        _fragmento_por_patron(texto_post, next(p for p in _PATRONES_AUTORIDAD if _contiene_patron(texto_post_normalizado, p))),
                        "El contexto permitido prohíbe autoridad explícita, pero el post la introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "anecdota" and any(_contiene_patron(texto_post_normalizado, patron) for patron in _PATRONES_ANECDOTA):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        _fragmento_por_patron(texto_post, next(p for p in _PATRONES_ANECDOTA if _contiene_patron(texto_post_normalizado, p))),
                        "El contexto permitido prohíbe anécdotas, pero el post las introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "promesa" and any(_contiene_patron(texto_post_normalizado, patron) for patron in _PATRONES_PROMESA):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        _fragmento_por_patron(texto_post, next(p for p in _PATRONES_PROMESA if _contiene_patron(texto_post_normalizado, p))),
                        "El contexto permitido prohíbe promesas, pero el post las introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "claim" and any(_contiene_patron(texto_post_normalizado, patron) for patron in _PATRONES_CLAIM):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        _fragmento_por_patron(texto_post, next(p for p in _PATRONES_CLAIM if _contiene_patron(texto_post_normalizado, p))),
                        "El contexto permitido prohíbe claims sin fuente, pero el post los introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "hechos" and any(
                    _contiene_patron(texto_post_normalizado, patron)
                    for patron in ("hecho", "hechos", "dato", "datos", "resultado", "resultados", "logro", "logros")
                ):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        texto_post.strip(),
                        "El contexto permitido prohíbe hechos nuevos, pero el post los introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break
                if categoria == "datos_reales" and any(_contiene_patron(texto_post_normalizado, patron) for patron in _PATRONES_CONTEXTO_NEGADO["datos_reales"]):
                    _agregar_hallazgo(
                        hallazgos,
                        TipoHallazgoTrazabilidad.CONTRADICCION_CON_CONTEXTO,
                        texto_post.strip(),
                        "El contexto permitido prohíbe datos o casos reales, pero el post los introduce.",
                        soporte_encontrado=contexto_texto.strip(),
                    )
                    break

    for coincidencia in _PATRON_CIFRA.finditer(texto_post):
        cifra = coincidencia.group(0)
        cifra_normalizada = _normalizar(cifra)
        cifra_sin_porcentaje = cifra_normalizada[:-1] if cifra_normalizada.endswith("%") else cifra_normalizada
        if cifra_normalizada in corpus_soporte or cifra_sin_porcentaje in corpus_soporte:
            continue
        _agregar_hallazgo(
            hallazgos,
            TipoHallazgoTrazabilidad.CIFRA_NO_SOPORTADA,
            _fragmento_por_patron(texto_post, cifra),
            "La cifra o magnitud del post no está soportada por la entrada, la idea central o el contexto permitido.",
        )
        break

    reglas_textuales = (
        (TipoHallazgoTrazabilidad.AUTORIDAD_FINGIDA, _PATRONES_AUTORIDAD, "El post atribuye autoridad, liderazgo o experiencia no soportada."),
        (TipoHallazgoTrazabilidad.ANECDOTA_INVENTADA, _PATRONES_ANECDOTA, "El post introduce una anécdota o experiencia personal no soportada."),
        (TipoHallazgoTrazabilidad.PROMESA_EXCESIVA, _PATRONES_PROMESA, "El post formula una promesa o garantía excesiva no soportada."),
        (TipoHallazgoTrazabilidad.CLAIM_SIN_FUENTE, _PATRONES_CLAIM, "El post invoca un claim o fuente sin soporte explícito."),
    )

    for tipo, patrones, descripcion in reglas_textuales:
        for patron in patrones:
            if not _contiene_patron(texto_post_normalizado, patron):
                continue
            if _soporte_explicito(patron, corpus_soporte):
                continue
            _agregar_hallazgo(
                hallazgos,
                tipo,
                _fragmento_por_patron(texto_post, patron),
                descripcion,
            )
            break

    if not any(h.bloqueante for h in hallazgos):
        for patron in _PATRONES_INFERENCIA_DEBIL:
            if not _contiene_patron(texto_post_normalizado, patron):
                continue
            if _soporte_explicito(patron, corpus_soporte):
                continue
            _agregar_hallazgo(
                hallazgos,
                TipoHallazgoTrazabilidad.INFERENCIA_DEBIL,
                _fragmento_por_patron(texto_post, patron),
                "El post contiene una inferencia débil que requiere revisión humana.",
                soporte_encontrado=None,
            )
            break

    estado = resolver_estado_trazabilidad(hallazgos)
    resumen = {
        EstadoTrazabilidad.PASS: "No se detectaron hallazgos sensibles de trazabilidad.",
        EstadoTrazabilidad.WARN: "Solo se detectaron inferencias débiles.",
        EstadoTrazabilidad.FAIL: "Se detectaron hallazgos sensibles sin soporte suficiente.",
    }[estado]

    return DiagnosticoTrazabilidad(estado=estado, hallazgos=hallazgos, resumen=resumen)
