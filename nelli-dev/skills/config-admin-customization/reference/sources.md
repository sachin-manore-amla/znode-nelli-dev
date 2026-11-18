# Sources
Answers: which KB articles and release notes back this skill, and how each was read.

| Article | URL | Read |
|---|---|---|
| Admin Customization | https://support.znode.com/support/solutions/articles/43000761412-admin-customization | summary of full article (70-80) |
| Admin Customizations in Znode | https://support.znode.com/support/solutions/articles/43000785604-admin-customizations-in-znode | summary of full article (70-80) |
| Admin Setup, Installation & Configuration | https://support.znode.com/support/solutions/articles/43000761482-admin-setup-installation-configuration | summary; it says nothing about customization hooks |
| Admin Troubleshooting Guide | https://support.znode.com/support/solutions/articles/43000761488-admin-troubleshooting-guide | summary; says nothing about custom pages, iFrame or menus |
| 10.0.1.0 Release Notes (May 12, 2025) | https://support.znode.com/support/solutions/articles/43000761451-10-0-1-0-release-notes-may-12-2025 | WYSIWYG editor for Content Details |
| 10.10.1.0 Release Notes (May 12, 2026) | https://support.znode.com/support/solutions/articles/43000784440-10-10-1-0-release-notes-may-12-2026 | CSP change (Storefront scope) |
| API Customization Guide | https://support.znode.com/support/solutions/articles/43000761402-api-customization-guide | no custom Admin page content |

Where the Admin Setup article is useful: it lists the Admin `appsettings` keys for local development (API root, gateway, Admin address), the `Caching` and `EventBus` sections. Nothing there changes how custom pages work.

Troubleshooting article items that apply: check the Admin role claim when role-based access fails; clear cache keys after changes; use the browser network tab for CSS/JS 404s. It does not describe custom pages.
