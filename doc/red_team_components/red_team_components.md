# Red Team Components

This page provides an overview of the key Red Teaming components supported by SLRT. Each component is designed to facilitate different aspects of offensive security operations, including command and control, payload delivery, red team collaboration, and phishing campaigns.

## Overview
Currently, SLRT supports the following Red Teaming Components:
- Sliver C2 Server - A flexible and stealthy Command and Control (C2) framework.
- Nginx Redirector - A traffic redirector for concealing and managing C2 communications.
- VeilDrop Payload Server - A payload distribution server that authenticates clients via user-agent verification.
- Ghostwriter - A red team collaboration tool for managing operations and reporting.
- EvilGoPhish - A phishing framework for conducting realistic social engineering campaigns.

## Sliver C2 Server
**Description:**
The Sliver C2 Server is a highly customizable and open-source Command and Control (C2) framework. It enables operators to manage implants, execute post-exploitation activities, and maintain persistent access.

**Key Features:**
- Supports multiple communication protocols (HTTP, DNS, mTLS, WireGuard).
- Provides multiplayer capability for collaborative operations.
- Includes built-in encryption and evasion techniques.

For deployment details, refer to the [Sliver Deployment Wiki](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Red-Team-Components/%7BSliver%7D).

## Nginx Redirector
**Description:**
The Nginx Redirector acts as a traffic proxy that forwards authorized requests to the Sliver C2 server while presenting a legitimate-looking website to unauthorized users.

**Key Features:**
- Redirects traffic based on user-agent and authentication tokens.
- Serves a decoy HTML page for unauthorized requests.
- Uses Nginx for lightweight and high-performance handling.

For deployment details, refer to the [Nginx Redirector Wiki](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Red-Team-Components/Redirector).

## VeilDrop Payload Server
**Description:**
The VeilDrop Payload Server is a secure file distribution server that serves payloads only to authenticated clients. It verifies access based on user-agent values.

**Key Features:**
- Flask-based web server for lightweight operation.
- User-agent authentication to control payload access.
- Logging for tracking all download attempts.

For deployment details, refer to the [VeilDrop Deployment Wiki](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Red-Team-Components/VeilDrop).

## Ghostwriter Red Team Collaboration Tool
**Description:**
Ghostwriter is an open-source red team collaboration and reporting tool designed for managing engagements, tracking findings, and generating client-ready reports.

**Key Features:**
- Stores and manages operation logs.
- Integrates with external tools for automation.
- Generates customizable reports for engagements.

For deployment details, refer to the [Ghostwriter Deployment Wiki](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Red-Team-Components/Ghostwriter).

## EvilGoPhish
**Description:**
EvilGoPhish is a phishing framework designed to help red teams conduct realistic social engineering campaigns.

**Key Features:**
- Automates the creation and deployment of phishing campaigns.
- Provides templates for realistic email scenarios.
- Tracks user interactions and credential harvesting.

For deployment details, refer to the [EvilGoPhish Deployment Wiki](https://gitlab.fh-ooe.at/P41540/2024-streamlined-red-teaming-mpr3/-/wikis/Red-Team-Components/EvilGophish).

