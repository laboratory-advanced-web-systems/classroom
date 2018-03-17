import datetime

from flask import request, session, render_template
from bson.objectid import ObjectId

from classroom import app
from classroom import db


#registrando pedido para entrar em turma
@app.route("/classroom/invites/<invite_id>/", methods=["GET"])
def accept_invite(invite_id):
    try:
        invite = db.invites.find_one( {"_id": ObjectId(invite_id)} )
        user = db.users.find_one( {"_id": invite["user"]["_id"]} )

        db.classes.update({"_id": invite["class"]["_id"]}, {"$addToSet": {"participants": user["_id"]}})

        db.invite.remove({"_id": invite_id})
    except Exception as error:
        print(error)

    return "OK"

#apagando convite para entrar em turma
@app.route("/classroom/invites/<invite_id>/", methods=["DELETE"])
def refuse_invite(invite_id):
    try:
        db.invites.remove({"_id": ObjectId(invite_id)})
    except Exception as e:
        print(e)

    return "OK"


#registrando pedido para entrar em turma
@app.route("/classroom/classes/<class_id>/invites/", methods=["POST"])
def send_invite(class_id):
    try:
        user = db.users.find_one( {"_id": ObjectId(session["_id"])} )
        classe = db.classes.find_one( {"_id": ObjectId(class_id)} )

        db.invites.insert({
            "user": user,
            "class": classe
        })
    except:
        return "Error"

    return "OK"


@app.route("/classroom/user/<user_id>/classes/<class_id>/", methods=["GET"])
def get_index_student(class_id, user_id):
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    classe = db.classes.find_one({"_id": ObjectId(class_id)})
    tasks = db.tasks.find({
        "class._id": classe["_id"],
        "deadline" : { "$gte" : date }
    }).sort([("deadline", -1)])

    user = db.users.find_one({"_id": ObjectId(session["_id"])})

    return render_template("classes/student.html", c=classe, tasks=tasks, user=user)


#Criando uma nova turma
@app.route("/classroom/classes/", methods=["POST"])
def create_class():
    name = request.form.get("name")
    description = request.form.get("description")
    creator = db.users.find_one( {"email": session["email"]} )
    participants = []

    db.classes.insert( {
        "name": name,
        "description": description,
        "creator": creator,
        "participants": participants
    } )

    return "OK"

#redirecionando para painel de gerenciamento de turmas
@app.route("/classroom/classes/<class_id>/", methods=["GET"])
def get_class(class_id):
    c = db.classes.find_one( {"_id": ObjectId(class_id)} )

    tasks = db.tasks.find({"class._id": c["_id"]}).sort([("deadline", -1)])

    invites = db.invites.find({"class._id": c["_id"]})

    return render_template("classes/index.html", c=c, tasks=tasks, invites=invites)


#removendo turma
@app.route("/classroom/classes/<class_id>/", methods=["DELETE"])
def delete_class(class_id):
    db.classes.remove({"_id": ObjectId(class_id)})

    return "OK"


#atualizando turma
@app.route("/classroom/classes/<class_id>/", methods=["PUT"])
def update_class(class_id):
    name = request.form.get("name")
    description = request.form.get("description")

    db.classes.update({"_id": ObjectId(class_id)}, {"$set": {"name": name, "description": description}})

    return "OK"

@app.route("/classroom/classes/<class_id>/participants/", methods=["PUT"])
def add_participant(class_id):
    email = request.form.get("email")

    user = db.users.find_one({"email": email})

    db.classes.update({"_id": ObjectId(class_id)}, {"$addToSet": {"participants": user["_id"]}})

    return "OK"
