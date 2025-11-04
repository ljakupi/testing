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
        id: 'requirements-overview/requirements-overview',
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
        id: 'constraints/constraints',
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
            id: 'constraints/conventions/conventions',
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
        id: 'architecture-overview/architecture-overview',
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
        id: 'detailed-architecture/detailed-architecture',
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
            id: 'detailed-architecture/interface-inventory/interface-inventory',
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
        id: 'multi-processing-center/multi-processing-center',
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
        id: 'architectural-risks-issues/architectural-risks-issues',
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
