from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def explore_home(self):
        print("Simulando solicitud a /explore...")
        response = self.client.get("/explore")
        if response.status_code == 200:
            print("Página de Explore cargada exitosamente.")
        else:
            print(f"Error al cargar la página de Explore, código de estado: {response.status_code}")

    @task(2)
    def explore_with_filters(self):
        print("Simulando búsqueda con filtros...")

        params = {
            "query": "variable",
            "sorting": "newest",
            "publication_type": "any"
        }

        print(f"Parámetros de filtro: {params}")

        tags = ["tag1", "tag2"]
        for tag in tags:
            print(f"Agregando etiqueta: {tag} a los filtros de búsqueda.")
            params['tags'] = tag
            response = self.client.get("/explore", params=params)
            if response.status_code == 200:
                print(f"Página de Explore con filtros (etiquetas: {tags}) cargada exitosamente.")
            else:
                print(f"Error al cargar la página de Explore con filtros, código de estado: {response.status_code}")
