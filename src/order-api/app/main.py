import os
from decimal import Decimal

import httpx
import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel


def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_host = os.getenv("DB_HOST")
    if db_host:
        return (
            f"postgresql://{os.getenv('DB_USER', 'codedna')}:"
            f"{os.environ['DB_PASSWORD']}@"
            f"{db_host}:{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'referenceapp')}"
        )

    return "postgresql://app:app@postgres:5432/referenceapp"


DATABASE_URL = get_database_url()

INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL",
    "http://inventory-service:8001",
)

app = FastAPI(
    title="Order API",
    version="1.0.0",
)


class OrderRequest(BaseModel):
    customer_name: str
    product_id: int
    quantity: int


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "order-api",
    }


@app.get("/orders")
def list_orders():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    customer_name,
                    product_id,
                    product_name,
                    quantity,
                    unit_price,
                    total_price,
                    status,
                    created_at
                FROM orders
                ORDER BY created_at DESC
                """
            )
            return cur.fetchall()


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    customer_name,
                    product_id,
                    product_name,
                    quantity,
                    unit_price,
                    total_price,
                    status,
                    created_at
                FROM orders
                WHERE id = %s
                """,
                (order_id,),
            )
            order = cur.fetchone()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.post("/orders", status_code=201)
def create_order(request: OrderRequest):
    customer_name = request.customer_name.strip()

    if not customer_name:
        raise HTTPException(
            status_code=400,
            detail="Customer name is required",
        )

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    try:
        response = httpx.post(
            f"{INVENTORY_SERVICE_URL}/inventory/reserve",
            json={
                "product_id": request.product_id,
                "quantity": request.quantity,
            },
            timeout=10.0,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Inventory service unavailable",
        ) from exc

    if response.status_code != 200:
        try:
            detail = response.json().get(
                "detail",
                "Inventory reservation failed",
            )
        except ValueError:
            detail = "Inventory reservation failed"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    reservation = response.json()
    product = reservation["product"]

    unit_price = Decimal(str(product["price"]))
    total_price = unit_price * request.quantity

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (
                    customer_name,
                    product_id,
                    product_name,
                    quantity,
                    unit_price,
                    total_price,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'CONFIRMED')
                RETURNING
                    id,
                    customer_name,
                    product_id,
                    product_name,
                    quantity,
                    unit_price,
                    total_price,
                    status,
                    created_at
                """,
                (
                    customer_name,
                    request.product_id,
                    product["name"],
                    request.quantity,
                    unit_price,
                    total_price,
                ),
            )

            order = cur.fetchone()
            conn.commit()

    return order
