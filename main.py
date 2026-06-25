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

# Foto de stock libre (Unsplash License) — calle urbana con ciclista.
# Fuente: Max Bender, unsplash.com/photos/1zFK0pkHo9w
BACKGROUND_IMAGE_URL = (
    "https://images.unsplash.com/photo-1712249764665-15da106b4be8"
    "?fm=jpg&q=70&w=1200&auto=format&fit=crop"
)

ACCENT = "#0891b2"  # cian oscuro — bordes y detalles de tarjetas


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
    regla_display: str = "Tarifa plana zona Centro"

    def actualizar_calculo(self):
        """
        Handler único: convierte strings → Enums,
        llama al motor de negocio y actualiza la UI.
        """
        try:
            monto = float(self.monto_efectivo.replace(".", "").replace(",", ".")) \
                    if self.monto_efectivo else 0.0
        except ValueError:
            monto = 0.0

        try:
            tipo_enum = TipoMandado(self.tipo_mandado)
            zona_enum = Zona(self.zona)
        except ValueError:
            return

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
            f"Hola Manda Bike, necesito un servicio de "
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
    """Identidad de marca + métricas de confianza. Logo en 2 líneas, estilo urbano."""
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "MANDA",
                size="8",
                color="green",
                font_weight="900",
                letter_spacing="2px",
                line_height="1",
            ),
            rx.heading(
                "BIKE",
                size="8",
                color=ACCENT,
                font_weight="900",
                letter_spacing="2px",
                line_height="1",
            ),
            spacing="0",
            align="center",
        ),
        rx.text(
            "Más de 15 años de confianza y seguridad recorriendo las calles de General Pico.",
            size="3",
            color="gray",
            font_style="italic",
            text_align="center",
        ),
        rx.hstack(
            rx.box(
                rx.vstack(
                    rx.heading("15+", size="7", color="green", font_weight="900"),
                    rx.text("años", size="2", color="gray"),
                    align="center",
                    spacing="1",
                ),
                border=f"2px solid {ACCENT}",
                border_radius="12px",
                padding="14px 22px",
                background="rgba(255,255,255,0.95)", 
                box_shadow=f"0 0 10px {ACCENT}55",
            ),
            rx.box(
                rx.vstack(
                    rx.heading("100k+", size="7", color="green", font_weight="900"),
                    rx.text("mandados", size="2", color="gray"),
                    align="center",
                    spacing="1",
                ),
                border=f"2px solid {ACCENT}",
                border_radius="12px",
                padding="14px 22px",
                background="rgba(255,255,255,0.95)",
                box_shadow=f"0 0 10px {ACCENT}55",
            ),
            spacing="4",
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
        rx.fragment(),
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


def tarjeta_calculadora() -> rx.Component:
    """Tarjeta contenedora: selector + zona + tarifa, estilo urbano con borde cian."""
    return rx.box(
        rx.vstack(
            selector_servicio(),
            calculador_monto(),
            resultado_tarifa(),
            spacing="3",
            width="100%",
        ),
        border=f"2px solid {ACCENT}",
        border_radius="16px",
        background="rgba(255,255,255,0.95)", 
        box_shadow=f"0 0 16px {ACCENT}55",
        padding="20px",
        width="100%",
    )
def mapa() -> rx.Component:
    """Mapa de cobertura — General Pico (OpenStreetMap, sin costo)."""
    return rx.box(
        rx.vstack(
            rx.text("Zona de cobertura", size="2", color="gray", font_weight="600"),
            rx.el.iframe(  
                src="https://www.openstreetmap.org/export/embed.html?bbox=-63.80,-35.69,-63.71,-35.62&layer=mapnik",
                width="100%",
                height="300px",
            ),
            spacing="2",
            width="100%",
        ),
        border=f"2px solid {ACCENT}",
        border_radius="16px",
        background="rgba(255,255,255,0.95)",
        box_shadow=f"0 0 16px {ACCENT}55",
        padding="20px",
        width="100%",
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
def plan_empresas() -> rx.Component:
    """Sección Plan para Empresas — propuesta de valor B2B."""
    texto_wa = urllib.parse.quote(
        "Hola Manda Bike, quiero información sobre el Plan para Empresas"
    )
    whatsapp_empresas = f"https://wa.me/{WHATSAPP_NUMERO}?text={texto_wa}"

    return rx.box(
        rx.vstack(
            rx.heading(
                "Plan para Empresas",
                size="7",
                color="#f97316",
                font_weight="900",
                letter_spacing="1px",
            ),
            rx.text(
                "¿Tu negocio necesita mandados frecuentes? Armamos un plan a tu medida. "
                "Mismo cadete, misma confianza, precio acordado por volumen.",
                size="3",
                color="gray",
                text_align="center",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Mandados y trámites regulares", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Depósitos bancarios de alta confidencialidad", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Pedidos y entregas a domicilio", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Facturación y cuenta corriente", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Siempre el mismo cadete — confianza garantizada", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                rx.hstack(
                    rx.text("✓", color="#f97316", font_weight="900", size="3"),
                    rx.text("Precio negociable por volumen de servicios", size="3", color="gray"),
                    spacing="2", align="center",
                ),
                align="start",
                width="100%",
                spacing="2",
            ),
            rx.link(
                rx.button(
                    rx.hstack(
                        rx.text("💼", size="4"),
                        rx.text("Consultar Plan Empresas", size="4", font_weight="700"),
                        spacing="2",
                        align="center",
                    ),
                    width="100%",
                    size="4",
                    color_scheme="orange",
                    cursor="pointer",
                ),
                href=whatsapp_empresas,
                is_external=True,
                width="100%",
            ),
            spacing="4",
            width="100%",
            align="center",
        ),
        border="2px solid #f97316",
        border_radius="16px",
        background="rgba(255,255,255,0.95)",
        box_shadow="0 0 20px #f9731655",
        padding="24px",
        width="100%",
    )

def footer() -> rx.Component:
    """Contacto y redes — tarjeta estilo urbano con borde cian."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("📸", size="3"),
                rx.link(
                    rx.text("@manda1bike", size="2", color="gray"),
                    href=f"https://instagram.com/{INSTAGRAM_USER}",
                    is_external=True,
                ),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.text("✉", size="3"),
                rx.link(
                    rx.text("Email", size="2", color="gray"),
                    href=f"mailto:{EMAIL_CONTACTO}",
                ),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.text("📍", size="3"),
                rx.text("General Pico · La Pampa", size="2", color="gray"),
                spacing="2",
                align="center",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        border=f"2px solid {ACCENT}",
        border_radius="16px",
        background="rgba(255,255,255,0.95)", 
        box_shadow=f"0 0 14px {ACCENT}55",
        padding="20px",
        width="100%",
    )


# ──────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                hero(),
                tarjeta_calculadora(),mapa(),
                cta_whatsapp(),
                footer(),
                spacing="5",
                padding="24px",
                max_width="480px",
                width="100%",
            ),
            width="100%",
        ),
        background_image=(
            f"linear-gradient(rgba(255,255,255,0.78), rgba(255,255,255,0.85)), "
            f"url('{BACKGROUND_IMAGE_URL}')"
        ),
        background_size="cover",
        background_position="center",
        background_attachment="fixed",
        min_height="100vh",
        width="100%",
    )


# ──────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="cyan",
    )
)
app.add_page(index, route="/", title="Manda Bike — General Pico")
