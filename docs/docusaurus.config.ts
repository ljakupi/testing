import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Solution Architecture Design',
  tagline: 'Comprehensive documentation for our solution architecture',
  favicon: 'img/favicon.ico',

  // Future flags
  future: {
    v4: true,
  },

  // Set the production url of your site here
  // For GitLab Pages: https://username.gitlab.io
  url: 'https://username.gitlab.io',

  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitLab Pages: usually '/<repository-name>/'
  // Update this to match your GitLab repository name
  baseUrl: '/docs/',

  // GitLab Pages deployment config
  // Update these to match your GitLab username/group and repository
  organizationName: 'username', // Your GitLab username or group
  projectName: 'docs', // Your repository name

  onBrokenLinks: 'warn', // Set to 'throw' after configuring correct baseUrl and url for your GitLab Pages
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/', // Serve docs at root
          // Remove or update the editUrl if you want "Edit this page" links
          // editUrl: 'https://gitlab.com/username/docs/-/tree/main/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',

    // Dark/Light mode toggle (light theme as default)
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },

    navbar: {
      title: 'SAD',
      logo: {
        alt: 'SAD Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'solutionArchitectureSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          type: 'search',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Introduction',
              to: '/',
            },
            {
              label: 'Architecture Overview',
              to: '/architecture-overview/architecture-overview',
            },
            {
              label: 'Glossary',
              to: '/glossary',
            },
          ],
        },
        {
          title: 'Quick Links',
          items: [
            {
              label: 'Requirements',
              to: '/requirements-overview/requirements-overview',
            },
            {
              label: 'Constraints',
              to: '/constraints/constraints',
            },
            {
              label: 'Architectural Decisions',
              to: '/architectural-decisions',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'Architectural Risks',
              to: '/architectural-risks-issues/architectural-risks',
            },
            {
              label: 'Detailed Architecture',
              to: '/detailed-architecture/detailed-architecture',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Solution Architecture Documentation. Built with Docusaurus.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'typescript', 'javascript', 'json', 'yaml', 'markdown'],
    },

    // Table of contents configuration
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  } satisfies Preset.ThemeConfig,

  // Mermaid support for diagrams
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
};

export default config;
