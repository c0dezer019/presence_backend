# Database schemas

## Guild

Represents a Discord server.

### Parameters

`id` - int, required<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Primary key, database id, unnullable<br><br>
`guild_id` - int, required<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Snowflake server id, unnullable<br><br>
`name` - str, required<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name of the guild<br><br>
`last_activity` - str<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Last activity performed in the guild.<br><br>
`last_active_channel` - int, default = 0<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Snowflake id of the last channel to receive activity.<br>
<br>
`last_activity_ts` - datetime<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The timestamp the guild was last active.<br><br>
`idle_times` - List[int]<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A List containing the recent times a guild as been idle.
A value is added when a guild received<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;activity again
after a set amount of time without.<br><br>
`avg_idle_time` - int<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The average time a server is idle based on the average of `idle_times`.<br><br>
`recent_avgs` - List[int]<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A List of recent averages.<br><br>
`status` - str<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Signifies if the server is active or inactive based on length of time idle.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Can only be `active` or `inactive`.<br><br>
`settings` - dict, default = {}<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A dict for guild settings that dictate how the bot should behave.<br><br>
`members` - Set[dict], default = []<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A Set of `MemberShard` objects representing the members in a guild.<br><br>
`date_added` - datetime, required<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The date the server was added to the database.

### Methods

## UserShard

## User