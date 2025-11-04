---
id: glossary
title: Glossary
sidebar_label: 8. Glossary
sidebar_position: 11
---

# Glossary

This section provides definitions of terms, acronyms, and concepts used throughout this Solution Architecture Design documentation.

## A

**ABAC (Attribute-Based Access Control)**
: Access control paradigm whereby access rights are granted through policies that combine attributes (user attributes, resource attributes, environment attributes).

**ADR (Architecture Decision Record)**
: A document that captures an important architectural decision made along with its context and consequences.

**Aggregate**
: A cluster of domain objects that can be treated as a single unit in Domain-Driven Design. All external access to the aggregate should go through the aggregate root.

**API (Application Programming Interface)**
: A set of protocols, routines, and tools for building software applications that specifies how software components should interact.

**API Gateway**
: A server that acts as an API front-end, receives API requests, enforces throttling and security policies, passes requests to the back-end service, and then passes the response back to the requester.

**APM (Application Performance Monitoring)**
: The monitoring and management of performance and availability of software applications to detect and diagnose complex application performance problems.

## B

**Bounded Context**
: A central pattern in Domain-Driven Design defining the scope of a domain model where a particular domain model is well-defined and applicable.

**Business Layer**
: The layer of an application that contains business logic and rules, orchestrates business processes, and enforces business constraints.

**Business Logic**
: The part of a program that encodes the real-world business rules that determine how data can be created, displayed, stored, and changed.

## C

**Cache**
: A hardware or software component that stores data so that future requests for that data can be served faster.

**CDN (Content Delivery Network)**
: A geographically distributed network of proxy servers and their data centers to provide high availability and performance by distributing the service spatially relative to end users.

**CI/CD (Continuous Integration / Continuous Deployment)**
: A method to frequently deliver apps to customers by introducing automation into the stages of app development.

**Circuit Breaker**
: A design pattern used in software development to detect failures and encapsulate the logic of preventing a failure from constantly recurring during maintenance, temporary external system failure, or unexpected system difficulties.

**CORS (Cross-Origin Resource Sharing)**
: A mechanism that allows restricted resources on a web page to be requested from another domain outside the domain from which the first resource was served.

## D

**DAO (Data Access Object)**
: An object that provides an abstract interface to some type of database or other persistence mechanism.

**DAST (Dynamic Application Security Testing)**
: The process of testing an application or software product in an operating state to find security vulnerabilities.

**DDD (Domain-Driven Design)**
: An approach to software development that centers the development on programming a domain model that has a rich understanding of the processes and rules of a domain.

**DMZ (Demilitarized Zone)**
: A physical or logical subnetwork that contains and exposes an organization's external-facing services to an untrusted network, usually the Internet.

**Domain Event**
: Something that happened in the domain that domain experts care about.

**DTO (Data Transfer Object)**
: An object that carries data between processes to reduce the number of method calls.

## E

**Entity**
: An object that is identified by its consistent thread of continuity, as opposed to traditional objects which are defined by their attributes.

**ETL (Extract, Transform, Load)**
: The general procedure of copying data from one or more sources into a destination system which represents the data differently from the source(s).

**Eventual Consistency**
: A consistency model used in distributed computing to achieve high availability that informally guarantees that, if no new updates are made to a given data item, eventually all accesses to that item will return the last updated value.

## F

**Failover**
: Switching to a redundant or standby server, system, hardware component, or network upon the failure or abnormal termination of the previously active server, system, hardware component, or network.

**Fault Tolerance**
: The property that enables a system to continue operating properly in the event of the failure of some of its components.

## G

**GDPR (General Data Protection Regulation)**
: A regulation in EU law on data protection and privacy in the European Union and the European Economic Area.

**GraphQL**
: A query language for APIs and a runtime for fulfilling those queries with your existing data.

**gRPC**
: A modern open source high performance Remote Procedure Call (RPC) framework that can run in any environment.

## H

**High Availability (HA)**
: A characteristic of a system that aims to ensure an agreed level of operational performance, usually uptime, for a higher than normal period.

**Horizontal Scaling**
: Adding more machines to your pool of resources (also known as "scaling out").

**HTTP/HTTPS**
: Hypertext Transfer Protocol / Secure. The foundation of data communication for the World Wide Web.

## I

**IaaS (Infrastructure as a Service)**
: Online services that provide high-level APIs used to dereference various low-level details of underlying network infrastructure like physical computing resources, location, data partitioning, scaling, security, backup, etc.

**IdP (Identity Provider)**
: A system entity that creates, maintains, and manages identity information for principals and also provides authentication services to relying applications.

**IoC (Inversion of Control)**
: A design principle in which custom-written portions of a computer program receive the flow of control from a generic framework.

**JWT (JSON Web Token)**
: An open standard that defines a compact and self-contained way for securely transmitting information between parties as a JSON object.

## K

**KPI (Key Performance Indicator)**
: A measurable value that demonstrates how effectively a company is achieving key business objectives.

**Kubernetes**
: An open-source container-orchestration system for automating application deployment, scaling, and management.

## L

**Latency**
: The time interval between the stimulation and response, or the time delay between an action and a reaction.

**Load Balancer**
: A device that acts as a reverse proxy and distributes network or application traffic across a number of servers.

**Loose Coupling**
: A method of interconnecting the components in a system or network so that those components depend on each other to the least extent practicable.

## M

**Microservices**
: An architectural style that structures an application as a collection of loosely coupled services, which implement business capabilities.

**Middleware**
: Software that provides common services and capabilities to applications outside of what's offered by the operating system.

**MTBF (Mean Time Between Failures)**
: The predicted elapsed time between inherent failures of a mechanical or electronic system during normal system operation.

**MTTR (Mean Time To Repair)**
: The average time required to repair a failed component or device.

**MVC (Model-View-Controller)**
: An architectural pattern that separates an application into three main logical components: the model, the view, and the controller.

## N

**NFR (Non-Functional Requirement)**
: A requirement that specifies criteria that can be used to judge the operation of a system, rather than specific behaviors (functional requirements).

**NoSQL**
: A database that provides a mechanism for storage and retrieval of data that is modeled in means other than the tabular relations used in relational databases.

## O

**OAuth**
: An open standard for access delegation, commonly used as a way for users to grant websites or applications access to their information on other websites.

**ORM (Object-Relational Mapping)**
: A programming technique for converting data between incompatible type systems using object-oriented programming languages.

**OpenAPI**
: A specification for machine-readable interface files for describing, producing, consuming, and visualizing RESTful web services (formerly known as Swagger).

## P

**PaaS (Platform as a Service)**
: A category of cloud computing services that provides a platform allowing customers to develop, run, and manage applications without the complexity of building and maintaining the infrastructure.

**PII (Personally Identifiable Information)**
: Any data that could potentially be used to identify a particular person.

**Presentation Layer**
: The layer that interacts with users and displays data, handling all user interface and client communication logic.

## R

**RBAC (Role-Based Access Control)**
: An approach to restricting system access to authorized users based on their role within an organization.

**Repository Pattern**
: A design pattern that mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects.

**REST (Representational State Transfer)**
: An architectural style for providing standards between computer systems on the web, making it easier for systems to communicate with each other.

**RPO (Recovery Point Objective)**
: The maximum targeted period in which data might be lost from an IT service due to a major incident.

**RTO (Recovery Time Objective)**
: The targeted duration of time and a service level within which a business process must be restored after a disaster.

## S

**SaaS (Software as a Service)**
: A software licensing and delivery model in which software is licensed on a subscription basis and is centrally hosted.

**SAST (Static Application Security Testing)**
: A type of security testing that analyzes source code to find security vulnerabilities before an application is executed.

**Service Mesh**
: A dedicated infrastructure layer for handling service-to-service communication to make it manageable, visible, and controlled.

**SLA (Service Level Agreement)**
: A commitment between a service provider and a client defining the level of service expected from the service provider.

**SOLID Principles**
: Five design principles intended to make software designs more understandable, flexible, and maintainable. (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)

**SPA (Single Page Application)**
: A web application or website that interacts with the user by dynamically rewriting the current page rather than loading entire new pages from a server.

**SQL (Structured Query Language)**
: A domain-specific language used in programming and designed for managing data held in a relational database management system.

**SSL/TLS (Secure Sockets Layer / Transport Layer Security)**
: Cryptographic protocols designed to provide communications security over a computer network.

## T

**Technical Debt**
: The implied cost of additional rework caused by choosing an easy solution now instead of using a better approach that would take longer.

**Throughput**
: The amount of work or information that can be processed in a given period of time.

**TPS (Transactions Per Second)**
: A measure of the number of atomic actions performed by a computer system in a second.

## U

**UAT (User Acceptance Testing)**
: The last phase of the software testing process where actual software users test the software to make sure it can handle required tasks in real-world scenarios.

**UML (Unified Modeling Language)**
: A standardized modeling language consisting of an integrated set of diagrams, developed to help system and software developers specify, visualize, construct, and document the artifacts of software systems.

## V

**Value Object**
: An object that contains attributes but has no conceptual identity. They should be treated as immutable in Domain-Driven Design.

**Vertical Scaling**
: Adding more power (CPU, RAM) to an existing machine (also known as "scaling up").

**VPN (Virtual Private Network)**
: A technology that creates a safe and encrypted connection over a less secure network, such as the Internet.

## W

**WAF (Web Application Firewall)**
: A firewall that monitors, filters, and blocks HTTP traffic to and from a web application.

**WCAG (Web Content Accessibility Guidelines)**
: Guidelines for making web content more accessible to people with disabilities.

**Webhook**
: A method of augmenting or altering the behavior of a web page or web application with custom callbacks.

## X

**XSS (Cross-Site Scripting)**
: A type of security vulnerability typically found in web applications that enables attackers to inject client-side scripts into web pages viewed by other users.

## Acronyms Quick Reference

| Acronym | Full Term |
|---------|-----------|
| **API** | Application Programming Interface |
| **CDN** | Content Delivery Network |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CORS** | Cross-Origin Resource Sharing |
| **CRUD** | Create, Read, Update, Delete |
| **DTO** | Data Transfer Object |
| **GDPR** | General Data Protection Regulation |
| **gRPC** | Google Remote Procedure Call |
| **HTTP** | Hypertext Transfer Protocol |
| **HTTPS** | Hypertext Transfer Protocol Secure |
| **IoC** | Inversion of Control |
| **JWT** | JSON Web Token |
| **MTBF** | Mean Time Between Failures |
| **MTTR** | Mean Time To Repair |
| **MVC** | Model-View-Controller |
| **NoSQL** | Not Only SQL |
| **OAuth** | Open Authorization |
| **ORM** | Object-Relational Mapping |
| **PII** | Personally Identifiable Information |
| **RBAC** | Role-Based Access Control |
| **REST** | Representational State Transfer |
| **RPO** | Recovery Point Objective |
| **RTO** | Recovery Time Objective |
| **SaaS** | Software as a Service |
| **SAST** | Static Application Security Testing |
| **SLA** | Service Level Agreement |
| **SQL** | Structured Query Language |
| **SSL** | Secure Sockets Layer |
| **TLS** | Transport Layer Security |
| **UAT** | User Acceptance Testing |
| **UML** | Unified Modeling Language |
| **VPN** | Virtual Private Network |
| **WAF** | Web Application Firewall |
| **WCAG** | Web Content Accessibility Guidelines |
| **XSS** | Cross-Site Scripting |

---

:::tip Adding Terms
This glossary should be updated as new terms and concepts are introduced. If you encounter a term not defined here, please add it.
:::
