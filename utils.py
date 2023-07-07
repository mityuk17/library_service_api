import hashlib


def get_password_hash(password: str):
    cypher = hashlib.sha256()
    cypher.update(password.encode('utf8'))
    password_hash = cypher.hexdigest()
    return password_hash


