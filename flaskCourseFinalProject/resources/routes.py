from resources.auth import RegisterComplainer, LoginComplainer, Password
from resources.complaint import Complaint, ComplaintApproved, ComplaintRejected, ComplaintDetail
from resources.user import User

routes = (
    (RegisterComplainer, "/register"),
    (LoginComplainer, "/login"),
    (Complaint, "/complainers/complaints"),
    (ComplaintApproved, "/approver/complaints/<int:complaint_id>/approved"),
    (ComplaintRejected, "/approver/complaints/<int:complaint_id>/rejected"),
    (User, "/admins/users"),
    (Password, "/users/change-password"),
    (ComplaintDetail, "/admins/complaints/<int:complaint_id>")
)