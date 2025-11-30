import random
from datetime import datetime, timedelta
from models import SessionLocal, init_db, Store, Product, Order, OrderItem


def seed():
    init_db()
    session = SessionLocal()

    # Lojas
    stores = [
        Store(name="Loja Centro", city="Araraquara"),
        Store(name="Loja Norte", city="Araraquara"),
        Store(name="Loja Sul", city="São Carlos"),
    ]
    session.add_all(stores)

    # Produtos
    categories = ["Mercearia", "Hortifruti", "Limpeza", "Bebidas", "Padaria"]
    products = []
    for i in range(1, 61):
        cat = random.choice(categories)
        price = round(random.uniform(3.0, 50.0), 2)
        cost = round(price * random.uniform(0.5, 0.8), 2)
        p = Product(
            sku=f"SKU{i:04d}",
            name=f"Produto {i}",
            category=cat,
            price=price,
            cost=cost,
            stock=random.randint(20, 300),
        )
        products.append(p)
    session.add_all(products)
    session.commit()

    # Pedidos últimos 60 dias
    all_products = session.query(Product).all()
    all_stores = session.query(Store).all()

    start = datetime.now() - timedelta(days=60)
    for d in range(60):
        day = start + timedelta(days=d)
        for _ in range(random.randint(8, 40)):   # pedidos por dia
            store = random.choice(all_stores)
            order = Order(store_id=store.id, created_at=day + timedelta(hours=random.randint(8, 21)))
            session.add(order)
            session.flush()

            # itens do pedido
            for _ in range(random.randint(1, 6)):
                prod = random.choice(all_products)
                qty = random.randint(1, 5)
                oi = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=prod.price
                )
                session.add(oi)
                prod.stock = max(prod.stock - qty, 0)
    session.commit()
    session.close()
    print("✓ Seed concluído com sucesso!")


if __name__ == "__main__":
    seed()
