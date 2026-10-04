import { DefaultTheme } from "vitepress"

export default {
  title: "Blackrose",
  description: "Decision layer for LLM apps on any decision model — allow | review | block",
  sitemap: {
    hostname: "https://blackrose.dev"
  },
  lang: "en-US",
  themeConfig: {
    nav: nav(),
    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/Dino-Kupinic/blackrose"
      },
      {
        icon: "twitter",
        link: "https://x.com/DinoKupinic"
      }
    ],
    search: {
      provider: "local"
    },
    footer: {
      message: "Released under the MIT License.",
      copyright: "Copyright © 2024-present Dino Kupinic"
    }
  },
  editLink: {
    pattern: "https://github.com/Dino-Kupinic/blackrose/edit/main/docs/:path",
    text: "Edit this page on GitHub"
  },
  lastUpdated: true
}

function nav(): DefaultTheme.NavItem[] {
  return [
    {
      text: "Home",
      link: "/"
    },
    {
      text: "Guide",
      link: "/guide/getting-started"
    },
    {
      text: "Providers",
      link: "/guide/providers"
    }
  ]
}
