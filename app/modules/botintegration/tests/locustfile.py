from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class BotIntegrationBehavior(TaskSet):
    def on_start(self):
        """Esta función se ejecuta al inicio de la simulación."""
        self.login()

    def login(self):
        """Realiza el login en la aplicación para obtener acceso autenticado."""
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)
        self.client.post(
            "/login",
            data={"username": "test_user", "password": "test_pass", "csrf_token": csrf_token}
        )

    @task
    def index_page(self):
        """Carga la página principal de integración de bots."""
        response = self.client.get("/botintegration")
        get_csrf_token(response)

    @task
    def add_bot(self):
        """Prueba la funcionalidad de agregar un bot."""
        response = self.client.get("/botintegration/add-bot")
        csrf_token = get_csrf_token(response)
        self.client.post(
            "/botintegration/add-bot",
            data={"name": "TestBot", "parent_id": "", "csrf_token": csrf_token}
        )

    @task
    def add_chat(self):
        """Prueba la funcionalidad de agregar un chat."""
        response = self.client.get("/botintegration/add-chat")
        csrf_token = get_csrf_token(response)
        self.client.post(
            "/botintegration/add-chat",
            data={"name": "TestChat", "parent_id": "", "csrf_token": csrf_token}
        )

    @task
    def add_feature(self):
        """Prueba la funcionalidad de agregar una característica."""
        response = self.client.get("/botintegration/add-feature")
        csrf_token = get_csrf_token(response)
        self.client.post(
            "/botintegration/add-feature",
            data={"name": "TestFeature", "parent_id": "", "csrf_token": csrf_token}
        )

    @task
    def delete_node(self):
        """Prueba la funcionalidad de eliminar un nodo."""
        node_id = 1  # ID de nodo de prueba
        response = self.client.post(f"/botintegration/delete/{node_id}")
        get_csrf_token(response)

    @task
    def merge_node(self):
        """Prueba la funcionalidad de fusionar nodos."""
        node_id = 1  # ID de nodo de prueba
        response = self.client.post(f"/botintegration/merge/{node_id}")
        get_csrf_token(response)

    @task
    def save_node_states(self):
        """Prueba la funcionalidad de guardar el estado de los nodos."""
        self.client.post(
            "/save_node_states",
            json={"open_nodes": [1, 2, 3]}  # Ejemplo de nodos abiertos
        )


class BotIntegrationUser(HttpUser):
    tasks = [BotIntegrationBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
