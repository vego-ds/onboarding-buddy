# Security Model

## Defense In Depth For Assistant Pipeline

The assistant pipeline uses layered controls so user text, retrieved knowledge, and final LLM output are treated as separate trust boundaries.

## 0. Authentication And RBAC

Phase 4 adds real user identity with JWT bearer tokens, refresh-token rotation, tenant isolation, SSO assertion login, password reset tokens, and auth audit logs.

Implemented roles:

```text
employee
manager
hr_admin
admin
```

RBAC rules:

- employees can access only their linked onboarding record
- managers can access direct reports linked by `manager_id`
- HR admins and admins can access onboarding workflows inside their tenant
- only HR admins and admins can reindex assistant knowledge
- the assistant derives role from the authenticated backend user, not request-body text
- refresh tokens and password reset tokens are stored as hashes
- auth events are written to `auth_audit_logs`

## 1. Input Validation Layer

All incoming assistant questions pass through a fast local safety classifier before retrieval, workflow context lookup, or LLM synthesis.

Location:

```text
backend/security/guardrails.py
backend/services/assistant_service.py
```

Current implementation:

- local Llama Guard compatible classifier shim
- blocks prompt-injection patterns
- blocks execution-oriented requests
- blocks oversized input

The implementation is intentionally shaped so a hosted or local Llama Guard model can replace the local classifier without changing the assistant route contract.

## 2. Context Isolation

Retrieved knowledge chunks and workflow context are treated as untrusted data. Before LLM synthesis, they are wrapped in XML with explicit trust labels.

Example:

```xml
<isolated_untrusted_context>
  <source index="1" trust="untrusted">
    <title>Access Policy</title>
    <file>policies.md</file>
    <content trust="untrusted">
      ...
    </content>
  </source>
</isolated_untrusted_context>
```

The system prompt explicitly instructs the LLM to ignore commands, policies, role changes, or tool instructions inside the untrusted XML.

## 3. Least Privilege Tools

The assistant does not execute arbitrary tool strings. Workflow context is fetched through hard-coded repository calls with fixed parameters.

Current tool wrapper:

```text
fetch_employee_workflow_context(employee_id, user_role)
```

The repository layer uses parameterized database calls. The assistant does not use `eval()`, execute raw user strings, or construct arbitrary SQL from user text.

## 4. Output Inspection

Final assistant answers are inspected before they are returned.

The output guard checks for:

- prompt or hidden-instruction exfiltration
- email addresses
- phone-number-like strings
- SSN-like strings
- payment-card-like strings

If the answer fails inspection, it is replaced with a safe response and marked for escalation.

## Current Limitations

- The input classifier is a fast local shim, not a deployed Llama Guard model yet.
- SSO is implemented as an assertion foundation; production should integrate a real OAuth/OIDC provider.
- Multi-tenant boundaries are implemented at the application RBAC layer; production should add database-level tenant constraints and migration hardening.
- The PII detector is regex-based and should be replaced or supplemented for production.
- The guardrail currently protects the assistant path, not every backend route.
