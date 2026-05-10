from api.controllers.statement_controller import router as StatementRouter
from api.controllers.webhook_controller import router as WebhookRouter


def init_routes(app):
    app.include_router(WebhookRouter, prefix="/webhooks", tags=["Webhooks"])
    app.include_router(StatementRouter, prefix="/statements", tags=["Statements"])
    return app
