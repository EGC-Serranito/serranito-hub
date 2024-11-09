from app import db

class TreeNode(db.Model):
    __tablename__ = 'tree_nodes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tree_nodes.id', ondelete='CASCADE'))  # Cascade delete
    path = db.Column(db.String(512), nullable=False)
    single_child = db.Column(db.Boolean, default=False)

    # Relación con el modelo TreeNode, configurando single_parent=True para que solo tenga un padre
    parent = db.relationship("TreeNode", backref="children", remote_side=[id], cascade="all, delete-orphan", single_parent=True)
    
    user = db.relationship('User', backref='tree_nodes', lazy=True)

    def __repr__(self):
        return f'TreeNode<{self.id}, Name={self.name}, User={self.user.username}, Parent={self.parent_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children]
        }    

    

class TreeNodeBot(db.Model):
    __tablename__ = 'treenode_bot'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('treenode_bot.id', ondelete='CASCADE'))  # Cascade delete
    path = db.Column(db.String(512), nullable=False)
    single_child = db.Column(db.Boolean, default=False)

    # Relación con el modelo TreeNodeBot, configurando single_parent=True para que solo tenga un padre
    parent = db.relationship("TreeNodeBot", backref="children", remote_side=[id], cascade="all, delete-orphan", single_parent=True)
    
    def __repr__(self):
        return f'TreeNodeBot<{self.id}, Name={self.name}, Parent={self.parent_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children]
        }    