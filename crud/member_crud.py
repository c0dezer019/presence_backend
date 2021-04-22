from datetime import datetime
from flask import jsonify
from main.models import db
from main.models import Member, Guild


def get_all_members():
    all_members = Member.query.all()
    results = [member.as_dict() for member in all_members]

    return jsonify(results)


def get_member(member_id):
    member = Member.query.filter_by(member_id = member_id).first()

    if member:
        member_dict = member.as_dict()

        if member_dict['last_activity_ts'] is not None:
            member_dict['last_activity_ts'] = member_dict['last_activity_ts'].isoformat()

        return jsonify(member_dict)
    else:
        return f'No member at id: {member_id}', 404


def add_member(**data):
    member = Member.query.filter_by(member_id = data['member_id']).first()
    guild = Guild.query.filter_by(guild_id = data['guild_id']).first()

    if not member:
        try:
            member = Member(member_id = data['member_id'], username = data['username'], nickname = data['nickname'])

            guild.members.append(member)
            db.session.add(member)
            db.session.flush()
            db.session.commit()

        except ValueError:
            return f'Guild with id #{data["guild_id"]} not found.', 404

        except AttributeError:
            return 'An association error has occurred.', 400

        else:
            return jsonify(member.as_dict())
    else:
        guild.members.append(member)
        db.session.add(member)
        db.session.commit()

        return jsonify(guild.as_dict())


def update_member(member_id, **data):
    member = Member.query.filter_by(member_id = member_id).first()

    if member:
        for k, v in data.items():
            if k != 'last_activity_ts':
                setattr(member, k, v)
            else:
                v = datetime.fromisoformat(v)
                member.update(v)

        db.session.commit()

        return jsonify(member.as_dict())
    else:
        raise Exception(f'No member at id {member_id}')


def remove_member(member_id, **data):
    member = Member.query.filter_by(member_id = member_id).first()

    if member:
        for v in data.keys():
            if v != 'hard_delete':
                guild = Guild.query.filter_by(**data).first()

                if guild:
                    guild.members.remove(member)
                    db.session.commit()

                    return f'Member {member.username}(id #{member.member_id}) successfully removed from guild' \
                           f' {guild.name} (id #{guild.guild_id}).', 200
                else:
                    raise Exception('A valid guild id was not provided.')
        else:
            db.session.delete(member)
            db.session.commit()

            return f'Member {member.username}(id #{member.member_id}) successfully purged from database.', 200
    else:
        raise Exception(f'Nothing found with the args: {data}')
