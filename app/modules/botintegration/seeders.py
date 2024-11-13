from core.seeders.BaseSeeder import BaseSeeder


class TreeNodeSeeder(BaseSeeder):
    """
    Seeder for creating TreeNode records with high priority.
    """
    priority = 1  # High priority

    def run(self):
        """
        Defines the data to be seeded and seeds it.
        """
        data = [
            # Add the model objects or dictionaries representing the seed data here
        ]

        # Call the seed method from the parent class to persist the data
        self.seed(data)
