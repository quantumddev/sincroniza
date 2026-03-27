"""
Dispatcher JSON-RPC 2.0 — núcleo de la capa API.

Registra manejadores de métodos y despacha llamadas JSON-RPC entrantes,
devolviendo siempre una respuesta JSON bien formada.

Códigos de error estándar JSON-RPC:
  -32700  Parse error          — JSON no válido
  -32600  Invalid request      — estructura de la petición incorrecta
  -32601  Method not found     — método no registrado
  -32602  Invalid params       — parámetros incorrectos
  -32603  Internal error       — error inesperado en el manejador

Códigos de error de aplicación:
  -32001  Error de validación
  -32002  Operación en curso   — ya hay un worker activo
  -32003  Plan desactualizado  — fingerprint no coincide
  -32004  Perfil no encontrado
  -32005  Regla inválida
  -32006  Historial no encontrado
  -32007  Operación cancelada
  -32008  Error de filesystem
  -32009  Timeout de operación

Ref: §04_protocolo_jsonrpc.md
"""

from __future__ import annotations

import json
from typing import Any, Callable


# ── Excepciones de aplicación ─────────────────────────────────────────────────

class ErrorAPI(Exception):
    """Error que el manejador puede lanzar para devolver un error JSON-RPC con
    código y datos personalizados."""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


# ── Constantes de error ───────────────────────────────────────────────────────

ERR_PARSE          = -32700
ERR_INVALID_REQ    = -32600
ERR_METHOD_NOT_FND = -32601
ERR_INVALID_PARAMS = -32602
ERR_INTERNAL       = -32603

ERR_VALIDATION     = -32001
ERR_OP_IN_PROGRESS = -32002
ERR_STALE_PLAN     = -32003
ERR_PERFIL_NF      = -32004
ERR_REGLA_INVALID  = -32005
ERR_HISTORIAL_NF   = -32006
ERR_CANCELLED      = -32007
ERR_FILESYSTEM     = -32008
ERR_TIMEOUT        = -32009


# ── Dispatcher ────────────────────────────────────────────────────────────────

class Dispatcher:
    """
    Receptor y enrutador de llamadas JSON-RPC 2.0.

    Uso típico::

        dispatcher = Dispatcher()
        dispatcher.registrar("perfil.listar", lambda params: servicio.listar())
        respuesta_json = dispatcher.despachar('{"jsonrpc":"2.0","id":"1","method":"perfil.listar","params":{}}')
    """

    def __init__(self) -> None:
        self._metodos: dict[str, Callable] = {}

    # ── Registro ──────────────────────────────────────────────────────────────

    def registrar(self, nombre: str, funcion: Callable) -> None:
        """
        Registra un manejador para el método ``nombre``.

        Args:
            nombre:  Nombre del método en formato ``namespace.accion``.
            funcion: Callable que recibe ``params`` (dict) y devuelve el resultado.
        """
        self._metodos[nombre] = funcion

    def metodos_registrados(self) -> list[str]:
        """Devuelve la lista de nombres de métodos registrados."""
        return list(self._metodos.keys())

    # ── Despacho ──────────────────────────────────────────────────────────────

    def despachar(self, json_str: str) -> str:
        """
        Parsea una petición JSON-RPC 2.0, la despacha y devuelve la respuesta.

        Nunca lanza excepciones: siempre devuelve un JSON válido.

        Args:
            json_str: Cadena JSON con la petición.

        Returns:
            Cadena JSON con la respuesta (éxito o error).
        """
        # 1. Parsear JSON
        try:
            req = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return self._error_json(None, ERR_PARSE, "Parse error")

        # 2. Validar estructura de la petición
        request_id = req.get("id") if isinstance(req, dict) else None

        if not isinstance(req, dict):
            return self._error_json(None, ERR_INVALID_REQ, "Invalid Request")
        if req.get("jsonrpc") != "2.0":
            return self._error_json(request_id, ERR_INVALID_REQ, "Invalid Request: jsonrpc must be '2.0'")
        if "method" not in req or not isinstance(req["method"], str):
            return self._error_json(request_id, ERR_INVALID_REQ, "Invalid Request: method is required")

        method = req["method"]
        params = req.get("params", {})
        if not isinstance(params, dict):
            return self._error_json(request_id, ERR_INVALID_PARAMS, "Invalid params: params must be an object")

        # 3. Buscar manejador
        handler = self._metodos.get(method)
        if handler is None:
            return self._error_json(request_id, ERR_METHOD_NOT_FND, f"Method not found: {method}")

        # 4. Ejecutar manejador
        try:
            resultado = handler(params)
        except ErrorAPI as exc:
            return self._error_json(request_id, exc.code, exc.message, exc.data)
        except TypeError as exc:
            return self._error_json(request_id, ERR_INVALID_PARAMS, f"Invalid params: {exc}")
        except Exception as exc:  # noqa: BLE001
            return self._error_json(request_id, ERR_INTERNAL, f"Internal error: {exc}")

        return self._ok_json(request_id, resultado)

    # ── Constructores de respuesta ────────────────────────────────────────────

    def _ok_json(self, request_id: Any, result: Any) -> str:
        """Construye una respuesta de éxito JSON-RPC 2.0."""
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }, ensure_ascii=False)

    def _error_json(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: Any = None,
    ) -> str:
        """Construye una respuesta de error JSON-RPC 2.0."""
        error: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error,
        }, ensure_ascii=False)
