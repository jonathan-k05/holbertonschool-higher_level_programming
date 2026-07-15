"""
db.py
Database setup, ORM models, seed data, and schema introspection.

We use SQLAlchemy so the app can talk to SQLite (default, zero setup)
or swap in Postgres later by changing DATABASE_URL only.
"""

import os
from datetime import date, timedelta
import random

from sqlalchemy import (
    create_engine, inspect, text,
    Column, Integer, String, Float, Date, ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

# check_same_thread=False is needed because FastAPI can use a request in a
# different thread than the one that created the connection (SQLite only).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    signup_date = Column(Date, nullable=False)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # open, closed, cancelled
    amount = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_date = Column(Date, nullable=True)   # null == not paid yet
    due_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    paid = Column(Integer, nullable=False, default=0)  # 0/1 (SQLite has no bool)

    order = relationship("Order", back_populates="payments")


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

REGIONS = ["North", "South", "East", "West"]
STATUSES = ["open", "closed", "cancelled"]


def _seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Customer).count() > 0:
            return  # already seeded

        random.seed(42)
        today = date.today()

        customers = []
        for i in range(1, 31):
            c = Customer(
                name=f"Customer {i}",
                region=random.choice(REGIONS),
                signup_date=today - timedelta(days=random.randint(30, 900)),
            )
            customers.append(c)
        db.add_all(customers)
        db.flush()  # assign ids

        orders = []
        for i in range(1, 151):
            c = random.choice(customers)
            o = Order(
                customer_id=c.id,
                order_date=today - timedelta(days=random.randint(0, 400)),
                status=random.choices(STATUSES, weights=[0.2, 0.7, 0.1])[0],
                amount=round(random.uniform(50, 5000), 2),
            )
            orders.append(o)
        db.add_all(orders)
        db.flush()

        payments = []
        for o in orders:
            due = o.order_date + timedelta(days=30)
            is_paid = random.random() < 0.75
            payments.append(
                Payment(
                    order_id=o.id,
                    due_date=due,
                    payment_date=(due - timedelta(days=random.randint(0, 20)))
                    if is_paid else None,
                    amount=o.amount,
                    paid=1 if is_paid else 0,
                )
            )
        db.add_all(payments)
        db.commit()
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    _seed_if_empty()


# ---------------------------------------------------------------------------
# Schema introspection (used to ground the model's prompt in the real schema)
# ---------------------------------------------------------------------------

def get_schema_description() -> str:
    """
    Read the live schema straight from the database (not hardcoded) and
    return a compact text block suitable for pasting into a prompt.
    """
    insp = inspect(engine)
    lines = []
    for table_name in insp.get_table_names():
        cols = insp.get_columns(table_name)
        col_strs = [f"{c['name']} {c['type']}" for c in cols]
        lines.append(f"TABLE {table_name} ({', '.join(col_strs)})")

        fks = insp.get_foreign_keys(table_name)
        for fk in fks:
            local = ", ".join(fk["constrained_columns"])
            ref_table = fk["referred_table"]
            ref_cols = ", ".join(fk["referred_columns"])
            lines.append(f"  FOREIGN KEY {table_name}.{local} -> {ref_table}.{ref_cols}")

    return "\n".join(lines)


def get_schema_json() -> dict:
    """Structured version of the schema, for the GET /schema endpoint."""
    insp = inspect(engine)
    schema = {}
    for table_name in insp.get_table_names():
        cols = insp.get_columns(table_name)
        schema[table_name] = {
            "columns": [{"name": c["name"], "type": str(c["type"])} for c in cols],
            "foreign_keys": [
                {
                    "columns": fk["constrained_columns"],
                    "references_table": fk["referred_table"],
                    "references_columns": fk["referred_columns"],
                }
                for fk in insp.get_foreign_keys(table_name)
            ],
        }
    return schema


def run_readonly_query(sql: str, max_rows: int = 1000):
    """
    Execute an already-validated read-only SELECT and return rows as a
    list of dicts, plus the column names. Assumes `sql` already passed
    guardrails.validate_sql().
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchmany(max_rows)]
        return columns, rows
