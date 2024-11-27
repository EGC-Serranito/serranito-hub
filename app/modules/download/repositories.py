from app.modules.download.models import Download
from core.repositories.BaseRepository import BaseRepository


class DownloadRepository(BaseRepository):
    def __init__(self):
        super().__init__(Download)
