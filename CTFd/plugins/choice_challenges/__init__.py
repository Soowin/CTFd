from __future__ import division  # Use floating point for math calculations
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.flags import get_flag_class
from CTFd.models import (
    db,
    Solves,
    Fails,
    Flags,
    Challenges,
    ChallengeFiles,
    Tags,
    Hints,
)
from CTFd.utils.user import get_ip
from CTFd.utils.uploads import delete_file
from CTFd.utils.modes import get_model
from flask import Blueprint
import math


class ChoiceValueChallenge(BaseChallenge):
    id = "choice"  # Unique identifier used to register challenges
    name = "choice"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/choice_challenges/assets/create.html",
        "update": "/plugins/choice_challenges/assets/update.html",
        "view": "/plugins/choice_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/choice_challenges/assets/create.js",
        "update": "/plugins/choice_challenges/assets/update.js",
        "view": "/plugins/choice_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/choice_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "choice_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()
        challenge = ChoiceChallenge(**data)

        db.session.add(challenge)
        db.session.commit()

        return challenge

    @staticmethod
    def read(challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = ChoiceChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "content1": challenge.content1,
            "content2": challenge.content2,
            "content3": challenge.content3,
            "content4": challenge.content4,
            "description": challenge.description,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": ChoiceValueChallenge.id,
                "name": ChoiceValueChallenge.name,
                "templates": ChoiceValueChallenge.templates,
                "scripts": ChoiceValueChallenge.scripts,
            },
        }
        return data

    @staticmethod
    def update(challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            # if attr in ("content1", "content2", "content3", "content4"):
            #     value = (value)
            setattr(content1, content2, content3, content4)

        Model = get_model()

        # solve_count = (
        #     Solves.query.join(Model, Solves.account_id == Model.id)
        #     .filter(
        #         Solves.challenge_id == challenge.id,
        #         Model.hidden == False,
        #         Model.banned == False,
        #     )
        #     .count()
        # )

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        # value = (
        #     ((challenge.minimum - challenge.initial) / (challenge.decay ** 2))
        #     * (solve_count ** 2)
        # ) + challenge.initial

        # value = math.ceil(value)

        # if value < challenge.minimum:
        #     value = challenge.minimum

        # challenge.value = value

        db.session.commit()
        return challenge

    @staticmethod
    def delete(challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        ChoiceChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def attempt(challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        try:
            submission = data["submission"].strip()
        except AttributeError as identifier:
            submission = 'e'
        
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            if get_flag_class(flag.type).compare(flag, submission):
                return True, "Correct"
        return False, "Incorrect"

    @staticmethod
    def solve(user, team, challenge, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        chal = ChoiceChallenge.query.filter_by(id=challenge.id).first()
        data = request.form or request.get_json()
        submission = data["submission"].strip()

        Model = get_model()

        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(solve)
        db.session.commit()
        db.session.close()

    @staticmethod
    def fail(user, team, challenge, request):
        """
        This method is used to insert Fails into the database in order to mark an answer incorrect.

        :param team: The Team object from the database
        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        wrong = Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=submission,
        )
        db.session.add(wrong)
        db.session.commit()
        db.session.close()


class ChoiceChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "choice"}
    id = db.Column(None, db.ForeignKey("challenges.id"), primary_key=True)
    content1 = db.Column(db.String(80), default="null")
    content2 = db.Column(db.String(80), default="null")
    content3 = db.Column(db.String(80), default="null")
    content4 = db.Column(db.String(80), default="null")

    def __init__(self, *args, **kwargs):
        super(ChoiceChallenge, self).__init__(**kwargs)
        self.initial = kwargs["value"]


def load(app):
    # upgrade()
    app.db.create_all()
    CHALLENGE_CLASSES["choice"] = ChoiceValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/choice_challenges/assets/"
    )
