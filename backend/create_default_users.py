"""
Script to create default admin and test users in the database.
Run this after setting up the database.

Usage:
    python create_default_users.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.user import User, UserRole
from app.utils.auth import hash_password


async def create_default_users():
    """Create default admin and test users"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == "admin@company.com")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✅ Admin user already exists: admin@company.com")
        else:
            # Create default admin
            admin = User(
                name="System Administrator",
                email="admin@company.com",
                password_hash=hash_password("admin123"),  # Change this password!
                role=UserRole.admin
            )
            session.add(admin)
            print("✅ Created admin user: admin@company.com / admin123")
        
        # Check if test user already exists
        result = await session.execute(
            select(User).where(User.email == "user@company.com")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("✅ Test user already exists: user@company.com")
        else:
            # Create test regular user
            user = User(
                name="Test User",
                email="user@company.com",
                password_hash=hash_password("user123"),
                role=UserRole.user
            )
            session.add(user)
            print("✅ Created test user: user@company.com / user123")
        
        await session.commit()
    
    await engine.dispose()
    
    print("\n" + "="*60)
    print("DEFAULT USERS CREATED SUCCESSFULLY")
    print("="*60)
    print("\n📧 Admin Login:")
    print("   Email: admin@company.com")
    print("   Password: admin123")
    print("   ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")
    print("\n📧 Test User Login:")
    print("   Email: user@company.com")
    print("   Password: user123")
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(create_default_users())
