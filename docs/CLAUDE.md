# Implementation Guide: Docusaurus Solution Architecture Design Documentation

## Project Overview
Create a Docusaurus documentation site for Solution Architecture Design that is:
- Easy for non-technical users to update (primarily markdown files)
- Deployable to GitLab Pages
- Minimalist and well-organized
- TypeScript-based with clear structure
- Includes dark/light mode toggle (default Docusaurus feature)

## Implementation Steps

### 1. Initialize Docusaurus Project

Create a new Docusaurus site using the latest version:
```bash
npx create-docusaurus@latest . classic --typescript
```

This will create:
- `docs/` - All documentation markdown files (main content area)
- `src/` - React components and pages
- `static/` - Static assets (images, files)
- `docusaurus.config.ts` - Main configuration file
- `sidebars.ts` - Sidebar navigation configuration

### 2. Clean Up Default Files

Remove unnecessary default files:
- Delete all files in `docs/` directory (we'll create our own structure)
- Delete `blog/` directory (not needed for this project)
- Keep `src/pages/index.tsx` but simplify it to redirect to docs

### 3. Create Documentation Structure

Create the following markdown files in the `docs/` directory:

```
docs/
├── index.md (Introduction)
├── prerequisites.md
├── requirements-overview/
│   ├── index.md
│   ├── functional-requirements.md
│   └── non-functional-requirements.md
├── stakeholders.md
├── constraints/
│   ├── index.md
│   ├── technical-organizational-constraints.md
│   └── conventions/
│       ├── index.md
│       └── enterprise-standards.md
├── architecture-overview/
│   ├── index.md
│   ├── business-context.md
│   └── logical-solution-overview.md
├── detailed-architecture/
│   ├── index.md
│   ├── technical-context.md
│   ├── interface-inventory/
│   │   ├── index.md
│   │   ├── interface-1.md
│   │   └── interface-2.md
│   ├── presentation-layer.md
│   └── business-layer.md
├── multi-processing-center/
│   ├── index.md
│   └── architectural-concerns-testing.md
├── architectural-decisions.md
├── architectural-risks-issues/
│   ├── index.md
│   ├── architectural-risks.md
│   └── architectural-issues.md
└── glossary.md
```

### 4. Configure Sidebars

Update `sidebars.ts` to reflect the documentation structure:

```typescript
import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  solutionArchitectureSidebar: [
    {
      type: 'doc',
      id: 'index',
      label: '1. Introduction',
    },
    {
      type: 'doc',
      id: 'prerequisites',
      label: '1.1. Prerequisites',
    },
    {
      type: 'category',
      label: '1.2. Requirements Overview',
      link: {
        type: 'doc',
        id: 'requirements-overview/index',
      },
      items: [
        {
          type: 'doc',
          id: 'requirements-overview/functional-requirements',
          label: '1.2.1. Functional Requirements',
        },
        {
          type: 'doc',
          id: 'requirements-overview/non-functional-requirements',
          label: '1.2.2. Non-Functional Requirements',
        },
      ],
    },
    {
      type: 'doc',
      id: 'stakeholders',
      label: '1.3. Stakeholders',
    },
    {
      type: 'category',
      label: '2. Constraints',
      link: {
        type: 'doc',
        id: 'constraints/index',
      },
      items: [
        {
          type: 'doc',
          id: 'constraints/technical-organizational-constraints',
          label: '2.1. Technical / Organizational Constraints',
        },
        {
          type: 'category',
          label: '2.2. Conventions',
          link: {
            type: 'doc',
            id: 'constraints/conventions/index',
          },
          items: [
            {
              type: 'doc',
              id: 'constraints/conventions/enterprise-standards',
              label: '2.2.1. Enterprise Standards',
            },
          ],
        },
      ],
    },
    {
      type: 'category',
      label: '3. Architecture Overview',
      link: {
        type: 'doc',
        id: 'architecture-overview/index',
      },
      items: [
        {
          type: 'doc',
          id: 'architecture-overview/business-context',
          label: '3.1. Business Context',
        },
        {
          type: 'doc',
          id: 'architecture-overview/logical-solution-overview',
          label: '3.2. Logical Solution Overview',
        },
      ],
    },
    {
      type: 'category',
      label: '4. Detailed Architecture',
      link: {
        type: 'doc',
        id: 'detailed-architecture/index',
      },
      items: [
        {
          type: 'doc',
          id: 'detailed-architecture/technical-context',
          label: '4.1. Technical Context',
        },
        {
          type: 'category',
          label: '4.2. Interface Inventory',
          link: {
            type: 'doc',
            id: 'detailed-architecture/interface-inventory/index',
          },
          items: [
            {
              type: 'doc',
              id: 'detailed-architecture/interface-inventory/interface-1',
              label: '4.2.1. Interface 1',
            },
            {
              type: 'doc',
              id: 'detailed-architecture/interface-inventory/interface-2',
              label: '4.2.2. Interface 2',
            },
          ],
        },
        {
          type: 'doc',
          id: 'detailed-architecture/presentation-layer',
          label: '4.3. Presentation Layer',
        },
        {
          type: 'doc',
          id: 'detailed-architecture/business-layer',
          label: '4.4. Business Layer',
        },
      ],
    },
    {
      type: 'category',
      label: '5. Multi-Processing Center',
      link: {
        type: 'doc',
        id: 'multi-processing-center/index',
      },
      items: [
        {
          type: 'doc',
          id: 'multi-processing-center/architectural-concerns-testing',
          label: '5.1. Architectural Concerns for Testing',
        },
      ],
    },
    {
      type: 'doc',
      id: 'architectural-decisions',
      label: '6. Architectural Decisions',
    },
    {
      type: 'category',
      label: '7. Architectural Risks and Issues',
      link: {
        type: 'doc',
        id: 'architectural-risks-issues/index',
      },
      items: [
        {
          type: 'doc',
          id: 'architectural-risks-issues/architectural-risks',
          label: '7.1. Architectural Risks',
        },
        {
          type: 'doc',
          id: 'architectural-risks-issues/architectural-issues',
          label: '7.2. Architectural Issues',
        },
      ],
    },
    {
      type: 'doc',
      id: 'glossary',
      label: '8. Glossary',
    },
  ],
};

export default sidebars;
```

### 5. Configure Docusaurus

Update `docusaurus.config.ts` with GitLab Pages configuration:

Key changes needed:
- Set `url` to your GitLab Pages URL (e.g., `https://username.gitlab.io`)
- Set `baseUrl` to `/repository-name/` (e.g., `/solution-architecture-docs/`)
- Set `organizationName` to your GitLab username/group
- Set `projectName` to your repository name
- Disable blog plugin
- Configure navbar with title and dark/light mode toggle
- Set docs as the default landing page

### 6. Simplify Home Page

Update `src/pages/index.tsx` to redirect to documentation:

```typescript
import React from 'react';
import {Redirect} from '@docusaurus/router';

export default function Home(): JSX.Element {
  return <Redirect to="/docs" />;
}
```

Or create a simple landing page that links to the documentation.

### 7. Create Markdown File Templates

Each markdown file should have frontmatter with at least a title:

```markdown
---
title: Page Title
sidebar_position: 1
---

# Page Title

Content goes here...
```

Create placeholder content for all markdown files so non-technical users have a starting point.

### 8. GitLab CI/CD Configuration

Create `.gitlab-ci.yml` in the project root for automated deployment:

```yaml
image: node:18

cache:
  paths:
    - node_modules/
    - .npm/

before_script:
  - npm ci --cache .npm --prefer-offline

pages:
  stage: deploy
  script:
    - npm run build
    - mv build public
  artifacts:
    paths:
      - public
  only:
    - main
```

### 9. Update Package.json Scripts

Ensure the following scripts are present:
```json
{
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve",
    "write-translations": "docusaurus write-translations",
    "write-heading-ids": "docusaurus write-heading-ids",
    "typecheck": "tsc"
  }
}
```

### 10. Create README.md

Create a README.md file with instructions for non-technical users:

```markdown
# Solution Architecture Design Documentation

This repository contains the Solution Architecture Design documentation built with Docusaurus.

## For Content Editors

All documentation content is in markdown files located in the `docs/` folder. You can edit these files directly to update the documentation.

### How to Edit Content

1. Navigate to the `docs/` folder
2. Find the markdown file you want to edit (e.g., `docs/prerequisites.md`)
3. Edit the file using any text editor or directly on GitLab
4. Commit your changes
5. The site will automatically rebuild and deploy (takes ~2-3 minutes)

### Markdown Basics

- Headers: Use `#` for headings (# H1, ## H2, ### H3)
- Bold: `**bold text**`
- Italic: `*italic text*`
- Lists: Use `-` or `1.` for bullet/numbered lists
- Links: `[link text](url)`
- Images: `![alt text](path/to/image.png)`

## For Developers

### Local Development

```bash
npm install
npm start
```

This starts a local development server at `http://localhost:3000`.

### Build

```bash
npm run build
```

### Deployment

The site automatically deploys to GitLab Pages when you push to the `main` branch.
```

### 11. Implementation Checklist

- [ ] Initialize Docusaurus with TypeScript template
- [ ] Remove default blog and demo docs
- [ ] Create all required markdown files with placeholder content
- [ ] Configure `sidebars.ts` with proper structure
- [ ] Update `docusaurus.config.ts` for GitLab Pages
- [ ] Simplify home page to redirect to docs
- [ ] Create `.gitlab-ci.yml` for automated deployment
- [ ] Create user-friendly README.md
- [ ] Add `.gitignore` (should be created by Docusaurus)
- [ ] Test local build with `npm run build`
- [ ] Commit and push to GitLab
- [ ] Verify GitLab Pages deployment

## Key Files for Non-Technical Users

The following files should ONLY be edited by non-technical users:
- **All files in `docs/` directory** - Documentation content
- **`static/` directory** - Images and static assets

The following files should NOT be edited by non-technical users:
- `docusaurus.config.ts` - Technical configuration
- `sidebars.ts` - Navigation structure
- `package.json` - Dependencies
- `.gitlab-ci.yml` - Deployment configuration
- Files in `src/` directory - React components

## Notes

1. **Dark/Light Mode**: Enabled by default in Docusaurus, no additional configuration needed
2. **Sidebar Navigation**: Automatically generated from `sidebars.ts`
3. **Search**: Consider enabling Algolia DocSearch later if needed
4. **Versioning**: Not implemented initially, can be added later if needed
5. **GitLab Pages URL**: Will be `https://username.gitlab.io/repository-name/` after deployment

## Folder Structure Summary

```
sad/
├── docs/                    # All markdown documentation (editable by non-technical users)
├── src/                     # React/TypeScript source (technical only)
│   └── pages/              # Custom pages
├── static/                  # Static assets like images (editable by non-technical users)
├── docusaurus.config.ts    # Main configuration (technical only)
├── sidebars.ts             # Sidebar structure (technical only)
├── package.json            # Dependencies (technical only)
├── .gitlab-ci.yml          # CI/CD configuration (technical only)
├── tsconfig.json           # TypeScript configuration (technical only)
└── README.md               # User guide
```

## GitLab Pages Setup

After pushing to GitLab:
1. Go to Settings > Pages in your GitLab repository
2. Wait for the pipeline to complete
3. Your site will be available at the URL shown in Settings > Pages
4. Update `docusaurus.config.ts` with the correct URL if needed

## Content Organization Tips

1. Each major section should have its own folder with an `index.md`
2. Use consistent naming: lowercase with hyphens (e.g., `technical-context.md`)
3. Include frontmatter in each markdown file for proper navigation
4. Use relative links between documents: `[link](./other-page.md)`
5. Store images in `static/img/` and reference as `/img/image-name.png`
