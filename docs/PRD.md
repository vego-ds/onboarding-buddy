# Onboarding Buddy - Product Requirements Document

## 1. Product Name

Onboarding Buddy

## 2. One-Line Description

Onboarding Buddy is a multi-agent onboarding system that helps companies automate and manage employee onboarding workflows through coordinated AI agents, human approvals, and observable workflow execution.

## 3. Product Vision

Onboarding Buddy aims to become an intelligent onboarding operations platform that reduces repetitive HR workload, improves onboarding consistency, and creates a better employee onboarding experience through safe, observable, and coordinated multi-agent workflow automation.

## 4. Problem Statement

HR teams spend too much time doing repeated onboarding tasks like sending emails, collecting documents, creating checklists, scheduling orientation, notifying managers, and tracking employee progress. This causes delays, missed steps, and poor onboarding experiences for new employees.

## 5. Target Users

- HR Executive
- New Employee
- Hiring Manager

## 6. User Personas

### HR Executive

Responsible for managing employee onboarding workflows. Needs faster onboarding execution, reduced manual work, and clear visibility into onboarding progress.

### New Employee

Needs clear onboarding guidance, timely reminders, and a smooth onboarding experience.

### Hiring Manager

Needs visibility into employee onboarding readiness and completion status.

## 7. MVP Features

- Employee details form
- Multi-agent onboarding workflow orchestration
- AI-generated onboarding checklist creation
- Welcome email draft generator
- Human approval system
- Task status tracker
- Onboarding dashboard
- Agent activity logging
- Supervisor-to-specialist agent routing

## 8. User Journey

1. HR enters employee details.
2. Supervisor Agent analyzes onboarding requirements.
3. Intake Agent validates onboarding information.
4. Policy and Knowledge Agent checks onboarding rules and templates.
5. Task Planning Agent generates the onboarding checklist.
6. HR reviews generated onboarding tasks.
7. System generates a welcome email draft.
8. HR approves actions.
9. System updates onboarding progress.
10. Dashboard displays workflow status and agent activity.

## 9. Success Metrics

- Checklist generated in under 10 seconds.
- HR manual effort reduced by at least 50 percent.
- Every onboarding task has a clear status.
- Welcome email draft is usable with minor edits.
- Supervisor Agent routes requests to the correct specialist agent.
- Demo can be understood by a recruiter in under 3 minutes.

## 10. Business KPIs

- Reduce onboarding coordination time by 50 percent.
- Reduce manual onboarding task creation effort by 70 percent.
- Improve onboarding task completion visibility.
- Reduce missed onboarding steps.
- Improve onboarding consistency across employees.

## 11. Out of Scope for Version 1

- Payroll integration
- Real HRMS integration
- Background verification
- Real document verification
- Real access provisioning
- Complex admin roles
- Real calendar integration
- Autonomous manager follow-up workflows

## 12. User Stories

### HR Executive

- As an HR Executive, I want to enter employee details so the onboarding process can begin.
- As an HR Executive, I want the system to generate onboarding tasks automatically so I can reduce manual work.
- As an HR Executive, I want to approve AI-generated actions before execution so I maintain control.
- As an HR Executive, I want to track onboarding progress so I know what is completed and pending.
- As an HR Executive, I want to see agent activity so I can understand how onboarding decisions were made.

### New Employee

- As a new employee, I want to receive clear onboarding instructions so I know what to do next.
- As a new employee, I want reminders for pending tasks so I do not miss anything.

### Hiring Manager

- As a hiring manager, I want updates about onboarding progress so I know when the employee is ready.

## 13. Functional Requirements

- The system must allow HR to enter employee information.
- The system must generate onboarding tasks using coordinated AI agents.
- The system must generate a welcome email draft.
- The system must allow HR approval before sensitive task execution.
- The system must store onboarding progress.
- The system must display onboarding status on a dashboard.
- The system must maintain onboarding history.
- The system must support a Supervisor Agent for workflow coordination.
- The system must support specialist onboarding agents.
- The Supervisor Agent must route tasks to appropriate specialist agents.
- Specialist agents must execute only their assigned responsibilities.
- The system must maintain visibility into agent execution history.
- The system must log agent decisions, routing actions, and workflow results.
- The system must support simulated tools for email, calendar, and task updates in Version 1.

## 14. Task States

Each onboarding task can exist in one of the following states:

- Pending
- Awaiting Approval
- In Progress
- Completed
- Failed
- Cancelled

## 15. Non-Functional Requirements

- The system should generate onboarding plans in under 10 seconds.
- The UI should be simple and beginner friendly.
- The system should not lose onboarding progress data.
- The application should support multiple onboarding records.
- The dashboard should update task statuses correctly.
- Agent execution should be observable through logs and workflow traces.
- Failed agent steps should be retried or surfaced clearly to the user.
- Specialist agents should remain modular and easy to debug.

## 16. Multi-Agent Evaluation Metrics

The multi-agent onboarding system should be evaluated based on:

- Accuracy of onboarding checklist generation
- Quality of generated welcome emails
- Human approval acceptance rate
- Tool execution success rate
- Agent retry frequency
- Incorrect task generation rate
- Supervisor routing accuracy
- Specialist agent execution success rate
- Model response validation success rate
- OpenRouter request failure rate

## 17. Multi-Agent Responsibilities

The multi-agent onboarding system will include multiple specialized agents coordinated through a Supervisor Agent.

### Supervisor Agent

Responsibilities:

- coordinating onboarding workflows
- routing tasks to specialist agents
- validating workflow execution order
- collecting final outputs
- maintaining workflow state visibility
- deciding when human approval is required

### Intake Agent

Responsibilities:

- validating employee onboarding information
- detecting missing onboarding fields
- structuring onboarding data
- preparing clean employee context for the workflow

### Policy and Knowledge Agent

Responsibilities:

- retrieving onboarding policies
- answering onboarding-related questions
- checking onboarding compliance rules
- referencing onboarding templates
- grounding generated outputs in available onboarding knowledge

### Task Planning Agent

Responsibilities:

- generating onboarding checklists
- suggesting onboarding tasks
- identifying missing onboarding steps
- recommending next onboarding actions
- preparing task plans for HR review

## 18. Human Responsibilities

HR Executive responsibilities:

- Verify employee information
- Approve onboarding actions
- Review AI-generated emails
- Mark exceptional cases manually
- Handle sensitive onboarding decisions
- Override or reject incorrect agent-generated recommendations

## 19. Workflow Ownership

| Workflow Step             | Owner                      |
| ------------------------- | -------------------------- |
| Employee data entry       | HR Executive               |
| Workflow orchestration    | Supervisor Agent           |
| Employee data validation  | Intake Agent               |
| Policy retrieval          | Policy and Knowledge Agent |
| Checklist generation      | Task Planning Agent        |
| Approval actions          | HR Executive               |
| Task tracking             | System                     |
| Monitoring and logging    | System                     |
| Exceptional case handling | HR Executive               |

## 20. Human Approval Requirements

The following actions require HR approval before execution:

- Sending official onboarding emails
- Marking onboarding as completed
- Requesting sensitive employee documents
- Triggering manager notifications
- Creating access-related tasks
- Applying final onboarding checklist changes

## 21. Failure Scenarios

Possible failure scenarios include:

- Missing employee information
- Specialist agent generating incomplete onboarding tasks
- Specialist agent generating incorrect email content
- Supervisor Agent routing to the wrong specialist agent
- Approval delays from HR
- System failure while saving onboarding progress
- Duplicate onboarding records
- OpenRouter request failure
- Configured model returning malformed output
- Tool execution failure
- Agent output validation failure

System behavior:

- Show clear error messages
- Allow retry actions
- Prevent data loss
- Log failed operations
- Preserve model provider and model metadata for debugging
- Preserve agent role, routing decision, and execution result for debugging

## 22. Risks and Mitigations

| Risk                                                  | Mitigation                                                  |
| ----------------------------------------------------- | ----------------------------------------------------------- |
| Specialist agent generates incorrect onboarding tasks | Human approval required before execution                    |
| Specialist agent generates inaccurate email content   | HR review before sending                                    |
| Missing employee data                                 | Validation checks before workflow execution                 |
| Supervisor Agent routes to the wrong specialist agent | Routing logs, validation checks, and fallback handling      |
| Workflow execution failure                            | Retry and logging mechanisms                                |
| Loss of onboarding visibility                         | Monitoring dashboard and audit logs                         |
| OpenRouter request fails                              | Retry logic and failure logging                             |
| Configured model quality varies                       | Use model configuration, validation, and evaluation metrics |
| Multi-agent workflow becomes too complex              | Limit MVP to core agents only                               |

## 23. Future Enhancements

Future versions may include:

- Real email integration
- Slack or Microsoft Teams integration
- HRMS integration
- Document verification
- Voice-based onboarding assistant
- Employee FAQ chatbot
- Analytics dashboard
- Multi-company onboarding support
- Parallel agent execution
- Advanced multi-agent collaboration
- Agent memory optimization
- Autonomous workflow recovery
- Provider abstraction for OpenRouter, direct OpenAI, Azure OpenAI, Anthropic, or local models

## 24. Monitoring and Logging

The system must log key agent and user actions for HR visibility, developer debugging, and workflow auditability.

### What Should Be Logged

- Employee onboarding record created
- Supervisor Agent routed workflow request
- Intake Agent validated employee information
- Policy and Knowledge Agent retrieved onboarding context
- Task Planning Agent generated onboarding checklist
- Welcome email draft generated
- HR approval given or rejected
- Task status changed
- Tool action attempted
- Tool action completed
- Tool action failed
- Error messages
- Agent decision summary
- Supervisor routing decision
- Specialist agent execution result
- Timestamp for every important action
- LLM provider used
- Configured model used
- OpenRouter request status
- Model output validation result

### Log Examples

- HR created onboarding record for Priya Sharma.
- Supervisor Agent routed workflow to Intake Agent.
- Intake Agent detected missing joining date.
- Policy and Knowledge Agent retrieved onboarding policy template.
- Task Planning Agent generated 6 onboarding tasks.
- Supervisor Agent prepared final onboarding workflow response.
- HR approved welcome email.
- Email tool executed successfully.
- Task status changed from Pending to Completed.
- Calendar scheduling failed because joining date was missing.
- OpenRouter request failed and was retried.
- Model output validation failed because required checklist fields were missing.

### Monitoring Dashboard

The dashboard should show:

- Total onboarding cases
- Pending tasks
- Completed tasks
- Failed actions
- Approval waiting list
- Recent agent activity
- Supervisor routing history
- Specialist agent execution history
- Error history
- Model request failures
- Retry activity

### Why This Matters

Monitoring helps make the multi-agent system trustworthy. HR teams can understand workflow execution, and developers can debug failures across supervisor coordination, specialist agents, tool execution, configured models, and workflow orchestration.

## 25. Security and Data Awareness

System behavior:

- avoid exposing sensitive employee data
- maintain onboarding audit history
- restrict sensitive actions behind approval workflows
- support future role-based access control implementation
- store OpenRouter API keys only in environment variables
- avoid logging raw secrets or sensitive credential values
- avoid exposing unnecessary employee data to specialist agents
- log only the minimum necessary employee context

## 26. Product Scope and Delivery Strategy

This project follows an MVP-first development strategy.

The current version intentionally focuses on core onboarding workflow automation in order to:

- reduce implementation complexity
- improve delivery speed
- validate the onboarding workflow
- establish a stable multi-agent architecture
- ensure observability and human approval systems work correctly
- maintain flexibility through configurable model routing

Advanced enterprise capabilities such as:

- HRMS integrations
- payroll integrations
- advanced security controls
- compliance management
- role-based access systems
- advanced distributed multi-agent scaling
- analytics pipelines
- enterprise authentication
- multi-provider production governance

have been intentionally deferred to future project phases.

This approach allows the project to prioritize:

- clean architecture
- workflow reliability
- agent observability
- safe execution
- maintainable system design
- provider flexibility

before scaling into enterprise-grade complexity.

## 27. Assumptions

- Email and calendar integrations will be simulated in Version 1.
- HR users will manually approve sensitive actions.
- The MVP will support a limited number of onboarding workflows.
- SQLite is sufficient for initial development and testing.
- Initial onboarding workflows will focus on standard employee onboarding cases.
- OpenRouter will be used as the LLM provider for configurable model routing.
- The selected model will be managed through environment variables.
- The MVP will include only core agents required for onboarding workflow generation.
- Calendar Agent and Manager Follow-up Agent will be deferred to Phase 2.

## 28. Release Strategy

### Phase 1

MVP multi-agent onboarding workflow system including:

- Supervisor Agent
- Intake Agent
- Policy and Knowledge Agent
- Task Planning Agent
- Human approval workflow
- Monitoring and observability

### Phase 2

Additional operational agents:

- Calendar Agent
- Manager Follow-up Agent
- Real email integration
- Real calendar integration

### Phase 3

Enterprise integrations, analytics, and advanced orchestration.

### Phase 4

Advanced multi-agent optimization, provider governance, and enterprise scaling.

## 29. Multi-Agent System Architecture

The system follows a supervisor-based multi-agent architecture.

### Core Principle

A Supervisor Agent coordinates specialized onboarding agents instead of relying on a single general-purpose AI agent.

### Initial MVP Agents

- Supervisor Agent
- Intake Agent
- Policy and Knowledge Agent
- Task Planning Agent

### Deferred Agents

- Calendar Agent
- Manager Follow-up Agent

### Workflow Pattern

```text
HR User
↓
Frontend
↓
Backend API
↓
Supervisor Agent
↓
Specialist Agents
↓
Tools + Memory + Database
↓
Monitoring and Logging
```

### Why Multi-Agent Architecture

The onboarding process includes multiple responsibilities such as validation, planning, policy retrieval, coordination, and task tracking.

Using specialist agents improves:

- modularity
- observability
- debugging
- workflow reliability
- scalability
- maintainability

## 30. Technical Stack

### Frontend

- Streamlit

### Backend

- FastAPI

### AI Framework

- LangGraph-based multi-agent orchestration

### LLM Provider

- OpenRouter

### LLM Model

- Configurable through environment variables
- Example models may include OpenRouter-supported OpenAI, Anthropic, Google, Meta Llama, Mistral, DeepSeek, or other compatible models

### Database

- SQLite

### Vector Memory

- ChromaDB

### Deployment

- Render or Railway

### Monitoring and Logging

- Python logging for backend logs
- SQLite audit_logs table for product activity logs
- LangSmith for LangGraph agent tracing
- OpenRouter request metadata for provider-level observability
