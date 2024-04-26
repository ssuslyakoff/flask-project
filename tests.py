from requests import get, post, delete


# для запроса на скачивание файла
ans = get('http://127.0.0.1:8080/api/download/scott_chief@mars.org/photo2', json={'password': '12345'})
print(ans)

# для запроса на загрузку файла
file_path = r'путь_к_твоим_файликам'
with open(file_path, 'rb') as file:
    files = {'file': file, 'password': '12345'}
    print(post('http://127.0.0.1:8080/api/upload/scott_chief@mars.org', files=files))

# для запроса на удаление файла
print(post('http://127.0.0.1:8080/api/delete/scott_chief@mars.org/cat', json={'password': '12345'}))

# для запроса на переименование файла
print(post('http://127.0.0.1:8080/api/rename/scott_chief@mars.org/photo/photo2', json={'password': '12345', 'new_filename': 'cat2'}))
