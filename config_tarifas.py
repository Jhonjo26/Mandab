# config_tarifas.py
# Motor de negocio Mandabike — General Pico, La Pampa
# Fuente única de verdad para reglas tarifarias.

from enum import Enum
from dataclasses import dataclass


# ──────────────────────────────────────────────
# ENUMS: contratos de tipo, no strings libres
# ──────────────────────────────────────────────

class Zona(str, Enum):
    """
    Zonas geográficas de General Pico.
    Delimitadas por Ruta Prov. 1, Ruta Prov. 101 y Av. Circunvalación.
    """
    CENTRO = "Centro"
    PERIFERIA = "Periferia"


class TipoMandado(str, Enum):
    """
    Tipos de servicio disponibles.
    Extender aquí cuando se agreguen nuevos mandados (farmacia, trámite, etc.)
    """
    MANDADO_COMUN = "Mandado Común"
    DEPOSITO_BANCARIO = "Depósito Bancario"


# ──────────────────────────────────────────────
# CONSTANTES TARIFARIAS (skill 1 + skill 2)
# ──────────────────────────────────────────────

PRECIO_CENTRO: int = 5_000          # Tarifa plana zona Centro
PRECIO_PERIFERIA: int = 7_500       # Tarifa plana zona Periferia
LIMITE_DEPOSITO: float = 1_000_000  # Umbral que activa el porcentaje
PORCENTAJE_DEPOSITO: float = 0.005  # 0.5% sobre el monto total


# ──────────────────────────────────────────────
# RESULTADO: objeto con tarifa + contexto
# (la UI necesita saber POR QUÉ es ese precio)
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class TarifaResultado:
    """
    Resultado inmutable del cálculo tarifario.

    Atributos:
        tarifa (int): Costo final del servicio en pesos.
        regla_aplicada (str): Descripción legible de la regla que determinó el precio.
        zona (Zona): Zona geográfica del viaje.
        tipo_mandado (TipoMandado): Tipo de servicio solicitado.
    """
    tarifa: int
    regla_aplicada: str
    zona: Zona
    tipo_mandado: TipoMandado

    def formatear_tarifa(self) -> str:
        """Devuelve la tarifa formateada para mostrar en UI. Ej: '$5.000'"""
        return f"${self.tarifa:,.0f}".replace(",", ".")


# ──────────────────────────────────────────────
# FUNCIONES INTERNAS (una responsabilidad cada una)
# ──────────────────────────────────────────────

def _validar_monto(monto: float) -> None:
    """
    Falla ruidosamente si el monto es inválido.
    Silenciar errores de entrada genera tarifas incorrectas en producción.
    """
    if not isinstance(monto, (int, float)):
        raise TypeError(f"monto_efectivo debe ser numérico, recibido: {type(monto)}")
    if monto < 0:
        raise ValueError(f"monto_efectivo no puede ser negativo: {monto}")


def _precio_base(zona: Zona) -> int:
    """
    Devuelve la tarifa plana según zona.
    Separado para poder usarlo en validaciones o UI sin ejecutar toda la lógica.
    """
    precios = {
        Zona.CENTRO: PRECIO_CENTRO,
        Zona.PERIFERIA: PRECIO_PERIFERIA,
    }
    return precios[zona]


# ──────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────

def calcular_tarifa_servicio(
    tipo_mandado: TipoMandado,
    zona: Zona,
    monto_efectivo: float = 0.0,
) -> TarifaResultado:
    """
    Calcula el costo exacto del servicio Mandabike.

    Reglas (skill 2):
      - Mandado Común: tarifa plana por zona, sin importar monto.
      - Depósito Bancario ≤ $1.000.000: igual que mandado común.
      - Depósito Bancario > $1.000.000: 0.5% del monto total.

    Args:
        tipo_mandado: TipoMandado.MANDADO_COMUN | TipoMandado.DEPOSITO_BANCARIO
        zona:         Zona.CENTRO | Zona.PERIFERIA
        monto_efectivo: Monto en pesos a depositar (solo aplica en DEPOSITO_BANCARIO)

    Returns:
        TarifaResultado con tarifa final, regla aplicada y contexto.

    Raises:
        TypeError: Si monto_efectivo no es numérico.
        ValueError: Si monto_efectivo es negativo.
    """
    _validar_monto(monto_efectivo)

    base = _precio_base(zona)

    if tipo_mandado == TipoMandado.DEPOSITO_BANCARIO and monto_efectivo > LIMITE_DEPOSITO:
        tarifa = int(monto_efectivo * PORCENTAJE_DEPOSITO)
        regla = f"0.5% sobre ${monto_efectivo:,.0f} (depósito mayor al límite)".replace(",", ".")
    else:
        tarifa = base
        regla = f"Tarifa plana zona {zona.value}"

    return TarifaResultado(
        tarifa=tarifa,
        regla_aplicada=regla,
        zona=zona,
        tipo_mandado=tipo_mandado,
    )


# ──────────────────────────────────────────────
# SMOKE TEST — ejecutar directamente para verificar
# python config_tarifas.py
# ──────────────────────────────────────────────

if __name__ == "__main__":
    casos = [
        (TipoMandado.MANDADO_COMUN,    Zona.CENTRO,    0),
        (TipoMandado.MANDADO_COMUN,    Zona.PERIFERIA, 0),
        (TipoMandado.DEPOSITO_BANCARIO, Zona.CENTRO,   800_000),
        (TipoMandado.DEPOSITO_BANCARIO, Zona.CENTRO,   2_000_000),
        (TipoMandado.DEPOSITO_BANCARIO, Zona.PERIFERIA, 5_000_000),
    ]

    print("=" * 52)
    print("  MANDABIKE — Verificación de tarifas")
    print("=" * 52)
    for tipo, zona, monto in casos:
        r = calcular_tarifa_servicio(tipo, zona, monto)
        print(f"\n  Servicio : {r.tipo_mandado.value}")
        print(f"  Zona     : {r.zona.value}")
        print(f"  Monto    : ${monto:,.0f}".replace(",", "."))
        print(f"  Tarifa   : {r.formatear_tarifa()}")
        print(f"  Regla    : {r.regla_aplicada}")
    print("\n" + "=" * 52)
