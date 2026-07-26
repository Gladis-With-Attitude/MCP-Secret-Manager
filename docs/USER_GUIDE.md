# User Guide

This guide explains how an end user works with MCP Secret Manager after an
operator has deployed the service and provided a valid API key.

It focuses on the browser UI and the user-visible MCP workflows. It does not
cover installation, production deployment, backups or administrator-only system
maintenance.

## Core Concepts

MCP Secret Manager organizes data in a small hierarchy:

- A vault is the top-level container for a security boundary or operational
  domain, such as `production` or `openclaw`.
- A project lives inside one vault and groups related applications, agents or
  services.
- A secret lives inside one project. Secret names, descriptions, tags and
  metadata are visible metadata and must not contain secret values.
- A secret version stores one encrypted value for a secret. Creating a new
  version is the normal user rotation flow.
- An API key authenticates a browser session, a script, an MCP client or another
  technical actor.
- Audit logs record sensitive actions and access attempts without storing secret
  values.

Permissions control which actions you can see and perform. If a button, page or
action is missing, your API key or user identity may not have the required
permission.

## Sign In And Sessions

Open the frontend URL provided by your operator. In local development this is
usually:

```text
http://127.0.0.1:3000
```

To sign in:

1. Paste your MCP Secret Manager API key into the `API key` field.
2. Select `Sign in`.
3. After a successful exchange, the browser opens an authenticated session and
   redirects to `Dashboard`.

The browser session uses an HTTP-only session cookie. The API key is exchanged
for the session and should not be saved in browser notes, screenshots or chat
messages.

Use `Profile` or the account control in the top bar to end the current browser
session. The `Profile` page also lists active session metadata, such as device,
IP address, user agent, last seen time and expiration when available. Session
tokens are never shown. If you see an unfamiliar session and have permission,
revoke it.

## Navigation

The authenticated UI uses the left sidebar as the primary navigation:

- `Dashboard`: operational overview.
- `Vaults`: vault list, vault creation and vault details.
- `Projects`: project list and project details. Projects are still owned by a
  vault, even when opened from the global project list.
- `Secrets`: secret list and secret details. Secrets are still owned by a
  project.
- `API Keys`: keys for users, service accounts, MCP clients and integrations.
- `Audit Logs`: user-visible security events.
- `RBAC`: roles, permissions and assignments when your account can manage them.
- `Profile`: your profile, security status and active sessions.
- `Settings`: preferences, notification settings and safe account options.

Breadcrumbs at the top of detail pages show the current path. Use them or the
sidebar to move back to broader lists.

## Vault Workflow

Use vaults to separate operational boundaries. Examples include one vault per
environment, customer group or agent system.

To create a vault:

1. Open `Vaults`.
2. Select `Create vault`.
3. Enter a non-sensitive name.
4. Add a non-sensitive description if the form allows it.
5. Save the vault.

Vault names and descriptions are metadata. Do not put passwords, tokens, private
URLs with credentials or recovery material in those fields.

Open a vault detail page to inspect its metadata and reach the projects inside
that vault. If archive controls are available, archiving a vault removes it from
normal active workflows without exposing secret values.

## Project Workflow

Use projects to group secrets for one application, MCP server, agent, service or
automation boundary.

To create a project:

1. Open the target vault.
2. Open the vault's `Projects` view.
3. Select `Create project`.
4. Enter a clear non-sensitive name, such as `openclaw-agent-prod`.
5. Save the project.

Project metadata should describe ownership and purpose, not credentials. Put
ownership context such as `platform`, `billing service` or `local automation`
in metadata only when it is safe for other authorized users to read.

Open a project detail page to view its metadata and reach the secrets in that
project.

## Secret Workflow

Create one secret record for each credential or sensitive value you want MCP
Secret Manager to control.

To create a secret:

1. Open the target project.
2. Open the project's `Secrets` view.
3. Select `Create secret`.
4. Enter a stable secret name, such as `DATABASE_PASSWORD` or
   `OPENAI_API_KEY`.
5. Choose the type, such as `password`, `token`, `api_key`, `certificate`,
   `generic` or `other`.
6. Add only non-sensitive description, tags and JSON metadata.
7. Paste the initial secret value into `Initial value`.
8. Save the secret.

The browser sends the value to the backend and clears the value field after the
request. Do not paste the value into the name, description, tags, metadata,
rotation note or audit context.

Open a secret detail page to see metadata and the current value controls. Values
are masked by default. Use `Reveal value` only when you need to copy or verify a
specific value. Revealing a value requires explicit permission and may create an
audit event. Metadata reads do not imply permission to read the secret value.

Archive a secret when it should no longer be used. Archiving does not display or
include the secret value in the confirmation.

## Versions And User Rotation

Secret values are versioned. A rotation creates a new immutable value version
for the same secret metadata record.

Use rotation when:

- a provider issues a new credential;
- a scheduled rotation window arrives;
- a user or integration that knew the old value leaves the access boundary;
- audit indicates unexpected access;
- an upstream system reports that the credential may be exposed.

To rotate a secret from the UI:

1. Open the secret detail page.
2. Open `Versions` or select the rotation action when available.
3. Select `Rotate secret`.
4. Paste the new value into `New value`.
5. Add an optional non-sensitive rotation note, such as
   `scheduled provider renewal`.
6. Leave `Mark as current version after creation` enabled unless you are staging
   the value for a later cutover.
7. Save the new version.
8. Update the consuming service, MCP client or automation to use the new value.
9. Verify the consumer works.
10. Review audit logs for the rotation and any subsequent value reads.

The old version remains part of version history. Only users with the right
permissions can inspect version metadata, restore a version or reveal values.

## API Keys

API keys authenticate browser sign-in, REST clients, MCP clients and service
accounts. Treat every API key like a secret.

To create an API key:

1. Open `API Keys`.
2. Select `Create API key`.
3. Enter a clear technical name.
4. Choose `Service account` or `User` as the owner type.
5. Enter the backend-owned owner ID.
6. Enter comma-separated permissions, such as
   `vault.read, project.read, secret.read`.
7. Enter comma-separated scopes, such as `global` or `vault:production`.
8. Set an expiration date when policy requires one.
9. Create the key.
10. Copy the generated value immediately and store it in the approved secret
    store for the consuming system.

The full API key value is shown only once after creation. After you close the
dialog, the UI can show metadata such as name, prefix, owner, permissions,
scopes, status and timestamps, but it cannot retrieve the full key value.

Revoke an API key when it is no longer needed, when an integration is retired or
when exposure is suspected. Revocation prevents future authentication with that
key. If a key has been used in an MCP client or automation, update that client
after replacing or revoking the key.

## MCP Client Workflows

MCP clients use API-key authentication supplied by the client integration or
runtime. The available MCP tools are intentionally narrow:

- `health`
- `list_vaults`
- `create_vault`
- `list_projects`
- `create_project`
- `list_secrets`
- `create_secret`
- `get_secret`
- `create_secret_version`
- `list_secret_versions`
- `get_secret_value`
- `rotate_secret`
- `search_secrets`

Metadata tools return vault, project, secret or version metadata. Value access
is explicit through `get_secret_value` or `rotate_secret` inputs. A client that
can list secret metadata still needs value-read permission before it can decrypt
and receive a secret value.

When connecting an MCP client:

1. Create or request an API key with only the permissions and scopes the client
   needs.
2. Store that API key in the client's approved secret storage.
3. Test `health` first.
4. Test metadata access before testing value access.
5. Rotate or revoke the API key when the client is decommissioned or
   compromised.

Never configure an MCP client with a broad administrative key when a narrower
key is enough.

## Audit Logs

Open `Audit Logs` to review backend-generated events. Depending on your
permissions, you can search, filter, paginate and open event details.

User-relevant audit events include:

- successful and failed sign-in attempts;
- vault, project and secret changes;
- explicit secret value access;
- secret rotation;
- API key creation, updates and revocation;
- profile and settings changes;
- session revocation;
- RBAC changes.

Audit entries are security records. They should show actor, action, result,
resource identifiers and safe metadata. They must not show secret values, raw API
keys, session tokens or authorization headers.

Use audit logs after sensitive work:

1. Confirm the action appears with the expected actor.
2. Confirm the result is success or failure as expected.
3. Check that the resource identifier matches the intended vault, project,
   secret, API key or session.
4. Escalate unexpected value reads, unknown actors or repeated authentication
   failures to an administrator.

## Profile And Security Settings

Open `Profile` to manage your own account information and sessions.

Depending on permissions and backend capability, you may be able to:

- edit non-sensitive profile fields such as name, email or organization;
- view account security status such as MFA, passkeys, WebAuthn or recovery-key
  availability;
- change a password if password change is available in the current deployment;
- inspect active sessions;
- revoke active sessions.

Some security options may appear as status-only because the backend owns the
actual security capability. Password authentication is not implemented for the
current bootstrap runtime, so password-related controls may be unavailable even
when the UI surface exists.

Open `Settings` for user preferences:

- `Preferences`: theme, language, timezone, date/time format and display
  density.
- `Notifications`: security alerts, audit alerts, email, in-app notifications
  and product updates when supported.
- `Security`: deployment-safe security settings and status.

Settings and notifications must not contain secret values.

## Common Errors

`Invalid authentication credentials.`

The API key is missing, malformed, expired, revoked or copied incorrectly. Paste
the key again from the approved source. If it still fails, ask an administrator
to check key status, owner, permissions and audit events.

`Authentication is required.`

Your browser session is missing or expired, or the API request did not include a
valid bearer API key. Sign in again or fix the client authentication
configuration.

`CSRF token is missing or invalid.`

The browser session cookie is present but the CSRF token did not match for an
unsafe request. Refresh the page and retry. If it continues, clear the site
cookies and sign in again.

`Permission denied.` or `403 Forbidden`

Your identity is authenticated but lacks the permission or scope for the
requested action. Use the least-privilege path: request only the specific
permission needed, such as metadata read, value read, rotation or API-key
revocation.

`404 Not Found`

The resource does not exist, is archived or is outside your authorized scope.
Check that you are in the correct vault and project before escalating.

`429 Too Many Requests`

The service rate limiter rejected the request. Wait before retrying. For scripts
or MCP clients, reduce retry frequency and avoid tight loops.

Validation errors on names, JSON metadata, permissions or scopes

Use non-empty names, valid JSON objects for metadata and comma-separated
permission or scope entries. Remove secret values from metadata fields before
submitting again.

Secret value was not copied before closing a create dialog

For API keys, the full key value cannot be retrieved after the creation dialog
closes. Revoke the lost key and create a new one. For stored secrets, users with
value-read permission can explicitly reveal the current secret value.

## Safe Handling Checklist

- Keep API keys and revealed secret values out of chats, tickets,
  screenshots, filenames and shell history.
- Use descriptions, tags, notes and metadata for non-sensitive context only.
- Prefer short-lived or narrowly scoped API keys for clients and agents.
- Reveal values only when needed, then close the page or hide the value.
- Rotate secrets after exposure, owner changes or scheduled credential renewal.
- Revoke unused sessions and API keys.
- Check audit logs after sensitive changes.
- Ask an administrator for permission changes instead of reusing a broad key.

## Related Documentation

- `README.md` covers repository setup and local development entry points.
- `docs/BACKUP_GUIDE.md` is the operator backup entry point.
- `backend/docs/ROTATION_STRATEGY.md` covers operational rotation strategy.
- `backend/docs/DISASTER_RECOVERY.md` covers restore and disaster recovery.
- `backend/docs/DEPLOYMENT.md` covers production runtime configuration.
