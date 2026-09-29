import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:app@postgres:5432/referenceapp",
)

app = FastAPI(
    title="Inventory Service",
    version="1.0.0",
)


class ReservationRequest(BaseModel):
    product_id: int
    quantity: int


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "inventory-service",
    }


@app.get("/products")
def list_products():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, sku, name, price, stock
                FROM products
                ORDER BY id
                """
            )
            return cur.fetchall()


@app.get("/products/{product_id}")
def get_product(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, sku, name, price, stock
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            )
            product = cur.fetchone()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.post("/inventory/reserve")
def reserve_inventory(request: ReservationRequest):
    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s
                  AND stock >= %s
                RETURNING id, sku, name, price, stock
                """,
                (
                    request.quantity,
                    request.product_id,
                    request.quantity,
                ),
            )

            product = cur.fetchone()

            if product is None:
                raise HTTPException(
                    status_code=409,
                    detail="Product unavailable or insufficient stock",
                )

            conn.commit()

    return {
        "status": "reserved",
        "quantity": request.quantity,
        "product": product,
    }
