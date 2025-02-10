# Obsidian-HTML
This is to convert obsidian markdown to HTML.

## Follow these steps to properly convert your obsidian HTML to markdown. 

1. Create a `config.py` file with the template: 

```Python 
    FILE_PATH = "File path of obsidian vault"
    EXPORT_PATH = "File path you plan to export html files to"
```

2. After you have successuly created the file make sure you have the following statement at the top of `main.py` 

```Python 
    import os 
```

3. You should be able to run the `main.py` file and all the HTML files will be outputted to the directory specified 

## Work in progress

For the most part the linking between different files, and images from obsidian's markdown to HTML works, the work in progress will be adding room for the blockqoutes and converting those to HTML. 