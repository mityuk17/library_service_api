from databases.core import Connection
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app import utils
from app.crud import user as db_user
from app.crud import misc as db_misc
from app.schemas import users, miscs

router = APIRouter(prefix="/api/v1/admin")


@router.get('users', response_model=list[users.NoPasswordUser])
async def get_users(authorized_user: users.User = Depends(utils.get_current_user),
                    session: Connection = Depends(db_misc.get_session)):
    """
    Get information about all users
    :param authorized_user: schemas.User
    :param session: Connection object
    :return: users list[schemas.NoPasswordUser]
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    all_users = await db_user.get_users(session)
    return all_users


@router.post('/users', response_model=miscs.GenericResponse)
async def create_user(new_user: users.NewUserData, background_tasks: BackgroundTasks,
                      authorized_user: users.User = Depends(utils.get_current_user),
                      session: Connection = Depends(db_misc.get_session)):
    """
    Creates a new user
    :param session: Connection object
    :param background_tasks: Background tasks
    :param new_user: new user data
    :param authorized_user: schemas.User object
    :return: schemas.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    new_user.password = utils.get_password_hash(new_user.password)
    await db_user.insert_user(new_user, session)
    background_tasks.add_task(utils.notify_about_account_creation, new_user)
    return miscs.GenericResponse(result=True)


@router.put('/users', response_model=miscs.GenericResponse)
async def change_user_data(updated_user_data: users.UpdatedUserData,
                           authorized_user: users.User = Depends(utils.get_current_user),
                           session: Connection = Depends(db_misc.get_session)):
    """
    Updates User's fields' values
    :param session: Connection object
    :param updated_user_data: updated user data
    :param authorized_user: schemas.User object
    :return: schemas.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db_user.get_user_by_id(updated_user_data.id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    if updated_user_data.password:
        updated_user_data.password = utils.get_password_hash(updated_user_data.password)
    updated_user = users.User(**(utils.unite_dicts(user.dict(), updated_user_data.dict())))
    await db_user.update_user(updated_user, session)
    return miscs.GenericResponse(result=True)


@router.get('/users/{user_id}', response_model=users.NoPasswordUser)
async def get_user_info(user_id: int, authorized_user: users.User = Depends(utils.get_current_user),
                        session: Connection = Depends(db_misc.get_session)):
    """
    Gets user information by id
    :param session: Connection object
    :param user_id:
    :param authorized_user: schemas.User object
    :return: schemas.NoPasswordUser
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    user = await db_user.get_no_password_user_by_id(user_id, session)
    if not user:
        return HTTPException(status_code=404, detail='User not found')
    return user


@router.delete('/users/{user_id}', response_model=miscs.GenericResponse)
async def delete_user(user_id: int, authorized_user: users.User = Depends(utils.get_current_user),
                      session: Connection = Depends(db_misc.get_session)):
    """
    Deletes user from database
    :param session: Connection object
    :param user_id:
    :param authorized_user: schemas.User object
    :return: schemas.GenericResponse
    """
    if not (authorized_user and authorized_user.check_role('admin')):
        return HTTPException(status_code=401)
    await db_user.delete_user(user_id, session)
    return miscs.GenericResponse(result=True)
