"""Inventory API with shared SQL storage and a factory for isolated tests."""
import os
import secrets

from flask import Flask, jsonify, request
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy import create_engine, delete, insert, select, text, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def create_app(database_url=None):
    app = Flask(__name__)
    engine = create_engine(
        database_url or os.getenv("DATABASE_URL", "sqlite:///items.db"),
        pool_pre_ping=True,
    )
    metadata = MetaData()
    items = Table(
        "items", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(120), nullable=False),
        Column("sku", String(120), nullable=False, unique=True),
        Column("quantity", Integer, nullable=False, default=0),
    )
    # Initialize the schema separately to avoid worker startup races.
    app.extensions["database"] = engine
    app.extensions["metadata"] = metadata

    def valid_quantity(quantity):
        if (type(quantity) is not int
                or not -2147483648 <= quantity <= 2147483647):
            return False
        return True

    def authorized():
        token = os.getenv("API_TOKEN", "")
        return bool(token) and secrets.compare_digest(
            request.headers.get("Authorization", ""), f"Bearer {token}"
        )

    def payload():
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else None

    @app.errorhandler(IntegrityError)
    def duplicate_sku(error):
        return jsonify(error="SKU already exists"), 409

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        app.logger.error("Database request failed: %s", type(error).__name__)
        return jsonify(error="database unavailable"), 503

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.get("/ready")
    def ready():
        with engine.connect() as connection:
            connection.execute(select(items.c.id).limit(1))
        return jsonify(status="ready"), 200

    @app.get("/version")
    def version():
        return jsonify(
            app=os.getenv("APP_NAME", "Inventory Tracker"),
            version=os.getenv("APP_VERSION", "dev"),
            revision=os.getenv("APP_REVISION", "local"),
        ), 200

    @app.get("/items")
    def list_items():
        query = select(items).order_by(items.c.id)
        with engine.connect() as connection:
            return jsonify([dict(row) for row in connection.execute(
                query
            ).mappings()]), 200

    @app.post("/items")
    def create_item():
        if not authorized():
            return jsonify(error="unauthorized"), 401
        data = payload()
        if data is None:
            return jsonify(error="JSON object required"), 400
        name, sku = data.get("name"), data.get("sku")
        if not all(isinstance(v, str) and 0 < len(v.strip()) <= 120
                   for v in (name, sku)):
            return jsonify(error="name and sku need 1-120 characters"), 400
        quantity = data.get("quantity", 0)
        if not valid_quantity(quantity):
            return jsonify(error="quantity must be an integer from 0 to "
                           "2147483647"), 400
        with engine.begin() as connection:
            result = connection.execute(insert(items).values(
                name=name.strip(), sku=sku.strip(), quantity=quantity
            ))
            row = connection.execute(select(items).where(
                items.c.id == result.inserted_primary_key[0]
            )).mappings().one()
        return jsonify(dict(row)), 201

    @app.patch("/items/<int:item_id>")
    def update_item(item_id):
        if not authorized():
            return jsonify(error="unauthorized"), 401
        data = payload()
        if data is None or "quantity" not in data:
            return jsonify(error="quantity required"), 400
        quantity = data["quantity"]
        if not valid_quantity(quantity):
            return jsonify(error="quantity must be an integer from 0 to "
                           "2147483647"), 400
        with engine.begin() as connection:
            result = connection.execute(update(items).where(
                items.c.id == item_id
            ).values(quantity=quantity))
            if not result.rowcount:
                return jsonify(error="item not found"), 404
            row = connection.execute(select(items).where(
                items.c.id == item_id
            )).mappings().one()
        return jsonify(dict(row)), 200

    @app.delete("/items/<int:item_id>")
    def delete_item(item_id):
        if not authorized():
            return jsonify(error="unauthorized"), 401
        with engine.begin() as connection:
            result = connection.execute(delete(items).where(
                items.c.id == item_id
            ))
        if not result.rowcount:
            return jsonify(error="item not found"), 404
        return "", 204

    @app.cli.command("init-db")
    def init_db():
        with engine.begin() as connection:
            if engine.dialect.name == "postgresql":
                connection.execute(text("SELECT pg_advisory_xact_lock(81001)"))
            metadata.create_all(connection)
        print("Database schema ready")

    return app


app = create_app()
