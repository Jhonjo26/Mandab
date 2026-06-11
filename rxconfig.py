import reflex as rx

config = rx.Config(
    app_name="main",
    app_module_import="main",
    db_url=None,
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
)
