from app.modules.download.repositories import DownloadRepository
from core.services.BaseService import BaseService


class DownloadService(BaseService):
    def __init__(self):
        super().__init__(DownloadRepository())
