# Publishing the Ars Magna Defluens GitHub Wiki

The companion wiki is prepared for:

- Repository: [`MA-Gustave/Ars-Magna-Defluens`](https://github.com/MA-Gustave/Ars-Magna-Defluens)
- Wiki URL: <https://github.com/MA-Gustave/Ars-Magna-Defluens/wiki>
- Wiki Git remote: `https://github.com/MA-Gustave/Ars-Magna-Defluens.wiki.git`

The repository's GitHub metadata reports `has_wiki=true`. **Wiki enabled does not guarantee the first page was initialized.** The assistant's GitHub connection was **read-only**; this delivery contains files for manual publication and does not imply that GitHub was modified.

## Package layout

```text
repository/
  README.md
  docs/                 # English documentation and evidence
wiki/
  Home.md
  _Sidebar.md
  _Footer.md
  Getting-Started.md
  ...                   # task-oriented pages
Publish-GitHub-Wiki.ps1
INSTALL_AND_PUBLISH.md
```

## Update the code repository

Copy `repository/README.md` to the repository root as `README.md` and the contents of `repository/docs/` into `docs/`, keeping filenames unchanged. Review any local modifications before replacing files. Commit the documentation using the usual repository contribution workflow; the GitHub connection used to prepare this package cannot push directly.

## Publish the wiki by Git

1. In GitHub, open **Wiki**. If no page exists yet, use **Create the first page**, name it `Home`, save it, then continue. This initializes the `.wiki.git` remote.
2. Install/configure **Git for Windows** and ensure your GitHub identity has wiki write permissions.
3. From the extracted package root, preview the pages:

   ```powershell
   .\Publish-GitHub-Wiki.ps1
   ```

4. Publish new pages, without overwriting different existing pages:

   ```powershell
   .\Publish-GitHub-Wiki.ps1 -Publish
   ```

5. If the initialized wiki has a placeholder `Home.md` or old content you explicitly want to replace, inspect it first, then publish with:

   ```powershell
   .\Publish-GitHub-Wiki.ps1 -Publish -OverwriteExisting
   ```

The publisher clones the wiki into a fresh temporary directory, checks for page conflicts, adds only `.md` files, commits and performs a **normal push**. It never force-pushes, deletes unrelated wiki pages or changes the code repository.

## Manual alternative

```powershell
git clone https://github.com/MA-Gustave/Ars-Magna-Defluens.wiki.git
Copy-Item .\wiki\*.md .\Ars-Magna-Defluens.wiki\ -Force
cd .\Ars-Magna-Defluens.wiki
git add -- '*.md'
git commit -m 'Add English Ars Magna Defluens documentation wiki'
git push origin HEAD
```

Only use `-Force` after reviewing existing wiki pages. If the remote is not initialized, create `Home` through the GitHub Wiki UI before cloning. Authentication and network access are required to publish.

## Navigation

GitHub Wiki interprets `_Sidebar.md` and `_Footer.md` as navigation elements. The `[[Page Name]]` links target the other included Markdown pages and are checked by the package validator. Documents within the wiki link back to the repository's `docs/` using its canonical GitHub URL.
