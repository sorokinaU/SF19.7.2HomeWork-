from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()

def test_get_api_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

def test_add_new_pet_with_valid_data(name='Капитоша', animal_type='корниш-рекс',
                                     age='11', pet_photo='images/my_cat2.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/my_cat.jpeg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("Здесь нет моих питомцев")

def test_get_api_key_for_invalid_password(email = valid_email, password = invalid_password):
    '''проверяем что система выдаёт ошибку на стороне пользователя, когда вводится невалидный пароль'''
    status, result = pf.get_api_key(email, password)
    assert status == 403

def test_get_all_pets_with_invalid_key(filter = ''):
    '''проверяем что система выдаёт ошибку на стороне пользователя, когда вводится невалидный ключь авторизации'''
    auth_key = {'key': "vhdkrj65576jmkvnlkjgbn"}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403

def test_get_api_key_for_invalid_email(email = invalid_email, password = valid_password):
    '''проверяем что система выдаёт ошибку на стороне пользователя, когда вводится невалидная почта'''
    status, result = pf.get_api_key(email, password)
    assert status == 403


def test_unsuccessful_update_self_pet_info_invalid_key(name = 'Gerda', animal_type = "sobaka", age = 1):
    auth_key = {'key': "kfbjkldshjt6433"}
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
    assert status == 403
    #Здесь пойман баг: auth_key невалидный. Тест должен выдать ошибку 403, а по факту возвращает код 200

def test_add_new_pet_with_invalid_data(name='Зая', animal_type='грызун',
                                     age='fghjja', pet_photo='images/my_cat.jpeg'):
    """Проверяем что можно добавить питомца с некорректными данными"""


    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 400
    #Здесь пойман баг: с данными str в age (age='fghjja') должен выдать ошибку 400, а по факту возвращает код 200

