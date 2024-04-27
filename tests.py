from requests import get, post


# для запроса на скачивание файла
ans = get('http://127.0.0.1:8080/api/download/gmail_пользователя/файл_пользователя', json={'password': '12345'})
print(ans)

# для запроса на загрузку файла
file_path = r'путь/к/твоим/файликам'
with open(file_path, 'rb') as file:
    files = {'file': file, 'password': '12345'}
    print(post('http://127.0.0.1:8080/api/upload/gmail_пользователя', files=files))

# для запроса на удаление файла
print(post('http://127.0.0.1:8080/api/delete/gmail_пользователя/файл_пользователя', json={'password': '12345'}))

# для запроса на переименование файла
print(post('http://127.0.0.1:8080/api/rename/gmail_пользователя/старое_название/новое_название', json={'password': '12345', 'new_filename': 'cat2'}))
