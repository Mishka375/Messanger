# 100
class RedisError (Exception):
    pass

# 101
class RedisDataError (Exception):
    pass

# 102
class RedisTimeoutError (Exception):
    pass

# 103
class RedisBusyError (Exception):
    pass





# 200
class SQLError (Exception):
    pass

# 201
class SQLValueExist (Exception):
    pass

# 202
class SQLValueIsNull (Exception):
    pass

# 203
class SQLRequestError (Exception):
    pass

# 204
class SQLDataError (Exception):
    pass





# 300
class IncorrectData (Exception):
    pass

# 301
class IncorrectLogin (Exception):
    pass

# 302
class IncorrectEnter (Exception):
    pass

# 303
class IncorrectKey (Exception):
    pass

# 304
class IncorrectConnect (Exception):
    pass





# 400
class ChatError (Exception):
    pass
