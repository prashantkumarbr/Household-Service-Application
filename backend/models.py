from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User_Info(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, default=1)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default='Active')
    service_requests = db.relationship("Service_Request", cascade="all,delete", backref="user_info", lazy=True)
    review = db.relationship("Review", cascade="all,delete", backref="user_info")


class Service_Professional(db.Model):
    __tablename__ = "service_professional"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, default=2)
    service_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Pending')
    service_requests = db.relationship("Service_Request", backref="professional", lazy=True)


class Service(db.Model):
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.String, nullable=False)
    service_requests = db.relationship("Service_Request", backref="service", lazy=True)


class Service_Request(db.Model):
    __tablename__ = "service_request"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("service_professional.id"))
    date_of_request = db.Column(db.Date, nullable=False)
    date_of_completion = db.Column(db.Date, nullable=True)
    status = db.Column(db.String, default='Requested')
    description = db.Column(db.String, nullable=False)
    review = db.relationship("Review", uselist=False, backref="service_request")


class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("service_professional.id"), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey("service_request.id"), unique=True)
    rating = db.Column(db.Float, db.CheckConstraint('rating BETWEEN 1 AND 5'), default=0.0)
    description = db.Column(db.String, nullable=False)
