from app import create_app
from app.core.db import db
from app.models import Company, Store, User
from werkzeug.security import generate_password_hash


def seed() -> None:
    app = create_app()
    with app.app_context():
        if User.query.filter_by(email="owner@demo-company.com").first():
            print("Demo data already exists.")
            return

        company = Company(name="Demo Company", slug="demo-company")
        db.session.add(company)
        db.session.flush()

        user = User(
            company_id=company.id,
            name="Demo Owner",
            email="owner@demo-company.com",
            password_hash=generate_password_hash("DemoPass123"),
        )
        db.session.add(user)

        store_1 = Store(
            company_id=company.id,
            name="Demo Store One",
            platform="Shopify",
            store_url="https://demo-store-one.example",
            external_api_token="shopify_token_demo_1",
            external_api_secret="shopify_secret_demo_1",
            internal_api_key=Store.generate_internal_api_key(),
            internal_webhook_token=Store.generate_webhook_token(),
            status="connected",
        )
        store_2 = Store(
            company_id=company.id,
            name="Demo Store Two",
            platform="WooCommerce",
            store_url="https://demo-store-two.example",
            external_api_token="woo_token_demo_2",
            external_api_secret="woo_secret_demo_2",
            internal_api_key=Store.generate_internal_api_key(),
            internal_webhook_token=Store.generate_webhook_token(),
            status="connected",
        )
        db.session.add_all([store_1, store_2])
        db.session.commit()
        print("Seeded demo company with two stores.")
        print("Login: owner@demo-company.com / DemoPass123")


if __name__ == "__main__":
    seed()
