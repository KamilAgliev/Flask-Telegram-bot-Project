from requests import get, delete, post, put

# Ввывод всех пользователей
# print(get('http://localhost:5000/api/users').json())
# # Вывод одного пользователя
# print(get('http://localhost:5000/api/users/1').json())
# # Удаление пользователя
# print(delete('http://localhost:5000/api/users/4').json())
# # Не правильный запрос параметр age пропущен
# print(post('http://127.0.0.1:5000/api/users',
#            json={'id': 3, 'name': 'Almaz', 'surname': 'Almazov',
#                  'email': 'almaz@mail.ru', 'password': 'test',
#                  'address': 'Almet'}, ).json())
# Правильный запрос
print(post('http://127.0.0.1:5000/api/users', json={
    'name': 'Almaz',
    'surname': 'Almazov',
    'email': 'almaz@mail.ru',
    'password': 'test',
    'address': 'Almet',
    "age": 34
}).json())
