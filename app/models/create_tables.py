from app.db.database import Base, engine

from app.models.user import User
from app.models.otp import OTPVerification
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user_memory import UserMemory
from app.models.feedback import Feedback


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")