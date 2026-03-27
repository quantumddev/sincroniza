"""
Tests de LogServicio.
"""

from __future__ import annotations

import pytest

from app.models.enums import NivelLog
from app.models.evento_log import EventoLog
from app.services.log import LogServicio


class TestLogServicioEmitir:
    def test_info_retorna_evento(self) -> None:
        svc = LogServicio()
        ev = svc.info("analisis.inicio", "Iniciando análisis")
        assert ev.nivel == NivelLog.INFO
        assert ev.tipo == "analisis.inicio"
        assert ev.mensaje == "Iniciando análisis"
        assert ev.datos is None

    def test_warning_retorna_evento(self) -> None:
        svc = LogServicio()
        ev = svc.warning("regla.skip", "Regla sin coincidencias")
        assert ev.nivel == NivelLog.WARNING

    def test_error_retorna_evento(self) -> None:
        svc = LogServicio()
        ev = svc.error("fs.permiso", "Acceso denegado", {"ruta": "C:/secreto"})
        assert ev.nivel == NivelLog.ERROR
        assert ev.datos == {"ruta": "C:/secreto"}

    def test_timestamp_generado(self) -> None:
        svc = LogServicio()
        ev = svc.info("x", "y")
        assert "T" in ev.timestamp  # formato ISO 8601

    def test_retorna_instancia_evento_log(self) -> None:
        svc = LogServicio()
        ev = svc.info("tipo", "msg")
        assert isinstance(ev, EventoLog)


class TestLogServicioAcumulacion:
    def test_acumula_eventos(self) -> None:
        svc = LogServicio()
        svc.info("a", "msg1")
        svc.warning("b", "msg2")
        svc.error("c", "msg3")
        assert svc.contar() == 3

    def test_obtener_todos_retorna_copia(self) -> None:
        svc = LogServicio()
        svc.info("t", "m")
        lista = svc.obtener_todos()
        lista.clear()
        assert svc.contar() == 1  # el original no se modificó

    def test_obtener_todos_orden_cronologico(self) -> None:
        svc = LogServicio()
        svc.info("t", "primero")
        svc.info("t", "segundo")
        todos = svc.obtener_todos()
        assert todos[0].mensaje == "primero"
        assert todos[1].mensaje == "segundo"

    def test_vaciar_borra_eventos(self) -> None:
        svc = LogServicio()
        svc.info("t", "m")
        svc.vaciar()
        assert svc.contar() == 0

    def test_contar_inicial_cero(self) -> None:
        assert LogServicio().contar() == 0


class TestLogServicioCallback:
    def test_callback_invocado_en_info(self) -> None:
        recibidos: list[EventoLog] = []
        svc = LogServicio(callback=recibidos.append)
        svc.info("t", "mensaje")
        assert len(recibidos) == 1
        assert recibidos[0].nivel == NivelLog.INFO

    def test_callback_invocado_en_error(self) -> None:
        recibidos: list[EventoLog] = []
        svc = LogServicio(callback=recibidos.append)
        svc.error("t", "error grave")
        assert recibidos[0].nivel == NivelLog.ERROR

    def test_sin_callback_no_falla(self) -> None:
        svc = LogServicio()  # callback=None
        svc.info("t", "m")  # no debe lanzar excepción

    def test_callback_recibe_todos_los_niveles(self) -> None:
        recibidos: list[EventoLog] = []
        svc = LogServicio(callback=recibidos.append)
        svc.info("t", "i")
        svc.warning("t", "w")
        svc.error("t", "e")
        niveles = {ev.nivel for ev in recibidos}
        assert niveles == {NivelLog.INFO, NivelLog.WARNING, NivelLog.ERROR}

    def test_establecer_callback_posterior(self) -> None:
        recibidos: list[EventoLog] = []
        svc = LogServicio()
        svc.info("t", "antes del callback")
        svc.establecer_callback(recibidos.append)
        svc.info("t", "despues del callback")
        assert len(recibidos) == 1
        assert recibidos[0].mensaje == "despues del callback"

    def test_establecer_callback_none_desactiva(self) -> None:
        recibidos: list[EventoLog] = []
        svc = LogServicio(callback=recibidos.append)
        svc.establecer_callback(None)
        svc.info("t", "m")
        assert len(recibidos) == 0

    def test_evento_acumulado_aunque_falle_callback(self) -> None:
        def callback_roto(ev: EventoLog) -> None:
            raise RuntimeError("callback falla")

        svc = LogServicio(callback=callback_roto)
        with pytest.raises(RuntimeError):
            svc.info("t", "m")
        # El evento sí quedó en memoria antes de invocar el callback
        assert svc.contar() == 1
