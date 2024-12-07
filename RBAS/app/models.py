from app import db
import datetime


class UserPermission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship to users
    users = db.relationship('User', back_populates='user_role', cascade='all, delete-orphan')

    @classmethod
    def create_initial_roles(cls):
        """
        Create initial roles if they don't exist
        """
        roles = ['admin', 'bulk', 'tanker']
        
        for role in roles:
            existing_role = cls.query.filter_by(role=role).first()
            if not existing_role:
                new_role = cls(role=role)
                db.session.add(new_role)
        
        db.session.commit()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    # Foreign key to UserPermission
    role_id = db.Column(db.Integer, db.ForeignKey('user_permission.id'), nullable=False)
    
    # Relationship to UserPermission
    user_role = db.relationship('UserPermission', back_populates='users')

    # Convenience property to get role name
    @property
    def role(self):
        return self.user_role.role if self.user_role else None # 'admin', 'bulk', or 'tanker'


    @classmethod
    def create_initial_roles(cls):
        """
        Create initial roles if they don't exist
        """
        roles = ['admin', 'bulk', 'tanker']
        
        for role in roles:
            existing_role = cls.query.filter_by(role=role).first()
            if not existing_role:
                new_role = cls(role=role)
                db.session.add(new_role)
        
        db.session.commit()


class GroupData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_type = db.Column(db.String(10), nullable=False)  # 'bulk' or 'tanker'
    data = db.Column(db.JSON, nullable=False)  # Store data as JSON
    fetched_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
