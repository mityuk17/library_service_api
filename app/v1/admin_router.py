from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.v1 import utils
from app.core.schemas import users_schema
from app.core.schemas import misc_schema
import app.core.models.database as db

router = APIRouter(prefix="/api/v1/admin")


@router.get('users', response_model=list[users_schema.NoPasswordUser])
async def get_users(authorized_user: users_schema.User = Depends(utils.get_current_user),
                    session: Connection = Depends(db.get_session)):
    """
    Get information about all users
    :param authorized_user: models.User
    :param session: Connection object
    :return: users list[models.NoPasswordUser]
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    users = await db.get_users(session)
    return users


@router.post('/users', response_model=misc_schema.GenericResponse)
async def create_user(new_user: users_schema.NewUserData, background_tasks: BackgroundTasks,
                      authorized_user: users_schema.User = Depends(utils.get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Creates a new user
    :param session: Connection object
    :param background_tasks: Background tasks
    :param new_user: new user data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    new_user.password = utils.get_password_hash(new_user.password)
    await db.insert_user(new_user, session)
    background_tasks.add_task(utils.notify_about_account_creation, new_user)
    return misc_schema.GenericResponse(result=True)


@router.put('/users', response_model=misc_schema.GenericResponse)
async def change_user_data(updated_user_data: users_schema.UpdatedUserData,
                           authorized_user: users_schema.User = Depends(utils.get_current_user),
                           session: Connection = Depends(db.get_session)):
    """
    Updates User's fields' values
    :param session: Connection object
    :param updated_user_data: updated user data
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db.get_user_by_id(updated_user_data.id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if updated_user_data.password:
        updated_user_data.password = utils.get_password_hash(updated_user_data.password)
    updated_user = users_schema.User(**(utils.unite_dicts(user.dict(), updated_user_data.dict())))
    await db.update_user(updated_user, session)
    return misc_schema.GenericResponse(result=True)


@router.get('/users/{user_id}', response_model=users_schema.NoPasswordUser)
async def get_user_info(user_id: int, authorized_user: users_schema.User = Depends(utils.get_current_user),
                        session: Connection = Depends(db.get_session)):
    """
    Gets user information by id
    :param session: Connection object
    :param user_id:
    :param authorized_user: models.User object
    :return: models.NoPasswordUser
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db.get_no_password_user_by_id(user_id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user


@router.delete('/users/{user_id}', response_model=misc_schema.GenericResponse)
async def delete_user(user_id: int, authorized_user: users_schema.User = Depends(utils.get_current_user),
                      session: Connection = Depends(db.get_session)):
    """
    Deletes user from database
    :param session: Connection object
    :param user_id:
    :param authorized_user: models.User object
    :return: models.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    await db.delete_user(user_id, session)
    return misc_schema.GenericResponse(result=True)
