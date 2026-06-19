# main.py
# Mandabike — General Pico, La Pampa
# Interfaz principal Reflex. Mobile-First.

import reflex as rx
import urllib.parse
from config_tarifas import (
    calcular_tarifa_servicio,
    TipoMandado,
    Zona,
)

# ──────────────────────────────────────────────
# CONSTANTES DE CONTACTO
# ──────────────────────────────────────────────

WHATSAPP_NUMERO = "542302567402"  # Formato internacional sin + ni guiones
INSTAGRAM_USER  = "manda1bike"
EMAIL_CONTACTO  = "carlosfabianpardo9@gmail.com"


# ──────────────────────────────────────────────
# ESTADO REACTIVO
# ──────────────────────────────────────────────

class MandabikeState(rx.State):
    """
    Fuente única de verdad para la UI.
    Reflex solo admite tipos primitivos en el state:
    str, int, float, bool. Los Enums se convierten internamente.
    """
    tipo_mandado: str = TipoMandado.MANDADO_COMUN.value
    zona: str         = Zona.CENTRO.value
    monto_efectivo: str = ""
    tarifa_display: str = "$5.000"
    whatsapp_link: str  = ""

    def actualizar_calculo(self):
        """
        Handler único: convierte strings → Enums,
        llama al motor de negocio y actualiza la UI.
        """
        # Conversión segura de monto
        try:
            monto = float(self.monto_efectivo.replace(".", "").replace(",", ".")) \
                    if self.monto_efectivo else 0.0
        except ValueError:
            monto = 0.0

        # Conversión str → Enum (compatibilidad con config_tarifas.py)
        try:
            tipo_enum = TipoMandado(self.tipo_mandado)
            zona_enum = Zona(self.zona)
        except ValueError:
            return  # Valor inválido: no actualizar

        resultado = calcular_tarifa_servicio(
            tipo_mandado=tipo_enum,
            zona=zona_enum,
            monto_efectivo=monto,
        )

        self.tarifa_display = resultado.formatear_tarifa()
        self.regla_display  = resultado.regla_aplicada

    def set_tipo_mandado(self, valor: str):
        self.tipo_mandado = valor
        self.actualizar_calculo()
        
        def set_zona(self, valor: str):
            self.zona = valor
            self.actualizar_calculo()

        def set_monto(self, valor: str):
            self.monto_efectivo = valor
            self.actualizar_calculo()
        @rx.var
        def whatsapp_link(self) -> str:
            texto = (
                f"Hola Mandabike, necesito un servicio de "
                f"{self.tipo_mandado} en la zona {self.zona} "
                f"por un valor de tarifa de {self.tarifa_display}"
            )
            return (
                f"https://wa.me/542302567402"
                f"?text={urllib.parse.quote(texto)}"
            ) 
        


# ──────────────────────────────────────────────
# COMPONENTES UI
# ──────────────────────────────────────────────

def hero() -> rx.Component:
    """Identidad de marca + métricas de confianza."""
    return rx.vstack(
        rx.heading(
            "MANDABIKE",
            size="9",
            color="green",
            font_weight="900",
            letter_spacing="2px",
        ),
        rx.text(
            "Más de 15 años de confianza y seguridad recorriendo las calles de General Pico.",
            size="3",
            color="gray",
            font_style="italic",
            text_align="center",
        ),
        # Métricas
        rx.hstack(
            rx.vstack(
                rx.heading("15+", size="7", color="orange"),
                rx.text("años", size="2", color="gray"),
                align="center",
            ),
            rx.divider(orientation="vertical", height="50px"),
            rx.vstack(
                rx.heading("100k+", size="7", color="orange"),
                rx.text("mandados", size="2", color="gray"),
                align="center",
            ),
            spacing="6",
            justify="center",
            width="100%",
            padding_y="12px",
        ),
        align="center",
        width="100%",
        padding_y="24px",
    )


def selector_servicio() -> rx.Component:
    """Selector de tipo de mandado y zona."""
    return rx.vstack(
        rx.text("Tipo de servicio", size="2", color="gray", font_weight="600"),
        rx.select(
            [TipoMandado.MANDADO_COMUN.value, TipoMandado.DEPOSITO_BANCARIO.value],
            value=MandabikeState.tipo_mandado,
            on_change=MandabikeState.set_tipo_mandado,
            width="100%",
        ),
        rx.text("Zona de entrega", size="2", color="gray", font_weight="600"),
        rx.hstack(
            rx.button(
                "Centro",
                on_click=lambda: MandabikeState.set_zona(Zona.CENTRO.value),
                color_scheme=rx.cond(
                    MandabikeState.zona == Zona.CENTRO.value,
                    "orange",
                    "gray",
                ),
                width="50%",
            ),
            rx.button(
                "Periferia",
                on_click=lambda: MandabikeState.set_zona(Zona.PERIFERIA.value),
                color_scheme=rx.cond(
                    MandabikeState.zona == Zona.PERIFERIA.value,
                    "orange",
                    "gray",
                ),
                width="50%",
            ),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="2",
    )


def calculador_monto() -> rx.Component:
    """Input de monto — solo visible para Depósito Bancario."""
    return rx.cond(
        MandabikeState.tipo_mandado == TipoMandado.DEPOSITO_BANCARIO.value,
        rx.vstack(
            rx.text("Monto a depositar ($)", size="2", color="gray", font_weight="600"),
            rx.input(
                placeholder="Ej: 2000000",
                value=MandabikeState.monto_efectivo,
                on_change=MandabikeState.set_monto,
                type="number",
                width="100%",
            ),
            rx.text(
                "Depósitos de Alta Confidencialidad",
                size="1",
                color="orange",
                font_style="italic",
            ),
            width="100%",
            spacing="2",
        ),
        rx.fragment(),  # Nada si es mandado común
    )


def resultado_tarifa() -> rx.Component:
    """Muestra la tarifa calculada y la regla aplicada."""
    return rx.vstack(
        rx.divider(),
        rx.hstack(
            rx.text("Tarifa estimada:", size="3", color="gray"),
            rx.heading(
                MandabikeState.tarifa_display,
                size="7",
                color="orange",
                font_weight="900",
            ),
            justify="between",
            width="100%",
        ),
        rx.text(
            MandabikeState.regla_display,
            size="1",
            color="gray",
            font_style="italic",
        ),
        width="100%",
        spacing="2",
        padding_y="8px",
    )


def cta_whatsapp() -> rx.Component:
        """Botón principal — abre WhatsApp con mensaje pre-cargado (skill 3)."""
        return rx.button(
            rx.hstack(
                rx.text("📱", size="4"),
                rx.text("Solicitar Cadete", size="4", font_weight="700"),
                spacing="2",
                align="center",
            ),
            on_click=rx.redirect(MandabikeState.whatsapp_link, is_external=True),
            width="100%",
            size="4",
            color_scheme="green",
            cursor="pointer",
        )


def footer() -> rx.Component:
    """Contacto y redes."""
    return rx.vstack(
        rx.divider(),
        rx.hstack(
            rx.link(
                rx.text("📸 @manda1bike", size="2", color="gray"),
                href=f"https://instagram.com/{INSTAGRAM_USER}",
                is_external=True,
            ),
            rx.link(
                rx.text("✉ Email", size="2", color="gray"),
                href=f"mailto:{EMAIL_CONTACTO}",
            ),
            justify="center",
            spacing="6",
            width="100%",
        ),
        rx.text(
            "General Pico · La Pampa",
            size="1",
            color="gray",
            text_align="center",
        ),
        width="100%",
        padding_y="16px",
    )


# ──────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            hero(),
            selector_servicio(),
            calculador_monto(),
            resultado_tarifa(),
            cta_whatsapp(),
            footer(),
            spacing="4",
            padding="24px",
            max_width="480px",  # Mobile-First: ancho máximo celular
            width="100%",
        ),
        min_height="100vh",
        background="black",
    )


# ──────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="orange",
    )
)
app.add_page(index, route="/", title="Mandabike — General Pico")
      
