import random

from locust import HttpUser, between, task


class DiaryUser(HttpUser):
    # Задержка между действиями от 1 до 3 секунд
    wait_time = between(1, 3)

    def on_start(self):
        """
        1. Логинимся
        2. Создаем локальный список для хранения ID заметок этого конкретного юзера
        """
        self.created_note_ids = []

        # Данные тестового пользователя, который уже заведен в БД
        login_payload = {
            "username": "testuser",  #
            "password": "password123",  #
        }

        response = self.client.post(
            "/auth/login", json=login_payload, name="Auth: Login"
        )
        if response.status_code != 200:
            print(f"Ошибка входа: {response.status_code} - {response.text}")

    @task(5)
    def get_all_notes(self):
        """
        Самый частый сценарий: пользователь просто открывает список всех заметок.
        """
        self.client.get("/notes/", name="Notes: Get All")

    @task(3)
    def create_note(self):
        """
        Создание заметки. Твой эндпоинт возвращает 201 Created и JSON с объектом NoteResponse.
        Мы забираем id созданной заметки и сохраняем его себе в массив.
        """
        payload = {
            "title": f"Заметка {random.randint(1000, 9999)}",
            "content": "Тестовый контент нагрузочного тестирования",
        }

        with self.client.post(
            "/notes/", json=payload, name="Notes: Create", catch_response=True
        ) as response:
            if response.status_code == 201:
                # Извлекаем ID только что созданной заметки
                note_data = response.json()
                note_id = note_data.get("id")
                if note_id:
                    self.created_note_ids.append(note_id)
                response.success()
            else:
                response.failure(f"Не удалось создать заметку: {response.status_code}")

    @task(2)
    def get_single_note(self):
        """
        Чтение конкретной заметки по ID (если юзер уже успел что-то создать).
        """
        if not self.created_note_ids:
            return  # Пропускаем, если пользователь еще не создал ни одной заметки

        note_id = random.choice(self.created_note_ids)
        self.client.get(f"/notes/{note_id}", name="Notes: Get Single")

    @task(1)
    def update_note(self):
        """
        Обновление заметки по PATCH.
        """
        if not self.created_note_ids:
            return

        note_id = random.choice(self.created_note_ids)
        payload = {"title": f"Обновленный заголовок {random.randint(1, 100)}"}
        self.client.patch(f"/notes/{note_id}", json=payload, name="Notes: Update")

    @task(1)
    def delete_note(self):
        """
        Удаление заметки. Твой эндпоинт возвращает 204 NO CONTENT.
        """
        if not self.created_note_ids:
            return

        # Достаем ID и удаляем его из нашего локального списка
        note_id = self.created_note_ids.pop()

        with self.client.delete(
            f"/notes/{note_id}", name="Notes: Delete", catch_response=True
        ) as response:
            if response.status_code == 204:
                response.success()
            else:
                response.failure(
                    f"Ошибка удаления ({response.status_code}): {response.text}"
                )
