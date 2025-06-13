# Extended-Localization
Localization source repo for Lotr: Renewed Extended. Any and all localizations accepted.

Please check the [Website for up-to-date-status](https://lotrextendedteam.github.io/Extended-Localization/) for all localizations.

## Locations for Extended Localizations:
*  Localization files are in [/langs/](https://github.com/maximuslotro/Extended-Localization/tree/main/langs)
*  Speechbank localization files are in [/speechbanks/](https://github.com/maximuslotro/Extended-Localization/tree/main/speechbanks) (Including the English speechbanks)
*  The latest up-to-date english translation for Extended can be found in here: [/langs/en_us.json/](https://github.com/maximuslotro/Extended-Localization/tree/main/langs/en_us.json) (in the langs folder)

## Updating/Override Renewed Localizations:
*  Renewed localization override files are in [/langs_renewed_override/](https://github.com/maximuslotro/Extended-Localization/tree/main/langs_renewed_override)
*  Renewed Speechbank localization override files are in [/speechbanks_renewed_override/](https://github.com/maximuslotro/Extended-Localization/tree/main/speechbanks_renewed_override)

## Contributing Instructions:
### Localizations:
If you wish to contribute, fork the repo, then add your new/updated lang files to your fork, then create a PR to this repo to have your localizations added into Extended.

When updating localizations, ensure removed lines are removed, and all new lines are added. If the contents of a key changes, ensure your translation reflects the new value/meaning.

Check the [Website](https://lotrextendedteam.github.io/Extended-Localization/) for info on what to correct.

## Github Tutorials
*  How to fork: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#forking-a-repository
*  How to push files: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository#adding-a-file-to-a-repository-on-github
*  How to open a PR to get your localizations added: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request

### Website Maintenance:
1. To work with mkdocs, first fork the repo and clone it to your local machine.
2. If you don't have Python or pip installed, I would recommend installing it, as later steps require it.
3. Next run the following command to set up all the required packages for a local instance.
~~~
 pip install mkdocs-material mkdocs-htmlproofer-plugin mkdocs-git-revision-date-localized-plugin mkdocs-glightbox "mkdocs-material[imaging]"
~~~
4. With your shell of choice, run the following command to start the live-reloading local-instance docs server.
~~~
 mkdocs serve
~~~
5. Now every change you make to your wiki instance will be reflected live in your web browser.
6. When you are satisfied your changes, open a PR to the main repo to have your changes/additions added to the wiki.
7. Profit?

## Note
- Do not contribute to the gh-pages branch, as this branch is created automatically when the Docs Deploy workflow is run.
- Also don't edit any Github workflows, your PR will not be accepted if you edit them, only staff should ever need to deploy to them folders.
