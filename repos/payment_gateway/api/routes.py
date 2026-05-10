from api.controllers.payment_controller import router as PaymentRouter


def init_routes(app):
    app.include_router(PaymentRouter, prefix="/payments", tags=["Payments"])
    return app
