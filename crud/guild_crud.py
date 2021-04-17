from datetime import datetime
from flask import jsonify
from main.models import db
from main.models import Guild


# *      * #
#  Create  #
# *      * #
def add_guild(**kwargs):
    try:
        new_guild = Guild(**kwargs)
        db.session.add(new_guild)
        db.session.commit()

        return 'Guild successfully added', 200

    except Exception:
        raise Exception('Something went wrong while adding new guild.')


# *         * #
#   Retrieve  #
# *         * #
def get_all_guilds():
    try:
        all_guilds = Guild.query.all()
        results = [guild.as_dict() for guild in all_guilds]

    except ValueError:
        raise Exception('No data exists in the database.')

    else:
        return jsonify(results)


def get_guild(guild_id):
    guild = Guild.query.filter_by(guild_id = guild_id).first()

    if guild:
        guild_dict = guild.as_dict()

        if guild_dict['last_activity_ts'] is not None:
            guild_dict['last_activity_ts'] = guild_dict['last_activity_ts'].isoformat()

        return jsonify(guild_dict)
    else:
        return f'Guild with id {guild_id} not found.', 404


# *      * #
#  Update  #
# *      * #
def update_guild(guild_id, **data):
    try:
        guild = Guild.query.filter_by(guild_id = guild_id).first()

        for k, v in data.items():
            if k == 'last_activity_ts':
                v = datetime.fromisoformat(v)

            setattr(guild, k, v)
        db.session.commit()

    except AttributeError:
        raise Exception('Tried passing incorrect attribute to guild.')

    except ValueError:
        return f'No guild found with id #{data["guild_id"]}.', 404

    except TypeError:
        raise Exception('Bot tried to do something obscene with an object.')

    else:
        return f'Guild name {guild.name} with id #{guild.guild_id} successfully updated.', 200


# *      * #
#  Delete  #
# *      * #
def remove_guild(guild_id):
    try:
        guild = Guild.query.filter_by(guild_id = guild_id).first()

        db.session.delete(guild)
        db.session.commit()

    except ValueError:
        raise Exception(f'No guild at id {guild.guild_id}')

    else:
        return f'Guild name {guild.name} with id #{guild.guild_id} successfully deleted.', 200
