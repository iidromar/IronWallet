from api.controllers.wallet_controller import router as WalletRouter


def init_routes(app):
    app.include_router(WalletRouter, prefix="/wallets", tags=["Wallets"])
    return app
