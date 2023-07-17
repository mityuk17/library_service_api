from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.crud import misc as db_misc
from app import utils
from app.schemas import miscs

router = APIRouter(prefix='/authorization')


@router.post("/token", response_model=miscs.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: Connection = Depends(db_misc.get_session)):
    user = await utils.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401)
    access_token = utils.create_access_token(
        data={"sub": user.login}
    )
    return miscs.Token(access_token=access_token, token_type='bearer')
