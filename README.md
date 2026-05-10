# scaffold

A fast, opinionated project scaffolder.

```
> python scaffold.py
No template selected. Use the -t or --template flag to select.
Available templates:
    - next-base : Next.js template using Tailwind, JS, ESLint, and src/ directory.
    - blank : A blank template. Add your own files and configure instructions.py to your needs.
    ...

> python scaffold.py -t next-base my-project
------- "my-project" Created successfully -------
> Running provided instructions now
> Modifying package name in package.json
------- Modification successful -------
> Running npm install
------- Installation successful -------
```

---

## Why

For me specifically, every Next.js project starts the same way. Run `create-next-app`, delete half of what it generates, recreate the same folder structure, fix `package.json`, install the same packages. Every time. 20 minutes of my life wasted.

This fixes that. One command, your template, ready to go.

---

## Structure

```
Scaffold/
├── scaffold.py          ← the script
└── Templates/
    └── next-base/
        ├── public/
        ├── src/
        ├── .env.local
        ├── .gitignore
        ├── jsconfig.json
        ├── next.config.mjs
        ├── postcss.config.mjs
        ├── eslint.config.mjs
        ├── package.json
        ├── instructions.py  ← template-specific setup, not copied
        └── scaffold.txt     ← template description, not copied
```

`instructions.py` and `scaffold.txt` are internal to each template and are never copied into your project.

---

## Usage

```bash
# See all options and description
python scaffoly.py -h

# List available templates
python scaffold.py
# OR
python scaffold.py -t

# Scaffold a project
python scaffold.py -t <template> <name>

# Skip all prompts, confirm everything automatically
python scaffold.py -t <template> <name> -y
```

### Flags

| Flag | Description |
|------|-------------|
| `name` | Project name. Prompted if not provided. |
| `-t`, `--template` | Template to use. Omit to list available templates. |
| `-y`, `--yes` | Skip all prompts and confirm everything automatically. |

---

## Adding a Template

1. Create a folder under `Templates/` with your template name.
2. Add a `scaffold.txt` with a short one-line description.
3. Add an `instructions.py` that handles setup (installs, replacements, whatever the template needs).
4. Put your actual template files in there.

The core script doesn't care what framework, language, or structure your template uses. All the setup logic lives in `instructions.py` and receives these variables automatically:

```python
project_name  # the name entered by the user
project_path  # absolute path to the newly created project
yes           # bool, True if -y flag was passed
```

---

## Dependencies

- Python 3.x
- [`rich`](https://github.com/Textualize/rich) — `pip install rich`

Everything else is standard library.

---

## Notes

- Running from a different directory is preferred — the script always resolves template paths relative to itself.
- If a folder with the project name already exists, the project is scaffolded as `<name>-scaffold` instead.
- Works on Windows and Linux.
