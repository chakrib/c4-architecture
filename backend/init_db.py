"""
Initialize database with pgvector extension and create tables.
Run this script once to set up the database.
"""
from sqlalchemy import text
from app.core.database import engine, Base
from app.models.database import (
    User, Team, ValidatedInput, Diagram,
    UserFeedback, LearnedPattern, UsageLog
)


def init_db():
    """Initialize database with pgvector extension and create all tables"""
    
    # Create pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("✓ Created pgvector extension")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created all database tables")
    
    # Create default team
    from sqlalchemy.orm import Session
    from app.api.auth import get_password_hash
    
    with Session(engine) as session:
        # Check if default team exists
        from app.models.database import Team
        default_team = session.query(Team).filter(Team.name == "Default").first()
        
        if not default_team:
            default_team = Team(
                name="Default",
                description="Default team for new users",
                api_quota_per_month=1000
            )
            session.add(default_team)
            session.commit()
            print("✓ Created default team")
        
        # Create admin user if not exists
        admin_user = session.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                full_name="Administrator",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                team_id=default_team.id
            )
            session.add(admin_user)
            session.commit()
            print("✓ Created admin user (username: admin, password: admin123)")
            print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")
    
    print("\n✅ Database initialization complete!")
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Change the admin password")
    print("3. Start the server: uvicorn app.main:app --reload")


if __name__ == "__main__":
    init_db()
