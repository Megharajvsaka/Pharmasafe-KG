"""
deps.py
-------
Dependency injection providers for FastAPI controllers.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.domain.models.user import User
from backend.app.core.security import decode_token
from backend.app.infrastructure.neo4j_repository import Neo4jGraphRepository
from ml_engine.inference.gnn_predictor import get_predictor
from backend.app.services.resolver_service import get_resolver, ResolverService
from backend.app.services.ddi_service import DDIService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token has expired. Please refresh your session.")
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated.")
    return user


def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        return get_current_user(token=token, db=db)
    except HTTPException:
        return None


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user has administrator privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access this resource."
        )
    return current_user


def get_graph_repository() -> Neo4jGraphRepository:
    return Neo4jGraphRepository()


def get_ddi_service(repo: Neo4jGraphRepository = Depends(get_graph_repository)) -> DDIService:
    predictor = get_predictor()
    return DDIService(graph_repo=repo, predictor=predictor)


def get_resolver_service() -> ResolverService:
    return get_resolver()
