import { DefaultTheme, defineConfig } from "vitepress";

export default defineConfig({
  title: "Blackrose",
  description: "TypeSafe decision layer for LLM apps — allow | review | block",
  sitemap: {
    hostname: "https://blackrose.dev",
  },
  lang: "en-US",
  lastUpdated: true,
  themeConfig: {
    nav: nav(),
    sidebar: {
      "/guide/": [
        {
          text: "Guide",
          items: [
            { text: "Getting started", link: "/guide/getting-started" },
            { text: "Verdicts", link: "/guide/verdicts" },
            { text: "Policy", link: "/guide/policy" },
            { text: "Python API", link: "/guide/python" },
            { text: "JavaScript API", link: "/guide/javascript" },
            { text: "Integration", link: "/guide/integration" },
          ],
        },
      ],
    },
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/Dino-Kupinic/blackrose",
      },
      {
        icon: "twitter",
        link: "https://x.com/DinoKupinic",
      },
    ],
    search: {
      provider: "local",
    },
    editLink: {
      pattern: "https://github.com/Dino-Kupinic/blackrose/edit/develop/docs/src/:path",
      text: "Edit this page on GitHub",
    },
    footer: {
      message: "Released under the MIT License.",
      copyright: "Copyright © 2024-present Dino Kupinic",
    },
  },
});

function nav(): DefaultTheme.NavItem[] {
  return [
    { text: "Home", link: "/" },
    { text: "Guide", link: "/guide/getting-started" },
    {
      text: "GitHub",
      link: "https://github.com/Dino-Kupinic/blackrose",
    },
  ];
}
