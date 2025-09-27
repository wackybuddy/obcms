# OBC Web-Based System

## Introduction

### Purpose

This project documentation acts as a complete guide for the development, implementation, and maintenance of a web-based system tailored to support the Office for Other Bangsamoro Communities (OOBC) in carrying out its mandate. It pursues several key objectives:

- Foster a Common Vision: The documentation outlines the project’s goals, scope, and deliverables to align the perspectives of all stakeholders. These stakeholders include OOBC staff, developers, project managers, and external partners such as local government units (LGUs), national government agencies (NGAs), Bangsamoro ministries, offices, and agencies (BMOAs), and approval bodies like the Office of the Chief Minister (OCM), Ministry of Finance, Budget and Management (MFBM), and the Bangsamoro Parliament.
- Map Out the Project Lifecycle: It provides a clear plan for each stage of the project, from gathering requirements and designing the system to developing, testing, deploying, and maintaining it. This roadmap ensures the project supports OOBC’s mission to advance the social, cultural, and economic well-being of Bangsamoro communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).
- Offer a Technical Foundation: The documentation supplies the development team with system architecture, functional requirements, and design details to create a secure, scalable, and user-friendly system.
- Equip Users and Administrators: It includes manuals, guides, and resources to help end-users, system administrators, and IT support staff operate, manage, and sustain the system effectively.
- Enhance Transparency and Accountability: The documentation captures critical decisions, project timelines, and resource allocations to build trust and responsibility among stakeholders and the communities OOBC serves.

These objectives keep the project focused, efficient, and responsive to the needs of OOBC and its partners.

## Scope of the Project

The project centers on designing, developing, and launching a web-based system to strengthen OOBC’s efforts in serving Bangsamoro communities outside BARMM. The system incorporates various tools and modules to improve data management, needs assessment, policy recommendations, coordination, planning, budgeting, and reporting.

### Key Functionalities

- Data Management: A centralized platform gathers, stores, and organizes data about Bangsamoro communities, including demographic profiles, socio-economic conditions, and cultural characteristics.
- Needs Assessment Tools: The system features tools for surveys, interviews, and focus groups, paired with analytics to pinpoint community challenges and opportunities.
- Policy Recommendation Module: It includes features to draft, review, and submit data-driven policy and program proposals to the Chief Minister.
- Coordination and Communication: Secure tools and shared workspaces enable collaboration with LGUs, NGAs, and BMOAs.
- Planning and Budgeting Module: The system provides tools to develop, manage, and submit annual plans and budget proposals, with workflows to secure approvals from:
  - Office of the Chief Minister (OCM) - Technical Management Services (TMS) and Finance and Budget Management Services (FBMS).
  - Ministry of Finance, Budget and Management (MFBM).
  - Bangsamoro Parliament.
- Reporting and Analytics: Customizable reports and data visualization tools track community needs, program results, budget performance, and coordination activities.
- Mobile Accessibility: A mobile-friendly interface or app allows field staff to conduct assessments, access data, and handle tasks in real time.

### Exclusions

- The project does not include hardware procurement, network infrastructure setup, or the creation of additional modules beyond the listed functionalities.
- Any scope changes or future enhancements need formal approval through a change management process.

This scope ensures the system fully supports OOBC’s mandate while remaining flexible for future adjustments.

## Intended Audience

The project documentation addresses all stakeholders involved in or affected by the development, implementation, and operation of the OOBC web-based system. It balances accessibility for non-technical readers with depth for technical users. The specific audiences include:

- OOBC Leadership and Staff: They consult the documentation to grasp the system’s features, offer feedback on requirements, and confirm alignment with operational needs and OOBC’s mandate.
- Project Management Team: The team uses the documentation to plan, execute, and monitor the project, ensuring it meets its goals within the set timeline and budget.
- Development Team: The team depends on technical specifications, system architecture, and design details to build a secure, high-quality, and scalable system.
- System Administrators and IT Support: They handle deployment, configuration, and ongoing maintenance to keep the system secure and functional.
- End-Users: This group includes OOBC staff, field coordinators, planners, financial officers, and analysts who rely on the system’s tools to perform their roles efficiently.
- External Stakeholders: LGUs, NGAs, BMOAs, OCM (TMS and FBMS), MFBM, and the Bangsamoro Parliament use the system for data sharing, coordination, and approving plans and budgets.
- General Public: They access non-sensitive information and updates on OOBC’s work, promoting transparency and community involvement.

## Requirements Documentation

### Business Requirements

The web-based system must fulfill critical objectives to support OOBC’s mission and daily operations. These objectives shape its design and functionality:

- Centralized Data Management: A single platform will collect, store, and manage data on Bangsamoro communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM). This includes details on demographics, socio-economic status, cultural traits, and community needs. Such data will anchor evidence-based policies and programs.
- Policy and Program Recommendations: Tools within the system will assist OOBC in drafting and recommending policies and programs to the Chief Minister. Features for data analysis, proposal creation, and impact evaluation will ensure recommendations address community needs effectively.
- Coordination and Collaboration: Seamless interaction with local government units (LGUs), national government agencies (NGAs), and Bangsamoro ministries, offices, and agencies (BMOAs) is essential. The system will include communication tools and shared data spaces to strengthen partnerships and improve service delivery.
- Needs Assessment and Analysis: To gather information and evaluate community needs, the system will offer tools for surveys, interviews, and focus groups. Data analysis features will pinpoint challenges and highlight development opportunities.
- Planning and Budgeting: Annual planning and budgeting processes require support from the system. Tools for drafting, revising, and managing plans and budget proposals will streamline submissions and approvals through the Office of the Chief Minister (OCM) Technical Management Services (TMS), Finance and Budget Management Services (FBMS), the Ministry of Finance, Budget and Management (MFBM), and the Bangsamoro Parliament.
- Reporting and Transparency: Detailed reports and analytics on community needs, program results, budget use, and coordination efforts will come from robust reporting tools. These features will foster accountability to stakeholders and the Chief Minister.
- Scalability and Adaptability: As data grows and mandates evolve, the system must expand and adjust. Flexibility will allow future upgrades without disrupting operations.
- Security and Confidentiality: Strong security measures will protect sensitive community data and coordination records. Compliance with data protection laws will maintain trust among stakeholders.

### User Requirements

The system must serve diverse users—OOBC staff, field coordinators, external stakeholders like LGU and NGA representatives, and the public. Each group needs tailored features for practical, effective use.

- OOBC Staff:
  - Intuitive Interface: A clear dashboard will provide fast access to data management, analysis, and reporting tools.
  - Data Entry and Retrieval: Efficient tools will handle data input, updates, and searches, with options for batch uploads and precise queries.
  - Collaboration Features: Messaging and document-sharing tools will support teamwork on policy drafts and revisions.
  - Report Generation: Custom templates and filters will produce reports on community needs, program outcomes, and budgets, exportable in various formats.
  - Notifications: Alerts will keep staff updated on deadlines, data changes, or coordination tasks.
- Coordinators (Field Staff):
  - Mobile Access: A mobile-friendly interface or app will allow data entry and profile access during field visits.
  - Offline Functionality: Data collection will work offline in remote areas, syncing automatically once connectivity returns.
  - Task Management: Features will assign, monitor, and track tasks for assessments and coordination, showing progress clearly.
- External Stakeholders (LGUs, NGAs, BMOAs):
  - Secure Access Portal: A login system with role-based permissions will grant access to shared data, reports, and requests.
  - Communication Tools: Channels will enable feedback, clarifications, and collaboration with OOBC on shared goals.
  - Resource Access: Guidelines, program details, and recommendations will align stakeholders with community priorities.
- General Public (Limited Access):
  - Public Dashboard: A simple interface will share non-sensitive reports and updates on OOBC’s work.
  - Feedback Mechanism: Options to submit inquiries or suggestions will include response tracking for transparency.

## System Requirements

The system must deliver specific functions to meet OOBC’s operational demands. These functions fall into key categories:

- Data Management Module:
  - A central database will store and organize community data with adjustable fields and categories.
  - Options to import data from outside sources and export it for analysis or reporting will enhance flexibility.
  - Search and filter tools will locate specific datasets by region, sector, or need.
- Needs Assessment Tools:
  - Templates and forms will support surveys, interviews, and focus groups, available digitally or manually.
  - Data validation will ensure accuracy and uniformity during entry.
  - Mapping tools (e.g., GIS) will display community locations and needs visually.
- Policy Recommendation Module:
  - Document tools with templates will create policy proposals, program plans, and briefs, allowing team edits and version tracking.
  - Automated workflows will manage drafting, review, and submission to the Chief Minister, with progress updates.
  - Analytics integration will tie recommendations to solid data insights.
- Coordination and Communication Module:
  - Secure messaging and file-sharing will enable real-time collaboration with LGUs, NGAs, and BMOAs.
  - A shared workspace will support joint projects, with controls for visibility and editing rights.
  - Notifications will alert stakeholders to new requests, updates, or deadlines.
- Planning and Budgeting Module:
  - Tools will draft, revise, and manage annual plans and budget proposals.
  - Integrated workflows will handle submissions and approvals through OCM (TMS and FBMS), MFBM, and the Bangsamoro Parliament.
  - Budget tracking and reporting will ensure transparency and goal alignment.
- Reporting and Analytics Module:
  - Pre-set templates will address common needs, while a custom builder will handle unique queries.
  - Visualization tools (e.g., charts, graphs, heatmaps) will show trends, gaps, and program effects.
  - Automated scheduling and distribution will deliver reports to key recipients.
- Integration Capabilities:
  - APIs will link to existing government systems for smooth data sharing.
  - Compatibility with tools like Microsoft Office or Google Workspace will aid document work.
- Mobile Functionality:
  - A responsive design or app will provide core features on mobile devices.
  - Offline mode with local storage and syncing will support work in low-connectivity areas.

## Non-Functional Requirements

The system must meet operational standards for reliability, usability, and efficiency:

- Performance:
  - Page loads will take no more than 3 seconds, and data queries or reports will process within 5 seconds under normal use.
  - At least 50 users can work simultaneously without slowdowns, with room for more during peak times.
- Scalability:
  - Expanding data and user numbers will not strain the system as OOBC grows.
  - Horizontal scaling will accommodate future demands.
- Security:
  - Role-based access control (RBAC) and multi-factor authentication (MFA) will safeguard data.
  - Encryption will protect data in transit (HTTPS/SSL) and at rest.
  - Regular audits and adherence to the Philippines’ Data Privacy Act of 2012 will ensure compliance.
- Reliability and Availability:
  - Uptime will reach at least 99.5%, keeping the system accessible during key periods.
  - Daily backups and a disaster recovery plan will restore operations within 24 hours of a failure.
- Usability:
  - A consistent, easy-to-use interface will suit users of all skill levels.
  - Support for languages like English, Filipino, and Arabic, plus WCAG 2.1 compliance, will enhance accessibility.
- Maintainability:
  - A modular setup will allow updates, fixes, and additions without downtime.
  - Detailed documentation for components, APIs, and settings will aid ongoing upkeep.
- Interoperability:
  - Standard formats (e.g., JSON, XML) and protocols (e.g., REST) will enable integration with other systems.
  - Compatibility with common devices and browsers will ensure broad access.

## Design Documentation

### System Architecture

The system architecture defines the structure and interactions of the web-based system’s components. It ensures the system remains scalable, adaptable, and capable of supporting OOBC’s data management, coordination, and planning needs.

- Client-Server Model:
  - The system operates on a client-server framework. The frontend serves as the client, providing a web-based interface for users. The backend, acting as the server, manages data processing, business logic, and database interactions.
  - Frontend: Developed with HTML5, CSS3, and JavaScript, it ensures compatibility across desktops, tablets, and mobile devices.
  - Backend: Built using Python (Django) or Node.js (Express), it delivers RESTful APIs to support communication and core functionalities.
- API-Driven Design:
  - The backend provides RESTful APIs to process frontend requests. This approach enhances flexibility and supports future expansions.
  - APIs remain stateless, enabling the system to scale efficiently and accommodate additional users or upgrades.
- Cloud-Based Hosting:
  - The system deploys on a cloud platform, such as AWS, Azure, or Google Cloud. This setup guarantees availability, scalability, and rapid recovery from disruptions.
  - Load balancing and auto-scaling features handle high-traffic scenarios, such as community consultations or data collection periods.
- Caching and Performance:
  - Caching tools, like Redis or Memcached, store frequently accessed data to accelerate responses and lessen database load.
  - A Content Delivery Network (CDN) distributes static files, such as images and scripts, for faster delivery.
- Offline Functionality:
  - Service Workers and IndexedDB enable field staff to collect data offline in remote areas. The system synchronizes automatically once connectivity resumes.

### User Interface Design

The user interface (UI) prioritizes ease of use, accessibility, and efficiency for OOBC staff, coordinators, and stakeholders. It facilitates data-intensive tasks and collaboration.

- Design Principles:
  - User-Centered Design: The interface aligns with user workflows, simplifying tasks like data entry and report generation.
  - Consistency: Uniform buttons, menus, and layouts accelerate user familiarity with the system.
  - Accessibility: Compliance with WCAG 2.1 standards ensures support for screen readers, keyboard navigation, and adequate color contrast.
- Key UI Components:
  - Dashboard: Users can personalize it with widgets displaying key metrics, such as active assessments or pending reports.
  - Data Entry Forms: Streamlined forms feature validation, tooltips, and auto-save to promote accuracy and efficiency.
  - Interactive Maps: GIS tools (e.g., Leaflet or Google Maps API) present community data and program coverage visually.
  - Collaboration Workspace: Real-time editing, commenting, and version history enhance team policy development.
  - Mobile-Friendly Interface: Responsive design and touch-friendly elements ensure usability on mobile devices.
- UI Framework:
  - Built with React or Vue.js for dynamic, reusable components, and styled with Bootstrap or Tailwind CSS for responsiveness.
- Prototyping and Testing:
  - Wireframes and mockups, created in Figma or Adobe XD, shape the design. Usability tests with OOBC staff and coordinators refine the interface.

### Database Design

The database design organizes data on community profiles, needs assessments, policies, and coordination efforts. It emphasizes efficiency, security, and accessibility.

- Database System:
  - A relational database, such as MySQL, ensures reliability and supports complex transactions.
- Key Tables and Relationships:
  - Community Profiles: Store demographic details (e.g., population, location) linked to needs assessments.
  - Needs Assessments: Contain survey, interview, and other data/information gathered, tied to community profiles.
  - Policy Recommendations: Record proposals and connect them to supporting evidence.
  - Coordination Logs: Document interactions with LGUs, NGAs, and BMOAs, including attachments and tasks.
  - User Accounts: Manage credentials, roles, and permissions, linked to activity logs.
- Data Normalization:
  - Tables adhere to 3rd Normal Form (3NF) to eliminate redundancy, with adjustments for faster reporting.
- Indexing and Optimization:
  - Indexes on frequently searched fields (e.g., community ID) and partitioning for large datasets enhance query performance.
- Backup and Recovery:
  - Daily backups with point-in-time recovery safeguard data. Archiving preserves historical records.

### Security Design

The security design protects sensitive information and ensures compliance with OOBC’s confidentiality requirements.

- Authentication and Authorization:
  - Multi-Factor Authentication (MFA) strengthens security with additional verification (e.g., SMS or authenticator app).
  - Role-Based Access Control (RBAC) restricts access to authorized users based on roles like admin, staff, or coordinator.
  - Single Sign-On (SSO) integrates with government systems where applicable.
- Data Encryption:
  - TLS 1.3 secures data in transit, while AES-256 protects data at rest. A Hardware Security Module (HSM) manages encryption keys.
- Application Security:
  - Input validation and sanitization block attacks like SQL injection. CSRF protection and secure session management provide additional safeguards.
  - Regular penetration tests and vulnerability scans identify and resolve weaknesses.
- Auditing and Monitoring:
  - Audit logs track user actions and system events. SIEM tools monitor anomalies and enable swift responses.
- Compliance:
  - The system aligns with the Philippines’ Data Privacy Act of 2012, incorporating retention policies and periodic audits.

### Integration Design

The integration design ensures seamless connections with external systems and services, fostering data sharing and collaboration.

- API Integration:
  - RESTful APIs enable controlled access to non-sensitive data, secured with API keys and rate limits.
  - Webhooks deliver real-time notifications (e.g., for new coordination requests).
- Third-Party Services:
  - GIS services (e.g., Google Maps API) enhance mapping, while cloud storage (e.g., AWS S3) manages documents.
  - Email/SMS gateways send automated alerts.
- Government System Interoperability:
  - JSON/XML protocols facilitate data exchange with BARMM or national systems (e.g., PSA). SFTP ensures secure file transfers.
- Single Sign-On (SSO):
  - SSO via OAuth 2.0 or SAML integrates with government credentials.
- Offline Syncing:
  - Field staff can gather data offline using local storage (e.g., IndexedDB), with automatic syncing upon reconnection.
- Extensibility:
  - A modular codebase simplifies future feature additions or integrations.

