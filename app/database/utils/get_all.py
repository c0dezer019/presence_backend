# Internal modules
from typing import Type, List

# Third-party modules
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from utils.types import Snowflake


def get_all(db: Session, model: Type[Guild | MemberShard], guild_id: Snowflake) -> List[Type[Guild | MemberShard]]:
    return db.query(model).where(model.guild_id == guild_id).all()
