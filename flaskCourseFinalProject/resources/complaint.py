from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.complainer import ComplainerManager
from models import RoleType
from schemas.response.complaint import ComplaintResponseSchema
from utils.decorators import permission_required, validate_schema


class Complaint(Resource):
    @auth.login_required
    def get(self):
        user = auth.current_user()
        complaints = ComplainerManager.get_claims(user)
        return {'complaints': ComplaintResponseSchema().dump(complaints, many=True)}

    @auth.login_required
    @permission_required(RoleType.complainer)
    @validate_schema(ComplaintResponseSchema)
    def post(self):
        data = request.get_json()
        user = auth.current_user()
        ComplainerManager.create(user, data)
        return 201


class ComplaintApproved(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.approve(complaint_id)
        return 204


class ComplaintRejected(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.reject(complaint_id)
        return 204


class ComplaintDetail(Resource):
    @auth.login_required
    @permission_required(RoleType.admin)
    def delete(self, complaint_id):
        ComplainerManager.delete(complaint_id)
        return 204
