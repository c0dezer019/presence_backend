from arrow import get
from core.models import db
from core.models import Guild


def resolve_create_guild(obj, info, **kwargs):
    try:
        guild = Guild(**kwargs)

        db.session.add(guild)
        db.session.commit()

        payload = {"code": 200, "guild": guild.as_dict()}

    except ValueError as e:
        payload = {
            "code": 400,
            "errors": [
                "You stuck up, half-witted, scruffy-looking nerf herder! You provided me with incorrect data!",
                str(e),
            ],
        }

    return payload


def resolve_guilds(obj, info):
    try:
        guilds = [guild.as_dict() for guild in Guild.query.all()]

        if guilds:
            payload = {"code": 200, "guilds": guilds}
        else:
            payload = {"code": 404, "errors": ["No guilds could be found."]}

    except AttributeError as e:
        payload = {"code": 404, "errors": ["No guilds could be found", str(e)]}

    except Exception as error:
        payload = {"code": 500, "errors": str(error)}

    return payload


def resolve_guild(obj, info, guild_id):
    try:
        guild = Guild.query.filter_by(guild_id=guild_id).first()

        payload = {
            "code": 200,
            "guild": guild.as_dict(),
        }

    except AttributeError as e:
        payload = {
            "code": 404,
            "errors": [f"Guild matching id {guild_id} cannot be found.", str(e)],
        }

    except ValueError as e:
        payload = {
            "code": 400,
            "errors": [
                "You stuck up, half-witted, scruffy-looking nerf herder! You provided me with incorrect data!",
                str(e),
            ],
        }

    return payload


def resolve_update_guild(obj, info, guild_id, **data):
    try:
        guild = Guild.query.filter_by(guild_id=guild_id).first()

        for k, v in data.items():
            if k == "last_activity_ts":
                v = get(v).to("US/Central").datetime

            setattr(guild, k, v)

        db.session.add(guild)
        db.session.commit()

        payload = {
            "code": 200,
            "success_msg": f"Guild matching id {guild_id} has been modified.",
            "guild": guild.as_dict(),
        }

    except AttributeError as e:
        payload = {
            "code": 404,
            "errors": [f"Guild matching id {guild_id} was unable to be found.", str(e)],
        }

    except ValueError as e:
        payload = {
            "code": 400,
            "errors": [
                "You stuck up, half-witted, scruffy-looking nerf herder! You provided me with incorrect data!",
                str(e),
            ],
        }

    except TypeError as e:
        payload = {
            "code": 500,
            "errors": ["Bot tried to do something obscene with an object.", str(e)],
        }

    return payload


def resolve_delete_guild(obj, info, guild_id):
    try:
        guild = Guild.query.filter_by(guild_id=guild_id).first()

        db.session.delete(guild)
        db.session.commit()

        payload = {
            "code": 200,
            "success_msg": f"Guild matching id {guild_id} has successfully been deleted.",
        }

    except AttributeError as e:
        payload = {
            "code": 404,
            "errors": [f"Guild matching id {guild_id} could not be found.", str(e)],
        }

    return payload
