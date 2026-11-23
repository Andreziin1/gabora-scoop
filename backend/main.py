from pathlib import Path
from secrets import token_hex

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from .database import connection, initialize

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

PRODUCTS = {
    "bijuterias": {"id": "bijuterias", "name": "Scoop de Bijuterias", "price": 59.90},
    "skincare": {"id": "skincare", "name": "Scoop de Skincare", "price": 69.90},
    "misto": {"id": "misto", "name": "Scoop Misto", "price": 64.90},
}

STATUS_LABELS = {
    "pago": "Pagamento confirmado",
    "aguardando_preparacao": "Aguardando preparação",
    "em_preparacao": "Em preparação",
    "preparado": "Preparado",
    "enviado": "Enviado",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
}


class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, le=10)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=20)
    cep: str = Field(min_length=8, max_length=10)
    address: str = Field(min_length=8, max_length=180)
    payment_method: str
    items: list[CartItem]


class StatusUpdate(BaseModel):
    status: str
    tracking_code: str | None = None
    video_url: str | None = None


app = FastAPI(title="Gabora Scoop", version="1.0.0")
initialize()
app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/products")
def products():
    return list(PRODUCTS.values())


@app.post("/api/orders", status_code=201)
def create_order(payload: OrderCreate):
    if not payload.items:
        raise HTTPException(400, "O carrinho está vazio.")
    if payload.payment_method not in {"pix", "card"}:
        raise HTTPException(400, "Forma de pagamento inválida.")

    normalized = []
    total = 0.0
    for item in payload.items:
        product = PRODUCTS.get(item.product_id)
        if not product:
            raise HTTPException(400, "Produto inválido.")
        total += product["price"] * item.quantity
        normalized.append((product, item.quantity))

    public_id = f"GS-{token_hex(3).upper()}"
    with connection() as conn:
        cursor = conn.execute(
            """INSERT INTO orders
            (public_id, customer_name, email, phone, cep, address, total, payment_method, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (public_id, payload.customer_name, payload.email.lower(), payload.phone,
             payload.cep, payload.address, round(total, 2), payload.payment_method, "pago"),
        )
        order_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO order_items (order_id, product_id, name, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
            [(order_id, p["id"], p["name"], q, p["price"]) for p, q in normalized],
        )
    return {"order_id": public_id, "total": round(total, 2), "status": "pago"}


@app.get("/api/orders/{public_id}")
def get_order(public_id: str, email: str):
    with connection() as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE public_id = ? AND lower(email) = lower(?)",
            (public_id.upper(), email),
        ).fetchone()
        if not order:
            raise HTTPException(404, "Pedido não encontrado.")
        items = conn.execute(
            "SELECT name, quantity, unit_price FROM order_items WHERE order_id = ?", (order["id"],)
        ).fetchall()
    result = dict(order)
    result["status_label"] = STATUS_LABELS.get(result["status"], result["status"])
    result["items"] = [dict(x) for x in items]
    result.pop("id", None)
    return result


@app.get("/api/admin/orders")
def admin_orders():
    with connection() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return [{**dict(row), "status_label": STATUS_LABELS.get(row["status"], row["status"])} for row in rows]


@app.patch("/api/admin/orders/{public_id}")
def update_order(public_id: str, payload: StatusUpdate):
    if payload.status not in STATUS_LABELS:
        raise HTTPException(400, "Status inválido.")
    with connection() as conn:
        cursor = conn.execute(
            "UPDATE orders SET status = ?, tracking_code = ?, video_url = ? WHERE public_id = ?",
            (payload.status, payload.tracking_code, payload.video_url, public_id.upper()),
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "Pedido não encontrado.")
    return {"message": "Pedido atualizado."}


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


@app.get("/{page}.html")
def page(page: str):
    candidate = FRONTEND / f"{page}.html"
    if not candidate.exists():
        raise HTTPException(404)
    return FileResponse(candidate)

