from app import db


class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Download<{self.id}>'
