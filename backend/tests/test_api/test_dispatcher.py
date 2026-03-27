"""
Tests de integración para el Dispatcher JSON-RPC 2.0.

Verifica:
  - Estructura de respuestas de éxito y error.
  - Enrutamiento correcto a los manejadores registrados.
  - Manejo de errores: parse error, invalid request, method not found,
    invalid params, internal error y errores de aplicación (ErrorAPI).
  - Métodos sin parámetros y con parámetros.
  - Respuesta con id correcto en todos los casos.

Ref: §04_protocolo_jsonrpc.md, Fase 5 (tarea 5.6)
"""

from __future__ import annotations

import json

import pytest

from app.api.dispatcher import (
    ERR_INTERNAL,
    ERR_INVALID_PARAMS,
    ERR_INVALID_REQ,
    ERR_METHOD_NOT_FND,
    ERR_OP_IN_PROGRESS,
    ERR_PARSE,
    ERR_PERFIL_NF,
    ERR_VALIDATION,
    Dispatcher,
    ErrorAPI,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def dispatcher() -> Dispatcher:
    """Dispatcher con algunos métodos de ejemplo registrados."""
    d = Dispatcher()

    d.registrar("echo", lambda params: {"echo": params.get("msg", "")})
    d.registrar("sumar", lambda params: {"suma": params["a"] + params["b"]})
    d.registrar("sin_params", lambda params: {"ok": True})
    d.registrar("lanzar_error_api", lambda params: _raise(ErrorAPI(ERR_VALIDATION, "Validación fallida", {"campo": "nombre"})))
    d.registrar("lanzar_excepcion", lambda params: _raise(RuntimeError("boom")))
    d.registrar("lanzar_type_error", lambda params: _raise(TypeError("bad arg")))

    return d


def _raise(exc: Exception):
    raise exc


def _dispatch(dispatcher: Dispatcher, payload: dict) -> dict:
    """Helper: despacha un payload y parsea la respuesta JSON."""
    respuesta = dispatcher.despachar(json.dumps(payload))
    return json.loads(respuesta)


# ── Estructura básica de respuesta ────────────────────────────────────────────

class TestEstructuraRespuesta:
    def test_respuesta_exito_tiene_jsonrpc_version(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "sin_params", "params": {}})
        assert r["jsonrpc"] == "2.0"

    def test_respuesta_exito_tiene_id(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "abc", "method": "sin_params", "params": {}})
        assert r["id"] == "abc"

    def test_respuesta_exito_tiene_result(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "sin_params", "params": {}})
        assert "result" in r
        assert "error" not in r

    def test_respuesta_error_tiene_jsonrpc_version(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "no_existe", "params": {}})
        assert r["jsonrpc"] == "2.0"

    def test_respuesta_error_tiene_id(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "xyz", "method": "no_existe", "params": {}})
        assert r["id"] == "xyz"

    def test_respuesta_error_tiene_error_object(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "no_existe", "params": {}})
        assert "error" in r
        assert "result" not in r

    def test_error_object_tiene_code_y_message(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "no_existe", "params": {}})
        assert "code" in r["error"]
        assert "message" in r["error"]


# ── Enrutamiento correcto ─────────────────────────────────────────────────────

class TestEnrutamiento:
    def test_echo_devuelve_mensaje(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "echo", "params": {"msg": "hola"}})
        assert r["result"] == {"echo": "hola"}

    def test_sumar_calcula_correctamente(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "2", "method": "sumar", "params": {"a": 3, "b": 4}})
        assert r["result"]["suma"] == 7

    def test_sin_params_funciona_con_dict_vacio(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "3", "method": "sin_params", "params": {}})
        assert r["result"] == {"ok": True}

    def test_sin_params_funciona_sin_campo_params(self, dispatcher):
        """params es opcional en JSON-RPC; debe usarse {} por defecto."""
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "4", "method": "sin_params"})
        assert r["result"] == {"ok": True}

    def test_id_numerico(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": 42, "method": "sin_params", "params": {}})
        assert r["id"] == 42

    def test_id_nulo(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": None, "method": "sin_params", "params": {}})
        assert r["id"] is None


# ── Errores estándar JSON-RPC ─────────────────────────────────────────────────

class TestErroresParse:
    def test_json_invalido_devuelve_parse_error(self, dispatcher):
        r = json.loads(dispatcher.despachar("{no es json}"))
        assert r["error"]["code"] == ERR_PARSE

    def test_parse_error_tiene_id_nulo(self, dispatcher):
        r = json.loads(dispatcher.despachar("no_json"))
        assert r["id"] is None

    def test_cadena_vacia_devuelve_parse_error(self, dispatcher):
        r = json.loads(dispatcher.despachar(""))
        assert r["error"]["code"] == ERR_PARSE

    def test_json_valido_pero_no_objeto(self, dispatcher):
        """Un array JSON no es una petición válida."""
        r = json.loads(dispatcher.despachar("[1, 2, 3]"))
        assert r["error"]["code"] in (ERR_PARSE, ERR_INVALID_REQ)


class TestErroresInvalidRequest:
    def test_falta_jsonrpc_field(self, dispatcher):
        r = _dispatch(dispatcher, {"id": "1", "method": "echo", "params": {}})
        assert r["error"]["code"] == ERR_INVALID_REQ

    def test_jsonrpc_version_incorrecta(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "1.0", "id": "1", "method": "echo", "params": {}})
        assert r["error"]["code"] == ERR_INVALID_REQ

    def test_falta_method_field(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "params": {}})
        assert r["error"]["code"] == ERR_INVALID_REQ

    def test_params_no_objeto(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "echo", "params": [1, 2]})
        assert r["error"]["code"] == ERR_INVALID_PARAMS


class TestErroresMethodNotFound:
    def test_metodo_inexistente(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "no.existe", "params": {}})
        assert r["error"]["code"] == ERR_METHOD_NOT_FND

    def test_message_menciona_el_metodo(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "perfil.xxx", "params": {}})
        assert "perfil.xxx" in r["error"]["message"]

    def test_id_se_preserva_en_method_not_found(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "mi-id", "method": "x.y", "params": {}})
        assert r["id"] == "mi-id"


class TestErroresInvalidParams:
    def test_tipo_error_en_manejador_devuelve_invalid_params(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "lanzar_type_error", "params": {}})
        assert r["error"]["code"] == ERR_INVALID_PARAMS

    def test_params_como_array_devuelve_invalid_params(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "echo", "params": [1, 2]})
        assert r["error"]["code"] == ERR_INVALID_PARAMS


class TestErroresInternal:
    def test_excepcion_inesperada_devuelve_internal_error(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "lanzar_excepcion", "params": {}})
        assert r["error"]["code"] == ERR_INTERNAL

    def test_id_se_preserva_en_internal_error(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "err-id", "method": "lanzar_excepcion", "params": {}})
        assert r["id"] == "err-id"


# ── Errores de aplicación (ErrorAPI) ─────────────────────────────────────────

class TestErroresAPI:
    def test_error_api_propaga_code(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "lanzar_error_api", "params": {}})
        assert r["error"]["code"] == ERR_VALIDATION

    def test_error_api_propaga_message(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "lanzar_error_api", "params": {}})
        assert r["error"]["message"] == "Validación fallida"

    def test_error_api_propaga_data(self, dispatcher):
        r = _dispatch(dispatcher, {"jsonrpc": "2.0", "id": "1", "method": "lanzar_error_api", "params": {}})
        assert r["error"]["data"] == {"campo": "nombre"}

    def test_error_api_sin_data_no_incluye_data_key(self, dispatcher):
        d = Dispatcher()
        d.registrar("sin_data", lambda params: _raise(ErrorAPI(ERR_PERFIL_NF, "no hallado")))
        r = _dispatch(d, {"jsonrpc": "2.0", "id": "1", "method": "sin_data", "params": {}})
        assert "data" not in r["error"]


# ── Registro de métodos ───────────────────────────────────────────────────────

class TestRegistro:
    def test_metodos_registrados_listados(self, dispatcher):
        metodos = dispatcher.metodos_registrados()
        assert "echo" in metodos
        assert "sumar" in metodos

    def test_dispatcher_vacio_devuelve_lista_vacia(self):
        d = Dispatcher()
        assert d.metodos_registrados() == []

    def test_registrar_sobreescribe_metodo(self):
        d = Dispatcher()
        d.registrar("m", lambda p: "v1")
        d.registrar("m", lambda p: "v2")
        r = _dispatch(d, {"jsonrpc": "2.0", "id": "1", "method": "m", "params": {}})
        assert r["result"] == "v2"


# ── Respuesta siempre es JSON válido ─────────────────────────────────────────

class TestRespuestaEsJSONValido:
    def test_siempre_devuelve_json_valido_en_error_de_parse(self, dispatcher):
        respuesta = dispatcher.despachar("!!!!")
        parsed = json.loads(respuesta)  # no debe lanzar
        assert parsed is not None

    def test_siempre_devuelve_json_valido_en_internal_error(self, dispatcher):
        respuesta = dispatcher.despachar(
            json.dumps({"jsonrpc": "2.0", "id": "1", "method": "lanzar_excepcion", "params": {}})
        )
        parsed = json.loads(respuesta)
        assert parsed is not None

    def test_resultado_es_cadena(self, dispatcher):
        resultado = dispatcher.despachar(
            json.dumps({"jsonrpc": "2.0", "id": "1", "method": "echo", "params": {"msg": "test"}})
        )
        assert isinstance(resultado, str)
