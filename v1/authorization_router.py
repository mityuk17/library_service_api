from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from core.schemas import misc_schema
import core.models.database as db
from v1 import utils


router = APIRouter(prefix='/authorization')


@router.post("/token", response_model=misc_schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: Connection = Depends(db.get_session)):
    user = await utils.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401)
    access_token = utils.create_access_token(
        data={"sub": user.login}
    )
    return misc_schema.Token(access_token=access_token, token_type='bearer')
