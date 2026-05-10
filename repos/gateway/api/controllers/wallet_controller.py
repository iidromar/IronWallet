import httpx
from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from core.config import INVESTMENT_WALLET_URL

router = APIRouter()


def buildResponse(resp: httpx.Response) -> JSONResponse:
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


async def wallet_id_for(user_id: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{INVESTMENT_WALLET_URL}/wallets/byUser/{user_id}")
    if resp.status_code != 200:
        raise HTTPException(404, "Wallet not found for user")
    return resp.json()["wallet_id"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_wallet(x_user_id: str = Header(...)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{INVESTMENT_WALLET_URL}/wallets",
            json={"user_id": x_user_id},
        )
    return buildResponse(resp)


@router.get("/me")
async def get_my_wallet(x_user_id: str = Header(...)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{INVESTMENT_WALLET_URL}/wallets/byUser/{x_user_id}")
    return buildResponse(resp)


@router.post("/me/topUp", status_code=status.HTTP_202_ACCEPTED)
async def top_up(request: Request, x_user_id: str = Header(...)):
    wallet_id = await wallet_id_for(x_user_id)
    body = await request.json()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{INVESTMENT_WALLET_URL}/wallets/{wallet_id}/topUp",
            json=body,
        )
    return buildResponse(resp)


@router.get("/me/fundRequests")
async def list_fund_requests(x_user_id: str = Header(...)):
    wallet_id = await wallet_id_for(x_user_id)
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{INVESTMENT_WALLET_URL}/wallets/{wallet_id}/fundRequests")
    return buildResponse(resp)
