# Archiving the hunt
We need to generate an entirely static version of the hunt for the [MIT Mystery Hunt archive](https://puzzles.mit.edu/huntsbyyear.html). This doc details how we generated that and things to be careful of.

 1. Ensure every puzzle has a static version that doesn't require a backend server, your podcast to remain available, etc. These are called "posthunt" versions. [See `USE_POSTHUNT_ON_HUNT_COMPLETE`](/hunt/app/core/constants.py) for the puzzles that we posthunted, and you can check the relevant puzzle bundles for how we implemented the posthunt version. Some tactics:
     - Transcribe external resources such as podcast episodes.
     - Make stub versions of puzzles that require external APIs such as our crow facts puzzle that required a texting bot.
     - Stub out calls to the backend server and write a JS version. We did this by checking a `posthunt_enabled` Django variable, so that the server can still be run using the original version of the puzzle.

 1. Download any external fonts you're using. We set up the `archivable_font` helper in [`hunt/app/templatetags/archive.py`](/hunt/app/templatetags/archive.py) to swap them out automatically. I downloaded all fonts from Google Fonts, and added files with the appropriate `@font-face` declarations in [`hunt/app/static/fonts`](/hunt/app/static/fonts).

 1. Download any other external assets you're using, such as solution files hosted on external websites.

 1. (optional) Simplify the pages before scraping. For example, we hid login pages and prevented CSRF tokens being output for a repeatable scrape result.

 1. (optional) Remove any cache breaking parameters like `?v=1`.

 1. Build and collect puzzle files using the special `archive` environment.
    ```
    DJANGO_ENV=archive npm run build
    DJANGO_ENV=archive python manage.py collectpuzzlefiles
    ```

 1. Run the server using the special `archive` environment. This sets up the site to be archived, and removes certain behaviors like needing to log in, so that the hunt website can be cleanly scraped. It will be available at <http://127.0.0.1:8000/>.
    ```
    DJANGO_ENV=archive python manage.py runserver
    ```

 1. Find all files that are asynchronously loaded, and add a link to them to the `archive-pages/` page.
     - These include:
        - Files loaded by ES6 imports: chunks, some libraries, some files in puzzle bundles.
        - Assets loaded asynchronously by libraries (such as lightbox images).
        - Assets loaded asyncronously by puzzles. You can find these by searching for uses of `puzzleStaticDirectory` and `puzzlePosthuntStaticDirectory`.
        - Extra pages within puzzles or rounds that aren't linked directly, and so the solver needs to find.
        - Extra assets used within puzzles or rounds after the puzzle is solved.
     - The archive pages is a stub page used to provide extra links to our scraping program.
     - **Note**: The "chunks" section is manually curated and may need to be updated regularly. As an alternative, the build script could be updated to disable chunking in the archived version.

 1. Scrape the website using [HTTrack](https://www.httrack.com/). It works really well except for not supporting ES6 imports. Our final configuration was:
     - Pages to scan.
        - <http://127.0.0.1:8000/>
        - <http://127.0.0.1:8000/archive-pages/>
     - Scan rules.
        ```
        +*.png +*.svg +*.gif +*.jpg +*.jpeg +*.css +*.js
        --disable-security-limits
        --utf8-conversion
        -*[file]wikimedia.org/*
        -*[file]ftw.usatoday.com/*
        -*[file]i.kinja-img.com/*
        -*[file]i.pinimg.com/*
        -*[file]i0.wp.com/*
        -*[file]mitadmissions.org/*
        -*[file]public.flourish.studio/*
        -*[file]unnamedtemporarysportsblog.com/*
        ```
      - > **Note**: I tried wget with the following command `wget --recursive --level inf --convert-links --page-requisites http://127.0.0.1:8000/ http://127.0.0.1:8000/archive-pages/`, and ran into several issues:
        >   - wget 1.11 doesn't support CSS URLs, so I needed an [unofficial build on Windows](https://opensourcepack.blogspot.com/2010/05/wget-112-for-windows.html)
        >   - Later versions needed extra flags like `-x` and `-H` or it wouldn't fetch everything properly.
        >   - It didn't seem to handle ES6 imports.
        >
        > In the end, using HTTrack was just easier to get mostly working.

 1. An issue with HTTrack is it doesn't rewrite ES6 imports. Most of them are handled by rewriting assets in archive mode </hunt/app/views/asset_views.py> to use chunks properly. However, we also need to handle ES6 imports within puzzles. You can run the following PowerShell script to fix these.
       ```
       Get-ChildItem -r -include "*.html" |
       ForEach-Object {
         $path = $_.FullName;
         ( Get-Content $path ) |
         ForEach-Object {
           $_ -replace '([''"])/static/lib/', '$1../../static/lib/'
         } |
         Set-Content $path
       }
      ```

 1. The other issue with HTTrack is it changes links from directories by suffixing `index.html`. This is mostly harmless, but it breaks some puzzles that use variables to dynamically build paths. For example, `puzzleStaticDirectory` is changed from `s__puzzle/` to `s__puzzle/index.html`. You can run the following PowerShell script to remove `index.html` relative links that end in `/index.html` in all HTML files.
      ```
       Get-ChildItem -r -include "*.html" |
       ForEach-Object {
         $path = $_.FullName;
         ( Get-Content $path ) |
         ForEach-Object {
           $_ -replace '([''"])((?!http).*/)index.html\1', '$1$2$1' -replace '([''"])index.html\1', '$1$1'
         } |
         Set-Content $path
       }
      ```

 1. Check the scraped site works as expected. Run a local server to try test it out.
    ```
    cd 127.0.0.1_8000
    python -m http.server 8001
    ```

 1. Hand the `127.0.0.1_8000` folder to the Puzzle Club webmaster.

> **Note**: HTTrack has issues with unicode path names and will make some unnecessary folders for them. Feel free to delete them.

> **Note**: HTTrack will try to access the puzzle static directory root page, and return an error. Errors for `/puzzle/.../s__puzzle` and `/puzzle/.../s__posthunt` can be ignored.

> **Tip**: For HTTrack, use the following settings:
>  - Disable pages for errors in `Build`.
>  - Increase number of connections in `Flow Control` to 99.
>  - Remove bandwidth limit (on the `Limits` tab) and include `--disable-security-limits` to let it proceed at full-speed.
>  - Remove footer in `Browser ID`.
