from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserStatus
from app.db.session import get_session

router = APIRouter()


# ---------- schemas ----------

class RegisterRequest(BaseModel):
    email: str
    name: str | None = None
    picture: str | None = None


class RegisterResponse(BaseModel):
    status: str
    is_admin: bool


class UserOut(BaseModel):
    id: int
    email: str
    name: str | None
    picture: str | None
    status: str
    created_at: datetime


# ---------- helpers ----------

async def _require_admin(
    x_admin_email: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> User:
    if not x_admin_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Admin-Email header")
    result = await session.execute(select(User).where(User.email == x_admin_email))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
    return admin


# ---------- endpoints ----------

@router.post("/users/register", response_model=RegisterResponse)
async def register_user(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> RegisterResponse:
    """Called by NextAuth on every sign-in. Creates user if new, returns current status."""
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=body.email, name=body.name, picture=body.picture)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return RegisterResponse(status=user.status.value, is_admin=user.is_admin)


@router.get("/admin/users", response_model=list[UserOut])
async def list_users(
    filter_status: str | None = None,
    admin: User = Depends(_require_admin),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> list[UserOut]:
    """List all non-admin users, optionally filtered by status."""
    query = select(User).where(User.is_admin == False).order_by(User.created_at.desc())  # noqa: E712
    if filter_status:
        try:
            s = UserStatus(filter_status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid status: {filter_status}") from exc
        query = query.where(User.status == s)

    result = await session.execute(query)
    users = result.scalars().all()
    return [
        UserOut(
            id=u.id,
            email=u.email,
            name=u.name,
            picture=u.picture,
            status=u.status.value,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("/admin/users/{user_id}/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_user(
    user_id: int,
    admin: User = Depends(_require_admin),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.approved
    user.reviewed_at = datetime.now(UTC)
    await session.commit()


@router.post("/admin/users/{user_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_user(
    user_id: int,
    admin: User = Depends(_require_admin),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.rejected
    user.reviewed_at = datetime.now(UTC)
    await session.commit()
