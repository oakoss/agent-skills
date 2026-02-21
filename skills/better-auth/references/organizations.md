---
title: Organizations
description: Multi-tenant organizations with teams, invitations, RBAC, dynamic access control, lifecycle hooks, and schema customization
tags: [organization, multi-tenant, teams, invitations, rbac, roles, permissions]
---

# Organizations

## Setup

Server:

```ts
import { betterAuth } from 'better-auth';
import { organization } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    organization({
      allowUserToCreateOrganization: true,
      organizationLimit: 5,
      membershipLimit: 100,
    }),
  ],
});
```

Run `npx @better-auth/cli@latest migrate` after adding the plugin.

Client:

```ts
import { createAuthClient } from 'better-auth/client';
import { organizationClient } from 'better-auth/client/plugins';

export const authClient = createAuthClient({
  plugins: [organizationClient()],
});
```

## Creating Organizations

```ts
const { data, error } = await authClient.organization.create({
  name: 'My Company',
  slug: 'my-company',
  logo: 'https://example.com/logo.png',
  metadata: { plan: 'pro' },
});
```

Creator is automatically assigned the `owner` role.

### Dynamic Limits

```ts
organization({
  allowUserToCreateOrganization: async (user) => {
    return user.emailVerified === true;
  },
  organizationLimit: async (user) => {
    return user.plan === 'premium' ? 20 : 3;
  },
});
```

### Server-Side Creation (on behalf of a user)

```ts
await auth.api.createOrganization({
  body: {
    name: 'Client Organization',
    slug: 'client-org',
    userId: 'user-id-who-will-be-owner',
  },
});
```

`userId` cannot be used alongside session headers.

## Active Organization

Many endpoints use the active organization automatically:

```ts
await authClient.organization.setActive({ organizationId });

await authClient.organization.listMembers();
await authClient.organization.listInvitations();

const { data } = await authClient.organization.getFullOrganization();
// data.organization, data.members, data.invitations, data.teams
```

## Members

### Adding and Removing

```ts
await auth.api.addMember({
  body: { userId: 'user-id', role: 'member', organizationId: 'org-id' },
});

await auth.api.addMember({
  body: {
    userId: 'user-id',
    role: ['admin', 'moderator'],
    organizationId: 'org-id',
  },
});

await authClient.organization.removeMember({
  memberIdOrEmail: 'user@example.com',
});
```

The last owner cannot be removed. Transfer ownership first.

### Updating Roles

```ts
await authClient.organization.updateMemberRole({
  memberId: 'member-id',
  role: 'admin',
});
```

### Dynamic Membership Limits

```ts
organization({
  membershipLimit: async (user, organization) => {
    if (organization.metadata?.plan === 'enterprise') return 1000;
    return 50;
  },
});
```

## Invitations

### Email Setup

```ts
organization({
  sendInvitationEmail: async (data) => {
    const { email, organization, inviter, invitation } = data;
    await sendEmail({
      to: email,
      subject: `Join ${organization.name}`,
      html: `<p>${inviter.user.name} invited you.</p>
             <a href="https://app.com/invite/${invitation.id}">Accept</a>`,
    });
  },
  invitationExpiresIn: 60 * 60 * 24 * 7, // 7 days (default: 48 hours)
  invitationLimit: 100,
  cancelPendingInvitationsOnReInvite: true,
});
```

### Sending and Accepting

```ts
await authClient.organization.inviteMember({
  email: 'newuser@example.com',
  role: 'member',
});

await authClient.organization.acceptInvitation({
  invitationId: 'invitation-id',
});
```

### Shareable Invitation URLs

```ts
const { data } = await authClient.organization.getInvitationURL({
  email: 'newuser@example.com',
  role: 'member',
  callbackURL: 'https://app.com/dashboard',
});
// data.url — does NOT trigger sendInvitationEmail
```

## Roles and Permissions

Default roles:

| Role     | Description                           |
| -------- | ------------------------------------- |
| `owner`  | Full access, can delete organization  |
| `admin`  | Manage members, invitations, settings |
| `member` | Basic access                          |

### Checking Permissions

```ts
const { data } = await authClient.organization.hasPermission({
  permission: 'member:write',
});

// Client-side only (no API call, static check)
const canManage = authClient.organization.checkRolePermission({
  role: 'admin',
  permissions: ['member:write'],
});
```

`checkRolePermission` does not work for dynamic access control — use `hasPermission` instead.

### Dynamic Access Control

```ts
organization({
  dynamicAccessControl: { enabled: true },
});
```

Custom roles:

```ts
await authClient.organization.createRole({
  role: 'moderator',
  permission: { member: ['read'], invitation: ['read'] },
});

await authClient.organization.updateRole({
  roleId: 'role-id',
  permission: { member: ['read', 'write'] },
});

await authClient.organization.deleteRole({ roleId: 'role-id' });
```

Pre-defined roles (owner, admin, member) cannot be deleted. Roles assigned to members cannot be deleted until members are reassigned.

## Teams

### Setup

```ts
organization({
  teams: {
    enabled: true,
    maximumTeams: 20,
    maximumMembersPerTeam: 50,
    allowRemovingAllTeams: false,
  },
});
```

### Managing Teams

```ts
const { data } = await authClient.organization.createTeam({
  name: 'Engineering',
});

await authClient.organization.addTeamMember({
  teamId: 'team-id',
  userId: 'user-id',
});

await authClient.organization.removeTeamMember({
  teamId: 'team-id',
  userId: 'user-id',
});

await authClient.organization.setActiveTeam({ teamId: 'team-id' });
```

## Lifecycle Hooks

```ts
organization({
  hooks: {
    organization: {
      beforeCreate: async ({ data, user }) => {
        return {
          data: {
            ...data,
            metadata: { ...data.metadata, createdBy: user.id },
          },
        };
      },
      afterCreate: async ({ organization, member }) => {
        await createDefaultResources(organization.id);
      },
      beforeDelete: async ({ organization }) => {
        await archiveOrganizationData(organization.id);
      },
    },
    member: {
      afterCreate: async ({ member, organization }) => {
        await notifyAdmins(organization.id, 'New member joined');
      },
    },
    invitation: {
      afterCreate: async ({ invitation, organization, inviter }) => {
        await logInvitation(invitation);
      },
    },
  },
});
```

## Schema Customization

```ts
organization({
  schema: {
    organization: {
      modelName: 'workspace',
      fields: { name: 'workspaceName' },
      additionalFields: {
        billingId: { type: 'string', required: false },
      },
    },
    member: {
      additionalFields: {
        department: { type: 'string', required: false },
        title: { type: 'string', required: false },
      },
    },
  },
});
```

## Security Considerations

- **Owner protection**: Last owner cannot be removed or leave. Transfer ownership first.
- **Invitation security**: Expire after 48 hours by default. Only the invited email can accept. Admins can cancel pending invitations.
- **Disable deletion**: `disableOrganizationDeletion: true` prevents org deletion entirely.
- **Soft-delete via hooks**: Throw from `beforeDelete` to archive instead of deleting.
