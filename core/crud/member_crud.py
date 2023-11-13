from arrow import get

from ..config import db
from ..models.member import Member
from ..models.guild import Guild


def resolve_create_member(obj, info, **data):
    try:
        guild_id = data["guild_id"]
        guild = Guild.query.filter_by(guild_id = guild_id).first()
        member = Member(**data)

        guild.members.append(member)
        db.session.add(member)
        db.session.commit()

        payload = {
            'code': 200,
            'member': member.as_dict(),
        }

    except AttributeError as e:
        payload = {
            'code': 404,
            'errors': [f'Guild matching id {guild_id} could not be found.', f'{e}']
        }

    except ValueError as e:
        payload = {
            'code': 400,
            'errors': ['It\'s probably that you gave me bad data, or something. Maybe this will be helpful.', f'{e}']
        }

    except Exception as e:
        payload = {
            'code': 500,
            'errors': [str(e)],
        }

    return payload


def resolve_members():
    try:
        members = [member.as_dict() for member in Member.query.all()]

        if members:
            payload = {
                'code': 200,
                'members': members
            }
        else:
            payload = {
                'code': 404,
                'errors': ['No members could be found.']
            }

    except Exception as e:
        payload = {
            'code': 500,
            'errors': [str(e)]
        }

    return payload


def resolve_member(obj, info, member_id):
    try:
        member = Member.query.filter_by(member_id = member_id).first()

        payload = {
            'code': 200,
            'member': member.__dict__,
        }

    except AttributeError as e:
        payload = {
            'code': 404,
            'errors': [f'Member matching id {member_id} could not be found.', f'{e}'],
        }

    return payload


def resolve_update_member(member_id, **data):
    try:
        member = Member.query.filter_by(member_id = member_id).first()

        for k, v in data.items():
            if k == 'last_activity_ts':
                v = get(v).to('US/Central').datetime  # Converting isostring back into a datetime object with Arrow.

            setattr(member, k, v)

        db.session.add(member)
        db.session.commit()

        payload = {
            'code': 200,
            'member': member.as_dict(),
        }

    except AttributeError as e:
        payload = {
            'code': 404,
            'errors': [f'Member matching id {member_id} could not be found.', f'{e}']
        }

    except ValueError as e:
        payload = {
            'code': 400,
            'errors': ['It\'s probably that you gave me bad data, or something. Maybe this will be useful.', f'{e}']
        }

    except Exception as e:
        payload = {
            'code': 500,
            'errors': [str(e)]
        }

    return payload


def resolve_delete_member(member_id):
    try:
        member = Member.query.filter_by(member_id = member_id).first()

        db.session.delete(member)
        db.session.commit()

        payload = {
            'code': 200,
            'success_msg': f'Member matching id {member_id} has successfully been deleted.',
        }

    except AttributeError as e:
        payload = {
            'code': 404,
            'errors': [f'Member matching id {member_id} could not be found.', f'{e}']
        }

    return payload
