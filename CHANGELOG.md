## CHANGELOG

### [24.6.0] - June 20, 2024
- Added an actual CHANGELOG.md instead of relying on GitHub Release history
- The `Content-Security-Policy` header is now set as a HTTP response header and uses a standard value for all pages
- The `Content-Security-Policy` header now allows an `img-src` of all, which means external images are now supported in Markdown
- Updated `github-markdown-css` JavaScript library to 5.6.1

### [24.5.0] - May 15, 2024
- Drop support for Python 3.8
- Updated `bootstrap` JavaScript library to 5.3.3
- Updated `dayjs` JavaScript library to 1.11.1
- Updated `github-markdown-css` to 5.5.1
- Updated Pandoc to 3.2 in Dockerfile

### [24.3.0] - March 7, 2024
- Update pandoc to v3.1.12.2
- Update bootstrap js lib to v5.3.3
- Update github-markdown-css to v5.5.1

### [24.1.1] - January 16, 2024
- Update Pandoc reference template

### [24.1.0] - January 9, 2024
- Update `Dockerfile` to use Pandoc 3.1.11.1

### [23.12.1] - December 12, 2023
- Update `github-markdown-css` on CDNJS to version 5.5.0
- Update `update_cdnjs_links.py` to scan `jinjafx_server.py` for libraries to update
- Update copyright notices in preparation for 2024

### [23.12.0] - December 4, 2023
- Update `Dockerfile` to use Pandoc 3.1.9
- Update CodeMirror JavaScript library to 5.65.16

### [23.11.1] - November 17, 2023
- Add `-pandoc` command line option to explicitly enable support for converting HTML to DOCX using pandoc

### [23.11.0] - November 3, 2023
- Update JavaScript libraries to the latest versions
- Add support for the conversion from HTML/Markdown to DOCX via Pandoc
- Update GitHub Markdown CSS to 5.3.0

### [23.9.1] - September 27, 2023
- Fix deprecation of `datetime.datetime.utcnow()`

### [23.9.0] - September 21, 2023
- Enforce minimal Python version in code

### [23.8.3] - August 23, 2023
- Add support for keyless YAML via the `_` variable

### [23.8.2] - August 21, 2023
- Add `-weblog` feature to view logs from the browser
- Improve rate limiting algorithm and extend to `weblog` and `get_dt`
- Separate out thread locks for logging and rate limiting
- Improve logging by including HTTP version number and mask out a couple of messages unless verbose logging is enabled

### [23.8.1] - August 8, 2023
- Improve error reporting if an exception happens in `window.onload()`

### [23.8.0] - August 7, 2023
- Update JavaScript libraries to latest version

### [23.6.0] - June 6, 2023
- Drop support for Python 3.7
- Update JavaScript libraries to latest version

### [23.3.2] - March 20, 2023
- Added support for Unicode symbols within templates (including Emojis)
- Fixed an issue where downloads weren't working in some scenarios

### [23.3.1] - March 17, 2023
- Code cleanup - removed unused commented out code

### [23.3.0] - March 16, 2023
- Replaced CryptoJS with native Subtle Crypto for Ansible Vault encryption
- Removed dependency on utf8 library as we no longer allow non-ASCII templates
- Downloads are now handled in the browser and don't require a POST request
- Updated CodeMirror JavaScript library to 5.65.12

### [23.2.1] - February 22, 2023
- Updated content encoding within JSON requests and responses

### [23.2.0] - February 1, 2023
- Improvements around exception handling and logging

### [23.1.0] - December 31, 2022
- Add support for `global.yml` when using DataSets
- Remove support for Python 3.6 due to end of life
- Update Python build to use `pyproject.toml` to avoid deprecation
- Versioned links are updated automatically for cacheing
- Replace `func_timeout` as it is no longer being maintained
- Reduce HTTP threads from 16 to 4 to reduce memory usage
- Remove expansion icons from panes in favour of full screen mode
- Minor updates to JavaScript libraries

### [22.12.2] - December 14, 2022
- Update various JavaScript libraries to latest versions
- Update copyright year to 2023

### [22.12.1] - December 8, 2022
- Improve exception reporting when using a persistent logfile

### [22.11.4] - November 28, 2022
- Add support for GitHub integration via the GitHub API to allow GitHub to be used to store DataTemplates

### [22.11.2] - November 18, 2022
- Fix issue with `-logfile` due to error in regexp for removing ansi colours

### [22.11.1] - November 10, 2022
- Updated the colour palette to hopefully be more aesthetically pleasing
- Updated `update_cdnjs_links.py` so it will update all html files automatically with latest JavaScript libs
- Added `update_versioned_links.py` to create static content links based on sha256 as a `pre-commit` Git Hook
- Updated various JavaScript libraries to latest versions

### [22.11.0] - November 8, 2022
- Add support for command line option `-logfile` for persistent logging

### [22.10.1] - November 7, 2022
- Fix issue with zIndex of `template.j2`

### [22.10.0] - October 25, 2022
- Update Dockerfile to use Python 3.11
- Update JavaScript libraries to latest version
- Fixed code scanning alert #67

### [22.9.5] - September 26, 2022
- Add support for a `Save As` button on DataTemplate Export

### [22.9.4] - September 20, 2022
- Add support for an `Import DataTemplate` button

### [22.9.2] - September 9, 2022
- Add `jinjafx.html` to permanent cache

### [22.9.1] - September 7, 2022
- Moved js/css/png content to versioned urls to enable permanent cacheing

### [22.9.0] - September 7, 2022
- Updated `codemirror` to 5.65.8
- Updated `bootstrap` to 5.2.0
- Updated `dayjs` to 1.11.5

### [22.8.1] - August 19, 2022
- Added support for `-ml` command line argument to set the maximum memory usage

### [22.8.0] - August 19, 2022
- Added support for `-tl` command line argument to set the maximum execution time of a request
- Fixed an issue where text highlighting wasn't visible when showing where non-ASCII characters were detected in `data.csv`
- JinjaFx Server will now execute JinjaFx using the Jinja2 SandboxEnvironment
- POST requests will now display total duration in output logging

### [22.7.9] - July 21, 2022
- Various cosmetic changes associated with syntax highlighting

### [22.7.8] - July 11, 2022
- Revert all font related changes to pre 22.7.0 as they didn't really work
- Finalise `<output>` tag highlighting to colour ":html" and ":markdown" in red

### [22.7.7] - July 8, 2022
- Cosmetic changes to the CSV table within the `data.csv` pane
- Added support for highlighting `<output>` tags in `template.j2`

### [22.7.6] - July 7, 2022
- Fix syntax highlighting of `template.j2` that I broke with the previous release
- Add CDNJS link to `output.html` for "Fira Code"

### [22.7.4] - July 7, 2022
- Disable ligatures on everything except `template.j2`

### [22.7.3] - July 7, 2022
- Disable ligatures for Output window and print view

### [22.7.2] - July 7, 2022
- Add missing `content-security-policy` for `font-src`
- Update Output window and print view to use "Fira Code" font

### [22.7.1] - July 7, 2022
- Align font sizes across all panes

### [22.7.0] - July 7, 2022
- Change CodeMirror font to "Fira Code" and enable ligatures
- Add `update_cdnjs_links.py` script to automatically update CDNJS links

### [22.6.2] - June 21, 2022
- More cosmetic changes to information pane

### [22.6.1] - June 20, 2022
- Cosmetic changes to information pane

### [22.6.0] - June 14, 2022
- Fix CodeQL issue - exception text reinterpreted as HTML

### [22.5.9] - May 31, 2022
- Updates to display of `X-Forwarded-Proto` header

### [22.5.8] - May 31, 2022
- Display `X-Forwarded-Proto` header in logs

### [22.5.7] - May 31, 2022
- Add subresource integrity to external resources loaded from `cdnjs.com`

### [22.5.6] - May 29, 2022
- Increase width of info div to 40% from 35%

### [22.5.5] - May 18, 2022
- HTML tags `<pre>` and `<code>` in Markdown will now wrap

### [22.5.4] - May 17, 2022
- Add support for UTF-8 characters in `template.j2`
- Update various JavaScript libraries to the latest versions

### [22.5.3] - May 16, 2022
- Allow HTML tags in Markdown (matches GitHub behaviour)
- Render emojis in Markdown as per GitHub

### [22.5.2] - May 15, 2022
- Improve the rendering of Markdown and sort out issues with escaping of HTML tags in different scenarios
- Update the template information screen with cosmetic enhancements

### [22.5.1] - May 13, 2022
- Added support for specifying the render format of output blocks (supported formats are "text", "html" and "markdown")
- Where HTML content was auto-detected before, it now needs to be explicitly specified using `output:html` else it will be rendered as text
- Added support for a `Print` button which will print the current output in a printer friendly format
- Added a template information screen which disappears when you start editing a template
- Fixed an issue where `<span>` HTML tags weren't being closed in `index.html`
- Cosmetic updates to HTML output to use a white background

### [22.5.0] - May 6, 2022
- Set minimum version of `jinjafx` for Ansible Vault support

### [22.4.6] - Apr 30, 2022
- Handle Python 3.6 deprecation by dependencies by forcing lower versions of modules under Python 3.6

### [22.4.5] - Apr 20, 2022
- Fixed an issue where output downloads didn't correct mark HTML with a .html extension

### [22.4.4] - Apr 13, 2022
- Encrypt when enter is pressed on "String to Encrypt"

### [22.4.2] - Apr 12, 2022
- Add support for Ansible Vault encryption of strings with client-side JavaScript

### [22.4.1] - Apr 11, 2022
- Update Ansible Vault decryption routines to use `Vault().decrypt()`

### [22.4.0] - Apr 6, 2022
- Remove undocumented `-api` command line option
- Update logging so it only shows limited requests without `-v`

### [22.3.6] - Mar 23, 2022
- Update `dayjs` JavaScript library to 1.11.0
- Fix issue with href link on JinjaFx header

### [22.3.5] - Mar 21, 2022
- Remove `ansible-core` dependency as JinjaFx now provides a native method to decrypt Ansible Vault credentials

### [22.3.4] - Mar 3, 2022
- Remove support for importing Ansible filters from Ansible as JinjaFx now provides some of them as a custom extension

### [22.3.3] - Mar 2, 2022
- Fix dependency issue

### [22.3.2] - Mar 2, 2022
- Update Lambda to support GZIP compression

### [22.3.1] - Feb 28, 2022
- Added support for JinjaFx to be used as an AWS Lambda (FaaS)
- Fixed an issue with logging

### [22.2.2] - Feb 25, 2022
- Updated link format for DataTemplates to use `/dt/`

### [22.2.1] - Feb 8, 2022
- The `data` and `template` variables are now passed as type `str` to `JinjaFx().jinjafx()`
- Update JinjaFx Server with latest JavaScript libraries

### [22.1.7] - Jan 21, 2022
- Move the custom extensions into JinjaFx core

### [22.1.6] - Jan 20, 2022
- Update JinjaFx Server using the new JinjaFx method for searching for extensions

### [22.1.5] - Jan 19, 2022
- Added support for custom filter `cisco7encode`
- Added support for custom filter `junos9encode`

### [22.1.4] - Jan 19, 2022
- Added support for custom filter `junos_snmpv3_key`

### [22.1.3] - Jan 18, 2022
- Fix CodeQL Security Alerts

### [22.1.2] - Jan 17, 2022
- Add custom JinjaFx Extensions in `/extensions`

### [21.12.3] - Dec 12, 2021
- Detect and highlight non-ascii characters
- Check `Content-Length` isn't too large on POST requests

### [21.12.2] - Dec 10, 2021
- Add support for detecting non-ascii characters in `template.j2`
- Increase maximum POST request length from 512KB to 2MB

### [21.12.1] - Dec 3, 2021
- Make JinjaFx Server available as a PyPi module

### 21.11.0 - Nov 29, 2021
- Initial release

[24.6.0]: https://github.com/cmason3/jinjafx_server/compare/24.5.0...24.6.0
[24.5.0]: https://github.com/cmason3/jinjafx_server/compare/24.3.0...24.5.0
[24.3.0]: https://github.com/cmason3/jinjafx_server/compare/24.1.1...24.3.0
[24.1.1]: https://github.com/cmason3/jinjafx_server/compare/24.1.0...24.1.1
[24.1.0]: https://github.com/cmason3/jinjafx_server/compare/23.12.1...24.1.0
[23.12.1]: https://github.com/cmason3/jinjafx_server/compare/23.12.0...23.12.1
[23.12.0]: https://github.com/cmason3/jinjafx_server/compare/23.11.1...23.12.0
[23.11.1]: https://github.com/cmason3/jinjafx_server/compare/23.11.0...23.11.1
[23.11.0]: https://github.com/cmason3/jinjafx_server/compare/23.9.1...23.11.0
[23.9.1]: https://github.com/cmason3/jinjafx_server/compare/23.9.0...23.9.1
[23.9.0]: https://github.com/cmason3/jinjafx_server/compare/23.8.3...23.9.0
[23.8.3]: https://github.com/cmason3/jinjafx_server/compare/23.8.2...23.8.3
[23.8.2]: https://github.com/cmason3/jinjafx_server/compare/23.8.1...23.8.2
[23.8.1]: https://github.com/cmason3/jinjafx_server/compare/23.8.0...23.8.1
[23.8.0]: https://github.com/cmason3/jinjafx_server/compare/23.6.0...23.8.0
[23.6.0]: https://github.com/cmason3/jinjafx_server/compare/23.3.2...23.6.0
[23.3.2]: https://github.com/cmason3/jinjafx_server/compare/23.3.1...23.3.2
[23.3.1]: https://github.com/cmason3/jinjafx_server/compare/23.3.0...23.3.1
[23.3.0]: https://github.com/cmason3/jinjafx_server/compare/23.2.1...23.3.0
[23.2.1]: https://github.com/cmason3/jinjafx_server/compare/23.2.0...23.2.1
[23.2.0]: https://github.com/cmason3/jinjafx_server/compare/23.1.0...23.2.0
[23.1.0]: https://github.com/cmason3/jinjafx_server/compare/22.12.2...23.1.0
[22.12.2]: https://github.com/cmason3/jinjafx_server/compare/22.12.1...22.12.2
[22.12.1]: https://github.com/cmason3/jinjafx_server/compare/22.11.4...22.12.1
[22.11.4]: https://github.com/cmason3/jinjafx_server/compare/22.11.2...22.11.4
[22.11.2]: https://github.com/cmason3/jinjafx_server/compare/22.11.1...22.11.2
[22.11.1]: https://github.com/cmason3/jinjafx_server/compare/22.11.0...22.11.1
[22.11.0]: https://github.com/cmason3/jinjafx_server/compare/22.10.1...22.11.0
[22.10.1]: https://github.com/cmason3/jinjafx_server/compare/22.10.0...22.10.1
[22.10.0]: https://github.com/cmason3/jinjafx_server/compare/22.9.5...22.10.0
[22.9.5]: https://github.com/cmason3/jinjafx_server/compare/22.9.4...22.9.5
[22.9.4]: https://github.com/cmason3/jinjafx_server/compare/22.9.2...22.9.4
[22.9.2]: https://github.com/cmason3/jinjafx_server/compare/22.9.1...22.9.2
[22.9.1]: https://github.com/cmason3/jinjafx_server/compare/22.9.0...22.9.1
[22.9.0]: https://github.com/cmason3/jinjafx_server/compare/22.8.1...22.9.0
[22.8.1]: https://github.com/cmason3/jinjafx_server/compare/22.8.0...22.8.1
[22.8.0]: https://github.com/cmason3/jinjafx_server/compare/22.7.9...22.8.0
[22.7.9]: https://github.com/cmason3/jinjafx_server/compare/22.7.8...22.7.9
[22.7.8]: https://github.com/cmason3/jinjafx_server/compare/22.7.7...22.7.8
[22.7.7]: https://github.com/cmason3/jinjafx_server/compare/22.7.6...22.7.7
[22.7.6]: https://github.com/cmason3/jinjafx_server/compare/22.7.4...22.7.6
[22.7.4]: https://github.com/cmason3/jinjafx_server/compare/22.7.3...22.7.4
[22.7.3]: https://github.com/cmason3/jinjafx_server/compare/22.7.2...22.7.3
[22.7.2]: https://github.com/cmason3/jinjafx_server/compare/22.7.1...22.7.2
[22.7.1]: https://github.com/cmason3/jinjafx_server/compare/22.7.0...22.7.1
[22.7.0]: https://github.com/cmason3/jinjafx_server/compare/22.6.2...22.7.0
[22.6.2]: https://github.com/cmason3/jinjafx_server/compare/22.6.1...22.6.2
[22.6.1]: https://github.com/cmason3/jinjafx_server/compare/22.6.0...22.6.1
[22.6.0]: https://github.com/cmason3/jinjafx_server/compare/22.5.9...22.6.0
[22.5.9]: https://github.com/cmason3/jinjafx_server/compare/22.5.8...22.5.9
[22.5.8]: https://github.com/cmason3/jinjafx_server/compare/22.5.7...22.5.8
[22.5.7]: https://github.com/cmason3/jinjafx_server/compare/22.5.6...22.5.7
[22.5.6]: https://github.com/cmason3/jinjafx_server/compare/22.5.5...22.5.6
[22.5.5]: https://github.com/cmason3/jinjafx_server/compare/22.5.4...22.5.5
[22.5.4]: https://github.com/cmason3/jinjafx_server/compare/22.5.3...22.5.4
[22.5.3]: https://github.com/cmason3/jinjafx_server/compare/22.5.2...22.5.3
[22.5.2]: https://github.com/cmason3/jinjafx_server/compare/22.5.1...22.5.2
[22.5.1]: https://github.com/cmason3/jinjafx_server/compare/22.5.0...22.5.1
[22.5.0]: https://github.com/cmason3/jinjafx_server/compare/22.4.6...22.5.0
[22.4.6]: https://github.com/cmason3/jinjafx_server/compare/22.4.5...22.4.6
[22.4.5]: https://github.com/cmason3/jinjafx_server/compare/22.4.4...22.4.5
[22.4.4]: https://github.com/cmason3/jinjafx_server/compare/22.4.2...22.4.4
[22.4.2]: https://github.com/cmason3/jinjafx_server/compare/22.4.1...22.4.2
[22.4.1]: https://github.com/cmason3/jinjafx_server/compare/22.4.0...22.4.1
[22.4.0]: https://github.com/cmason3/jinjafx_server/compare/22.3.6...22.4.0
[22.3.6]: https://github.com/cmason3/jinjafx_server/compare/22.3.5...22.3.6
[22.3.5]: https://github.com/cmason3/jinjafx_server/compare/22.3.4...22.3.5
[22.3.4]: https://github.com/cmason3/jinjafx_server/compare/22.3.3...22.3.4
[22.3.3]: https://github.com/cmason3/jinjafx_server/compare/22.3.2...22.3.3
[22.3.2]: https://github.com/cmason3/jinjafx_server/compare/22.3.1...22.3.2
[22.3.1]: https://github.com/cmason3/jinjafx_server/compare/22.2.2...22.3.1
[22.2.2]: https://github.com/cmason3/jinjafx_server/compare/22.2.1...22.2.2
[22.2.1]: https://github.com/cmason3/jinjafx_server/compare/22.1.7...22.2.1
[22.1.7]: https://github.com/cmason3/jinjafx_server/compare/22.1.6...22.1.7
[22.1.6]: https://github.com/cmason3/jinjafx_server/compare/22.1.5...22.1.6
[22.1.5]: https://github.com/cmason3/jinjafx_server/compare/22.1.4...22.1.5
[22.1.4]: https://github.com/cmason3/jinjafx_server/compare/22.1.3...22.1.4
[22.1.3]: https://github.com/cmason3/jinjafx_server/compare/22.1.2...22.1.3
[22.1.2]: https://github.com/cmason3/jinjafx_server/compare/21.12.3...22.1.2
[21.12.3]: https://github.com/cmason3/jinjafx_server/compare/21.12.2...21.12.3
[21.12.2]: https://github.com/cmason3/jinjafx_server/compare/21.12.1...21.12.2
[21.12.1]: https://github.com/cmason3/jinjafx_server/compare/21.11.0...21.12.1
