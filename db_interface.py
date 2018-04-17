"""
DB interface. Flask code shouldn't know anything else about the database other
than the functions exposed in this module. (In case we suddenly move over to
Postgres or sqlite or something)
Must export DATABASE_URL... before running this
"""

import records
import os
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# export DATABASE_URL=...; export FLASK_APP=...; python3 flask run
DATABASE_URL = (os.environ.get('DATABASE_URL')
                or 'mysql://root:lionell123@localhost:3306/smartbin')

# MYSQLDB_CONNECT_PARAMS = {
#     'user': 'mysql',
#     'passwd': '76a92eca8c7c4dc1',
#     'host': 'xenialsrv',
#     'port': 3307,
#     'db': 'smartbin'
# }


def transform_can_to_canonical(can_dirty):
    """
    Transform a CAN to the database format (string of digits).
    :param can_dirty: Any CAN
    :return: Canonical DB-formatted CAN.
    """
    can_dirty = str(can_dirty)

    # drop all non-digits
    can = ''.join(ch for ch in can_dirty if ch.isdigit())

    if len(can) != 16:
        raise ValueError('Invalid CAN length')

    return can


def get_user_by_can(can_dirty):
    """
    Get a user by card number
    :param can_dirty: str
    :return: {user info} or None
    """
    with records.Database(DATABASE_URL) as db:
        first_row = db.query('''
            SELECT id, can, name, display_name, phone_number, active
            FROM Users WHERE can = :can;
        ''', can=transform_can_to_canonical(can_dirty)).first()

        return first_row.as_dict() if first_row is not None else None


def get_user_items(user_id):
    """
    Get a user's deposited items, most recent first
    :param user_id: the user's id
    :return: a list of Record types
    """
    with records.Database(DATABASE_URL) as db:
        return db.query('''
            SELECT id, score, mass, category, deposited_by, created_at,
              extra_info
            FROM Items
            WHERE deposited_by = :user_id
            ORDER BY id DESC;
        ''', user_id=user_id).all()


def get_leaderboard(limit=10):
    """
    Get the leaderboard. Returns first 10 rows only!
    champion = get_leaderboard()[0]['display_name'] -> top user
    :param limit: Where to cut off the leaderboard (show the top <limit> users)
    :return a list of Record types
    """
    limit = int(limit)
    with records.Database(DATABASE_URL) as db:
        return db.query('''
            SELECT Users.id, Users.name, Users.display_name,
              IFNULL(It.score_sum, 0) AS score_sum
            FROM Users
            LEFT JOIN (
              SELECT SUM(Items.score) As score_sum, Items.deposited_by
              FROM Items
              GROUP BY Items.deposited_by
            ) AS It
            ON It.deposited_by = Users.id
            ORDER BY It.score_sum DESC
            LIMIT :limit;
        ''', limit=limit).all()


def create_user(can, name, display_name, phone_number, active=True):
    """
    Create a new user.
    :param can: CAN (compulsory)
    :param name: Username (not compulsory)
    :param display_name: Friendly name for display on UI (compulsory)
    :param phone_number: Phone number for push notifs (not compulsory)
    :param active: Is active (defaults to True)
    :return: Id of new user or False if couldn't create
    """
    params = {
        'can': transform_can_to_canonical(can),
        'name': str(name),
        'display_name': str(display_name),
        'phone_number': str(phone_number),
        'active': bool(active)
    }

    with records.Database(DATABASE_URL) as db:
        try:
            db.query('''
                INSERT INTO Users (can, name, display_name, phone_number, active)
                VALUES (:can,:name,:display_name,:phone_number,:active);
            ''', **params)

            # second round trip is terribly expensive but records is so cool...
            return db.query('SELECT last_insert_id() AS id;').first()['id']
        except IntegrityError as e:
            print('IntegrityError! {}'.format(repr(e)))
            return False

def create_item(score, mass, category, deposited_by, created_at=None,
                extra_info=None):
    """
    Create a new deposited item.
    :param created_at: Datetime of creation (if not specified just defaults to
    server time)
    :param score: Score int
    :param mass: Mass int
    :param category: Category int
    :param deposited_by: User ID of depositing user
    :param extra_info: Extra info in JSON format
    :return: Id of new item or False if create failed
    """
    # Only one None of type NoneType - same effect as ... is None
    if not isinstance(extra_info, (str, type(None))):
        raise ValueError('extra_info isn\'t a str or None')

    params = {
        'score': int(score),
        'mass': int(mass),
        'category': int(category),
        'deposited_by': int(deposited_by),
        'created_at': created_at or datetime.now(),
        'extra_info': extra_info
    }

    with records.Database(DATABASE_URL) as db:
        try:
            db.query('''
                INSERT INTO Items (score, mass, category, deposited_by,
                  created_at, extra_info)
                VALUES (:score,:mass,:category,:deposited_by,:created_at,
                  :extra_info);
            ''', **params)

            return db.query('SELECT last_insert_id() AS id;').first()['id']
        except IntegrityError as e:
            print('IntegrityError! {}'.format(repr(e)))
            return False
