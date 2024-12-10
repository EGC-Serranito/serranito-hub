from core.seeders.BaseSeeder import BaseSeeder


class TreeNodeSeeder(BaseSeeder):
    """
    Seeder for creating TreeNode records with high priority.
    """
    priority = 1

    def run(self):
        """
        Defines the data to be seeded and seeds it.
        """
        data = [

        ]

        self.seed(data)
