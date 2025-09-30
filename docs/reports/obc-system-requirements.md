# OBC Web-Based System

## Introduction

### Purpose

This project documentation acts as a complete guide for the development, implementation, and maintenance of the web-based system tailored to support the Office for Other Bangsamoro Communities (OOBC) in carrying out its mandate. It pursues several key objectives:

- Foster a Common Vision: The documentation outlines the project’s goals, scope, and deliverables to align the perspectives of all stakeholders, including OOBC staff, developers, project managers, and external partners such as LGUs, NGAs, BMOAs, and approval bodies like the OCM, MFBM, and the Bangsamoro Parliament. (PARTIALLY IMPLEMENTED)
- Map Out the Project Lifecycle: It captures discovery, design, development, testing, deployment, and maintenance stages, providing a roadmap for teams to follow. (PARTIALLY IMPLEMENTED)
- Offer a Technical Foundation: System architecture, data models, and module specifications equip the development team to deliver a secure and scalable Django-based platform. (IMPLEMENTED)
- Equip Users and Administrators: Manuals, quick-reference guides, and onboarding materials help end-users, system administrators, and IT support staff operate the system effectively. (PARTIALLY IMPLEMENTED)
- Enhance Transparency and Accountability: Documentation of decisions, timelines, and resource allocation supports accountability to stakeholders and the communities served. (PARTIALLY IMPLEMENTED)

These objectives keep the project focused, efficient, and responsive to the needs of OOBC and its partners.

## Scope of the Project

The project centers on designing, developing, and launching a modular web-based system that strengthens OOBC’s efforts in serving Bangsamoro communities outside BARMM. It integrates tools for data management, needs assessment, policy recommendations, coordination, planning, budgeting, and reporting.

### Key Functionalities

- Data Management: A centralized platform gathers, stores, and organizes community profiles, socio-economic indicators, and geographic metadata across regions, provinces, municipalities, and barangays. (IMPLEMENTED)
- Needs Assessment Tools: Digital survey builders, workshop tracking, and analytics support comprehensive community consultations under the MANA framework. (IMPLEMENTED)
- Policy Recommendation Module: Drafting, review, submission, and tracking of policy proposals are handled through the policy tracking workflows with status transitions and evidence linkages. (IMPLEMENTED)
- Coordination and Communication: Shared workspaces document engagements, events, communications, and partnership milestones with LGUs, NGAs, and BMOAs. (IMPLEMENTED)
- Planning and Budgeting Module: Dashboards summarize program pipelines, budget allocations, and ceilings to aid internal planning and financial analysis, while final approvals still rely on external routing. (PARTIALLY IMPLEMENTED)
- Reporting and Analytics: Configurable dashboards, tabular exports, and narrative summaries present progress on needs, programs, and budget performance. (IMPLEMENTED)
- Mobile Accessibility: Responsive Tailwind templates enable use on phones and tablets, though offline capture and native apps remain future enhancements. (PARTIALLY IMPLEMENTED)

### Exclusions

- Hardware procurement, network infrastructure setup, and third-party system acquisitions fall outside the scope of this software project. (IMPLEMENTED)
- Scope changes or major enhancements require governance through OOBC leadership and project steering committees rather than in-app automation. (PARTIALLY IMPLEMENTED)

## Intended Audience

The project documentation addresses all stakeholders involved in or affected by the development, implementation, and operation of the OOBC web-based system, balancing accessibility for non-technical readers with depth for technical users.

- OOBC Leadership and Staff: Reference modules and dashboards to align operations with agency mandates and monitor outcomes. (IMPLEMENTED)
- Project Management Team: Use planning artifacts, timelines, and module backlogs to coordinate releases and track dependencies. (IMPLEMENTED)
- Development and QA Teams: Consult architecture diagrams, model references, and API documentation to build and test features. (IMPLEMENTED)
- System Administrators and IT Support: Manage deployments, environment variables, and monitoring scripts while awaiting automated runbooks. (PARTIALLY IMPLEMENTED)
- End-Users (Field Coordinators, Planners, Finance Officers): Capture assessments, encode initiatives, and generate reports within day-to-day workflows. (IMPLEMENTED)
- External Stakeholders (LGUs, NGAs, BMOAs, Chief Minister’s offices): Access shared dashboards and coordination records with controlled visibility; collaborative portals are planned. (PARTIALLY IMPLEMENTED)
- General Public: Receive manually curated summaries and briefers; a live public transparency portal has not been launched. (NOT IMPLEMENTED)

## Requirements Documentation

### Business Requirements

- Centralized Data Management: Maintain unified datasets for communities, programs, and policies to drive evidence-based decision-making across OOBC operations. (IMPLEMENTED)
- Policy and Program Recommendations: Provide tooling to generate, justify, and monitor policy recommendations destined for the Chief Minister. (IMPLEMENTED)
- Coordination and Collaboration: Track consultations, partnerships, and communications to strengthen alignment with partner institutions. (IMPLEMENTED)
- Needs Assessment and Analysis: Capture field data, workshop outputs, and prioritization matrices to surface community needs and opportunities. (IMPLEMENTED)
- Planning and Budgeting Support: Enable budget capture, analytics, and reporting while acknowledging that endorsements and appropriations proceed through external workflows. (PARTIALLY IMPLEMENTED)
- Reporting and Transparency: Deliver dashboards and exportable reports that illustrate needs, interventions, and performance metrics for leadership. (IMPLEMENTED)
- Scalability and Adaptability: Use modular Django apps and reusable components to allow new modules and integrations with minimal disruption. (PARTIALLY IMPLEMENTED)
- Security and Confidentiality: Enforce role-based access, approvals, and session protections, with advanced controls scheduled for later phases. (PARTIALLY IMPLEMENTED)

### User Requirements

- OOBC Staff Dashboard: Provide a configurable landing page summarizing active assessments, policy drafts, and coordination tasks. (PARTIALLY IMPLEMENTED)
- Data Entry and Retrieval: Offer validated forms, batch import utilities, and filtered search to update and locate records efficiently. (PARTIALLY IMPLEMENTED)
- Collaboration Tools: Allow internal messaging, shared notes, and attachment management within coordination modules, pending richer co-authoring. (PARTIALLY IMPLEMENTED)
- Automated Notifications: Trigger email or in-app alerts for pending reviews, expiring initiatives, and coordination follow-ups once notification services are enabled. (PARTIALLY IMPLEMENTED)
- Field Accessibility: Guarantee responsive layouts for mobile browsers, with offline-first enhancements queued for future sprints. (PARTIALLY IMPLEMENTED)
- External Stakeholder Access: Provide authenticated views of relevant programs and documents with granular permissions to be expanded. (PARTIALLY IMPLEMENTED)
- Public Insight: Share selected metrics through printable briefers while planning a public-facing data portal. (NOT IMPLEMENTED)

## System Requirements

### Functional Modules

- Data Management Module: Manage CRUD workflows for community demographics, socio-economic indicators, and geographic mappings with import/export capabilities. (IMPLEMENTED)
- Needs Assessment Tools: Support survey forms, workshop scheduling, and analysis dashboards linked to community records and assessments. (IMPLEMENTED)
- Policy Recommendation Module: Track proposals from drafting through review, submission, and implementation, tying them to supporting assessments and needs. (IMPLEMENTED)
- Coordination and Communication Module: Record events, action items, engagement outcomes, and documents in a shared workspace for inter-agency collaboration. (IMPLEMENTED)
- Planning and Budgeting Module: Aggregate budgets, ceilings, and funding flows across initiatives, with workflow automation pending integration with approval bodies. (PARTIALLY IMPLEMENTED)
- Reporting and Analytics Module: Generate pre-built and ad hoc reports with visualization components for leadership briefings and exports. (IMPLEMENTED)
- Integration Capabilities: Expose REST APIs for internal services, with external API gateways, document suites, and webhook publishing slated for upcoming phases. (PARTIALLY IMPLEMENTED)
- Mobile Functionality: Deliver responsive UI components for field access while offline caching and sync remain under development. (PARTIALLY IMPLEMENTED)

### Non-Functional Requirements

- Performance: Optimize querysets, pagination, and caching hints to keep routine interactions responsive, pending formal load testing at peak concurrency. (PARTIALLY IMPLEMENTED)
- Scalability: Plan for containerized deployments and horizontal scaling even though current environments operate on single instances without auto-scaling. (NOT IMPLEMENTED)
- Security: Apply Django’s authentication, RBAC, CSRF, and password policies, with MFA, SSO, and data-at-rest encryption on the roadmap. (PARTIALLY IMPLEMENTED)
- Reliability and Availability: Ensure stable operations through monitoring scripts and manual backups, while automated backup/DR procedures are still being defined. (NOT IMPLEMENTED)
- Usability: Maintain consistent Tailwind styling, contextual help, and component reuse, with accessibility audits and multilingual content forthcoming. (PARTIALLY IMPLEMENTED)
- Maintainability: Use modular apps, service layers, and shared utilities to ease refactoring, though end-to-end technical runbooks remain in progress. (PARTIALLY IMPLEMENTED)
- Interoperability: Support CSV/Excel imports and REST endpoints; standards-based integrations with government systems are targeted for later releases. (PARTIALLY IMPLEMENTED)

## Design Documentation

### System Architecture

The system architecture defines the structure and interactions of the web-based system’s components, ensuring scalability of development teams and adaptability of features.

- Client-Server Model: Django serves HTML templates and RESTful JSON endpoints consumed by modern browsers and potential external clients. (IMPLEMENTED)
- API-Driven Design: Django REST Framework viewsets expose core resources, while some workflows still rely on server-rendered forms without API parity. (PARTIALLY IMPLEMENTED)
- Cloud and Hosting Strategy: Deployments currently run on single-instance servers; plans for cloud load balancing, auto-scaling, and managed services remain pending. (NOT IMPLEMENTED)
- Caching and Performance Acceleration: Query optimizations and select_related/prefetch_related calls reduce database hits; Redis and CDN layers are not yet provisioned. (PARTIALLY IMPLEMENTED)
- Offline Functionality: Service workers, background sync, and local data caches have not been built, limiting offline resilience. (NOT IMPLEMENTED)

### User Interface Design

The user interface prioritizes ease of use, accessibility, and efficiency for OOBC staff, coordinators, and stakeholders, facilitating data-intensive tasks and collaboration.

- Design Principles: User journeys, consistent navigation, and reusable Tailwind components improve usability, while formal accessibility compliance work remains. (PARTIALLY IMPLEMENTED)
- Key UI Components: Dashboards, wizard-style forms, tabular listings, and modal dialogs streamline daily operations; interactive GIS maps and real-time co-authoring are planned. (PARTIALLY IMPLEMENTED)
- UI Framework: Server-rendered Django templates augmented by Tailwind CSS utility classes and component includes deliver the interface layer. (IMPLEMENTED)
- Prototyping and Testing: Wireframes and prototypes are produced ad hoc; a maintained design system and structured usability testing cadence are still to be established. (NOT IMPLEMENTED)

### Database Design

The database design organizes data on community profiles, needs assessments, policies, and coordination efforts, emphasizing integrity, performance, and accessibility.

- Database Platform: PostgreSQL backs production deployments with SQLite used for developer setups, both managed through Django’s ORM. (IMPLEMENTED)
- Key Tables and Relationships: Community, assessment, policy, coordination, and monitoring models enforce referential integrity and encapsulate domain logic. (IMPLEMENTED)
- Data Normalization: Schemas largely follow 3rd Normal Form, with selective denormalization reviewed for reporting convenience. (PARTIALLY IMPLEMENTED)
- Indexing and Optimization: ORM-defined indexes and annotated queries handle common filters; advanced tuning (partitioning, materialized views) awaits future optimization cycles. (PARTIALLY IMPLEMENTED)
- Backup and Recovery: Automated backup routines, retention policies, and disaster-recovery drills are still being formalized. (NOT IMPLEMENTED)

### Security Design

The security design protects sensitive information and ensures compliance with OOBC confidentiality requirements.

- Authentication and Authorization: Custom user types, approval workflows, and per-view permissions safeguard access; MFA and government SSO integrations are not yet in place. (PARTIALLY IMPLEMENTED)
- Data Encryption: HTTPS is enforced at the web server tier, while managed encryption at rest and hardware security modules will be introduced later. (PARTIALLY IMPLEMENTED)
- Application Security: Django’s protections (ORM sanitation, CSRF tokens, secure sessions) mitigate common threats; recurring penetration tests and vulnerability scans need scheduling. (PARTIALLY IMPLEMENTED)
- Auditing and Monitoring: Fine-grained audit logs, SIEM integration, and anomaly detection pipelines have not been configured. (NOT IMPLEMENTED)
- Compliance: Operational practices align informally with the Data Privacy Act of 2012; formal retention schedules and documented audits are still being developed. (PARTIALLY IMPLEMENTED)

### Integration Design

The integration design ensures seamless connections with external systems and services, fostering data sharing and collaboration.

- API Integration: REST endpoints expose community, coordination, and policy datasets; API keys, rate limiting, and webhook callbacks are planned enhancements. (PARTIALLY IMPLEMENTED)
- Third-Party Services: GIS overlays, cloud storage for large documents, and SMS/email gateways are under evaluation for future phases. (NOT IMPLEMENTED)
- Government System Interoperability: No automated exchanges with BARMM or national systems (e.g., PSA) are live yet; SFTP/JSON pipelines remain conceptual. (NOT IMPLEMENTED)
- Single Sign-On: OAuth2, SAML, or government identity federation has not been integrated into the authentication flow. (NOT IMPLEMENTED)
- Offline Syncing: IndexedDB caches, background sync, and conflict resolution strategies have not been implemented. (NOT IMPLEMENTED)
- Extensibility: The modular Django architecture, shared services, and component libraries provide a foundation for future extensions, though plugin interfaces will be expanded. (PARTIALLY IMPLEMENTED)
