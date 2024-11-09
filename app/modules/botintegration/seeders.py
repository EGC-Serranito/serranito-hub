from app import db
from app.modules.auth.models import User
from app.modules.botintegration.models import TreeNode
from core.seeders.BaseSeeder import BaseSeeder

class TreeNodeSeeder(BaseSeeder):
    priority = 1  # Prioridad alta

    def run(self):

        data = [
            # Create any Model object you want to make seed
        ]

        self.seed(data)