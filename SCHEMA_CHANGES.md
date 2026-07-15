# GraphQL Schema Change Log

For the bot repo (separate project) to update its queries against `presence_backend`. Source of truth: `app/graphql/schema.py` (code-first, Strawberry). Mirrored SDL: `app/graphql/schema.graphql`.

---

## Change: `Member` type gained `username` and `guildId` fields

**File:** `app/graphql/schema.py`

```diff
 type Member implements User {
   memberId: Snowflake!
+  username: String!
+  guildId: Snowflake!
   adminAccess: Boolean
   dateAdded: DateTime
   flags: [String!]
   lastAct: LastAct!
   idleStats: IdleStats!
   status: String
 }
```

**What changed:** `Member` output type gained two new fields, both non-null: `username: String!` and `guildId: Snowflake!`. Non-breaking — existing bot queries that don't select them still work unchanged. Both fields are now selectable on any query/mutation returning `Member` (`createMember`, `updateMember`, `member`, `members`, `guild.members`).

**Resolver support confirmed:** all `Member(...)` construction sites (`createMember`, `updateMember`, `member` query, `members` query, `guild` query) already populate `username` and `guildId` from the DB row — no gap, safe to query immediately.

---

## Change: `updateGuild` arg `guildId` type fixed `Int!` → `Snowflake!`

**File:** `app/graphql/schema.py`

```diff
 type GuildMutations {
   createGuilds(bulkData: GuildsCreate!): GuildsResult!
-  updateGuild(guildId: Int!, input: GuildUpdate!): GuildResult!
+  updateGuild(guildId: Snowflake!, input: GuildUpdate!): GuildResult!
   resetGuild(guildId: Snowflake!): GuildResult!
   deleteGuild(guildId: Snowflake!): DeleteResult!
 }
```

**What changed:** `updateGuild`'s `guildId` arg was typed plain `Int`, inconsistent with every other mutation/query in the API (`resetGuild`, `deleteGuild`, `createGuilds`, all use custom scalar `Snowflake`). Now consistent. `Snowflake` scalar serializes as string, parses as int — bot must send `guildId` as the `Snowflake` scalar's wire format (string), not a bare GraphQL `Int` literal, if it wasn't already.

---

## Fix (no schema.py change): `schema.graphql` SDL file was stale, now regenerated/synced

**File:** `app/graphql/schema.graphql`

Two drifts corrected to match live `schema.py`:

1. `Member` type in the SDL file was missing `username`/`guildId` (see above).
2. Mutation arg name was `Input` (capital I) in the SDL file on all three `input`-taking mutations — actual arg name (from Strawberry's `_input` param, auto-camelCased) is lowercase `input`. Any bot query using `Input:` was already broken against the live server; this only fixes documentation to match reality.

```diff
-  updateGuild(guildId: Snowflake!, Input: GuildUpdate!): GuildResult!
+  updateGuild(guildId: Snowflake!, input: GuildUpdate!): GuildResult!
-  createMember(guildId: Snowflake!, Input: MemberCreate!): MemberResult!
+  createMember(guildId: Snowflake!, input: MemberCreate!): MemberResult!
-  updateMember(memberId: Snowflake!, guildId: Snowflake!, Input: MemberUpdate!): MemberResult!
+  updateMember(memberId: Snowflake!, guildId: Snowflake!, input: MemberUpdate!): MemberResult!
```

---

## Fix (no schema.py change): `MembersResult.members` field type corrected

**File:** `app/graphql/schema.py`

```diff
 type MembersResult {
   code: Int!
   success: Boolean!
   errors: [String!]!
-  members: Member
+  members: [Member!]!
 }
```

**What changed:** field was previously typed as a single nullable `Member` in code (`Optional[Member]`) despite the `members` (plural) resolver always assigning a list. Now correctly typed as a non-null list. If the bot had any query coded around the old (buggy) singular type, it needs updating to expect an array under `members`.

---

## Notes on `MemberCreate.flags` default behavior (no schema change, documented for reference)

`flags: Optional[list[str]] = UNSET` on `MemberCreate` — no default at the GraphQL/schema level. If omitted on `createMember`, the resolver (`create_member_shard`) strips UNSET kwargs before insert, so the DB column default applies: `flags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])` → empty list `[]`. No flags pre-populated automatically.

---

## Fix (no schema.py field/type/arg change): `createGuild` was 500ing / erroring on every call — now works

**Files:** `app/graphql/schema.py`, `app/database/models/base.py`, `app/database/models/guild.py`, `app/database/models/member_shard.py`, `app/graphql/resolvers/resolver.py`

No GraphQL type, field, or arg was added, removed, or renamed. Wire schema is identical. Bot queries against `createGuild` (and any query/mutation touching `Guild`/`Member`/`GuildResult`/`MemberResult`/etc. optional output fields) do not need updating. Documented because the previous behavior was broken end-to-end and worth bot devs knowing it's now fixed:

1. **Resolver key bug** — `Resolver.guild()` built the `find_or_create` defaults dict with the wrong key, causing every `createGuild` call to fail with a 500.
2. **`BaseModel` hardcoded `snowflake` column name** — `get_one`/`find_or_create` assumed every model had a column literally named `snowflake`; neither `Guild` (`guild_id`) nor `MemberShard` (`member_id`) do. Added `SNOWFLAKE_FIELD` class attr per model so the base class looks up the right column generically.
3. **`Guild.settings` default factory was a dict, not a callable** — `field(default_factory=_settings_default)` needs a zero-arg function; `_settings_default` was a bare dict literal, causing `'dict' object is not callable` any time `settings` was omitted on construction. Now a proper function returning a fresh dict.
4. **`UNSET` misused as default on output (`@type`/`@interface`) fields** — `UNSET` is only valid for `@input` types (lets a resolver tell "omitted" from "null" on args). It was copy-pasted onto output fields across `User`, `LastAct`, `Member`, `MemberResult`, `Server`, `Guild`, `GuildResult`, `DeleteResult`, causing `GraphQLError: Boolean cannot represent a non boolean value: <UnsetType instance>` (and equivalents for other scalars/types) whenever a resolver left one of those fields unset. All swapped to `None`. `@input` types (`GuildUpdate`, `MemberUpdate`, `MemberCreate`, `ISettings`, `UpdateLastAct`) correctly keep `UNSET` — unchanged.

**Net effect for bot:** previously-erroring responses on optional fields now correctly return `null` instead of throwing. If bot code has error-handling/retry logic built around these specific error strings ("Incorrect arguments received: ...", "type object 'Guild' has no attribute 'snowflake'", "'dict' object is not callable", "Boolean cannot represent a non boolean value..."), that logic is now dead code — those errors should no longer occur.
