# Editor setup

I find it helpful to ignore certain files in my editor to avoid them showing up in search results, etc.

## Sublime Text
My [Sublime Text](https://www.sublimetext.com/) [project](https://www.sublimetext.com/docs/projects.html) settings are:
```
{
    "folders":
    [
        {
            "path": "path/to/hunt",
            "folder_exclude_patterns": [
                "__pycache__",
                "*.egg-info",
                "//2022-hunt/env/",
                "//2022-hunt/node_modules/",
                "//2022-hunt/static/",
                "//2022-hunt/static_temp/",
                "//2022-hunt/hunt/data/templates/round_files",
                "//2022-hunt/hunt/data/templates/puzzle_files",
            ],
            "binary_file_patterns": [
                "//2022-hunt/hunt/app/static/lib/",
                "*.min.js",
                "*.wav",
                "*.mp3",
                "*.pdf",
            ]
        }
    ]
}
```
