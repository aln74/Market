from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    #return User.get(user_id)

class User(db.Model, UserMixin): #UserMixin helps with the User class as required by Flask
    id = db.Column(db.Integer(), primary_key=True) #sets the ID automatically!
    username = db.Column(db.String(length=35), unique=True, nullable=False)
    email_address = db.Column(db.String(length=60), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def format_budget(self):
        if len(str(self.budget)) >= 4:
            num = []
            num[:] = str(self.budget)
            counter = 0
            for i in num[::-1]:
                counter += 1
                if not counter % 3:
                    pos = len(str(self.budget)) - counter
                    num.insert(pos, ',')
            return ''.join(num)
        else:
            return f'{self.budget}'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items #checks if the user actually owns the object

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True) #sets the ID automatically!
    name = db.Column(db.String(length=35), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1200), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id')) #lowercase!

    def __repr__(self):
        return f'Item {self.name}'