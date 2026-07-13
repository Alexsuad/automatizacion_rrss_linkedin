from __future__ import annotations

from typing import Protocol

from linkedin_content_system.contracts import (
    AuditoriaEditorial,
    EstadoAuditoriaEditorial,
    FuenteTextualNormalizada,
    HallazgoEditorial,
    SeveridadHallazgoEditorial,
)
from linkedin_content_system.use_cases.flujo_textual_runtime import PerfilNarrativoRuntime


class RevisorEditorial(Protocol):
    def revisar(
        self, fuente: FuenteTextualNormalizada, perfil: PerfilNarrativoRuntime, texto_post: str
    ) -> AuditoriaEditorial: ...


class RevisorEditorialDeterminista:
    """Auditor inyectable: solo afirma lo que puede comprobar localmente."""

    _MARCAS_GENERICAS = ("en un mundo donde",)

    def revisar(self, fuente, perfil, texto_post):
        texto = (texto_post or "").strip()
        texto_normalizado = texto.lower()
        hallazgos: list[HallazgoEditorial] = []
        if not texto:
            hallazgos.append(HallazgoEditorial(categoria="cierre", severidad=SeveridadHallazgoEditorial.CRITICA, explicacion="La candidata está vacía.", requiere_regeneracion=True, instruccion_correccion="Genera un post completo."))
        if any(marca in texto_normalizado for marca in self._MARCAS_GENERICAS):
            hallazgos.append(HallazgoEditorial(categoria="genericidad", severidad=SeveridadHallazgoEditorial.MAYOR, fragmento=texto[:120], explicacion="La apertura usa una fórmula genérica.", requiere_regeneracion=True, instruccion_correccion="Abre con un hecho autorizado concreto, sin fórmulas genéricas."))
        if perfil.frases_prohibidas and any(frase.lower() in texto_normalizado for frase in perfil.frases_prohibidas):
            hallazgos.append(HallazgoEditorial(categoria="voz", severidad=SeveridadHallazgoEditorial.MAYOR, explicacion="La candidata usa una frase prohibida por el perfil.", requiere_regeneracion=True, instruccion_correccion="Elimina la frase prohibida y respeta el tono del perfil."))
        if fuente.no_inferir and any(item.lower() in texto_normalizado for item in fuente.no_inferir):
            hallazgos.append(HallazgoEditorial(categoria="afirmacion_sin_soporte", severidad=SeveridadHallazgoEditorial.CRITICA, explicacion="La candidata afirma un elemento prohibido de inferir.", requiere_regeneracion=False, referencias_evidencia=fuente.no_inferir))
        if fuente.elementos_pendientes and any(item.lower() in texto_normalizado for item in fuente.elementos_pendientes):
            hallazgos.append(HallazgoEditorial(categoria="afirmacion_pendiente", severidad=SeveridadHallazgoEditorial.MAYOR, explicacion="La candidata usa una afirmación pendiente de confirmación.", requiere_regeneracion=True, instruccion_correccion="Elimina o reformula la afirmación pendiente.", referencias_evidencia=fuente.elementos_pendientes))
        if texto and not texto.endswith((".", "?", "!", "…")):
            hallazgos.append(HallazgoEditorial(categoria="cierre", severidad=SeveridadHallazgoEditorial.MAYOR, explicacion="La candidata no tiene cierre completo.", requiere_regeneracion=True, instruccion_correccion="Completa el cierre con una oración terminada."))
        if texto and "?" not in texto:
            hallazgos.append(HallazgoEditorial(categoria="CTA", severidad=SeveridadHallazgoEditorial.MENOR, explicacion="No se puede confirmar un CTA interrogativo.", incertidumbre="El contrato puede no requerir CTA en todos los casos."))
        if any(h.severidad == SeveridadHallazgoEditorial.CRITICA for h in hallazgos):
            estado = EstadoAuditoriaEditorial.FAIL
        elif any(h.severidad == SeveridadHallazgoEditorial.MAYOR for h in hallazgos):
            estado = EstadoAuditoriaEditorial.WARN
        else:
            estado = EstadoAuditoriaEditorial.PASS
        return AuditoriaEditorial(
            estado=estado,
            hallazgos=hallazgos,
            limites=["Voz, naturalidad y fidelidad semántica completa requieren revisión humana."],
        )


# Alias de compatibilidad para consumidores del Incremento 1 ya existente.
RevisorEditorialConservador = RevisorEditorialDeterminista
