import os
import uuid

from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from Services.s3 import S3Service
from Services.ses import SESService
from Services.wise import WiseService
from constants import TEMP_FILE_FOLDER
from db import db
from managers.auth import AuthManager
from models import RoleType, UserModel, ComplaintModel, State, TransactionModel
from utils.helpers import decode_photo

wise_service = WiseService()
s3 = S3Service()
ses = SESService()

class ComplainerManager:
    @staticmethod
    def login(data):
        user = db.session.execute(db.select(UserModel).filter(UserModel.email == data['email'])).scalar()
        if user and check_password_hash(user.password, data['password']):
            return AuthManager.encode_token(user)
        raise Unauthorized()

    @staticmethod
    def register(complainer_data):
        """Hashes the plain password:param complainer_data: dict:return: complainer"""
        complainer_data['password'] = generate_password_hash(complainer_data['password'], method='pbkdf2:sha256')
        complainer_data['role'] = RoleType.complainer.name
        complainer = UserModel(**complainer_data)
        try:
            db.session.add(complainer)
            db.session.flush()
            ses.send_email(recipient=complainer_data['email'],
                           subject=f"Welcome, {complainer_data['first_name']}{complainer_data['last_name']}",
                           content="Welcome to our complain system.You can now login and submit complains.")
            return AuthManager.encode_token(complainer)
        except Exception as ex:
            raise BadRequest(str(ex))

    @staticmethod
    def get_claims(user):
        query = db.select(ComplaintModel)
        if user.role.complainer == RoleType.complainer:
            query = query.filter_by(complainer_id=user.id)
        return db.session.execute(query).scalars().all()

    @staticmethod
    def create(user, data):
        data["complainer_id"] = user.id
        photo = data.pop('photo')
        extension = data.pop('photo_extension')
        key = f"{uuid.uuid4()}.{extension}"
        full_file_path = os.path.join(TEMP_FILE_FOLDER, key)
        decode_photo(full_file_path, photo)
        url = s3.upload_photo(full_file_path, key, extension)
        data["photo_url"] = url
        complaint = ComplaintModel(**data)
        db.session.add(complaint)
        db.session.flush()
        ComplainerManager.issue_transaction(data["amount"], user.first_name, user.last_name, user.iban)

    @staticmethod
    def approve(complaint_id):
        complaint = db.session(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()
        if not complaint:
            raise NotFound(f"Complaint with id {complaint_id} does not exist")
        transaction = db.session.execute(db.select(TransactionModel).filter_by(complaint_id=complaint_id).scalar())
        wise_service.fund_transfer(transaction.transaction_id)
        complaint.status = State.approved
        db.session.add(complaint)
        db.session.flush()
        # db.session.execute(db.update(ComplaintModel).where(ComplaintModel.id == complaint_id).values(status=State.approved))


    @staticmethod
    def reject(complaint_id):
        complaint = db.session(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()
        if not complaint:
            raise NotFound(f"Complaint with id {complaint_id} does not exist")
        transaction = db.session.execute(db.select(TransactionModel).filter_by(complaint_id=complaint_id).scalar())
        wise_service.cancel_transfer(transaction.transaction_id)
        complaint.status = State.rejected
        db.session.add(complaint)
        db.session.flush()

        # db.session.execute(db.update(ComplaintModel).where(ComplaintModel.id == complaint_id).values(status=State.rejected))


    @staticmethod
    def delete(complaint_id):
        # complaint = db.session(db.select(ComplaintModel).filter_by(id=complaint_id).scalar())
        # if not complaint:
        #     raise NotFound(f"Complaint wit id {complaint_id} does not exist.")
        # db.session.delete(complaint)
        # db.session.flush()
        db.session.execute(db.delete(ComplaintModel).where(ComplaintModel.id == complaint_id))

    @staticmethod
    def issue_transaction(amount, first_name, last_name, iban, complaint_id):
        quote = wise_service.create_quote(amount)
        recipient = wise_service.create_recipient(first_name, last_name, iban)
        transfer = wise_service.create_transfer(recipient["id"], quote["id"])
        t = TransactionModel(quote_id=quote["id"], transfer_id=transfer["id"], target_account_id=recipient["id"], amount=amount, complaint_id=complaint_id)
        db.session.add(t)
        db.session.flush()

