import redis

r = redis.Redis(host='192.168.1.23', port=6379, db=0)

try:
    response = r.ping()
    print("连接成功:", response)
except redis.exceptions.ConnectionError as e:
    print("连接失败:", e)
