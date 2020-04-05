# import datetime
#
# from data import db_session
# from data.users import User
# from flask import Flask, jsonify
# from flask_restful import abort, Api, Resource
# from flask_restful import reqparse
#
# app = Flask(__name__)
# api = Api(app)
#
# parser = reqparse.RequestParser()
# parser.add_argument('surname', required=True)
# parser.add_argument('name', required=True)
# parser.add_argument('age', required=True, type=int)
# parser.add_argument('position', required=True)
# parser.add_argument('speciality', required=True)
# parser.add_argument('address', required=True)
# parser.add_argument('email', required=True)
# parser.add_argument('city_from', required=True)
# parser.add_argument('password', required=True)
#
#
# def abort_if_user_not_found(user_id):
#     session = db_session.create_session()
#     users = session.query(User).get(user_id)
#     if not users:
#         abort(404, message=f"Users {user_id} not found")
#
#
# class UsersResource(Resource):
#     def get(self, user_id):
#         abort_if_user_not_found(user_id)
#         session = db_session.create_session()
#         user = session.query(User).get(user_id)
#         return jsonify({'users': user.to_dict()})
#
#     def delete(self, user_id):
#         abort_if_user_not_found(user_id)
#         session = db_session.create_session()
#         user = session.query(User).get(user_id)
#         session.delete(user)
#         session.commit()
#         return jsonify({'success': 'OK - user deleted'})
#
#
# class UsersListResource(Resource):
#     def get(self):
#         session = db_session.create_session()
#         users = session.query(User).all()
#         return jsonify({'users': [item.to_dict() for item in users]})
#
#     def post(self):
#         args = parser.parse_args()
#         session = db_session.create_session()
#         users = User(
#             surname=args['surname'],
#             name=args['name'],
#             age=args['age'],
#             address=args['address'],
#             email=args['email'],
#         )
#         users.set_password(args['password'])
#         session.add(users)
#         session.commit()
#         return jsonify({'success': 'OK - the user has been added'})
