# Scaffold

A fast, opinionated project scaffolder.

```
> python scaffold.py
No template selected. Use the -t or --template flag to select.
Available templates:
    - next-base: Next.js template using Tailwind, JS, ESLint, and src/ directory.
    - blank: A blank template. Add your own files and configure instructions.py to your needs.
    ...

> python scaffold.py -t next-base my-project
> This template will:
    - Modify package name in package.json
    - Run npm install
    - Run npm update (prompted)
> WARNING: instructions.py will now execute. Only proceed if you trust this template.
Continue? (y/N) > y
------- "my-project" Created successfully -------
> Modifying package name in package.json
------- Modification successful -------
> Running npm install
------- Installation successful -------
Run npm update? (y/N) > y
> Running npm install
------- Update successful -------
```

---

## Why

For me specifically, every Next.js project starts the same way. Run `create-next-app`, delete half of what it generates, recreate the same folder structure, install the same packages. Every time. 20 minutes of my life wasted.

This fixes that. One command, your templates, ready to go.

---

## Structure

```
Scaffold/
├── scaffold.py          ← the script
└── Templates/
    └── next-base/
        ├── public/
        ├── src/
        ...
        ├── instructions.py  ← template-specific setup, not copied (optional)
        └── scaffold.json    ← template manifest, not copied
```

`instructions.py` and `scaffold.json` are internal to each template and are never copied into your project.

---

## Usage

```bash
# See all options and description
python scaffold.py -h

# List available templates
python scaffold.py
# OR
python scaffold.py -l

# Scaffold a project
python scaffold.py -t <template> <name>

# Skip all prompts, confirm everything automatically
python scaffold.py -t <template> <name> -y
```

### Flags

| Flag | Description |
|------|-------------|
| `name` | Project name. Prompted if not provided. |
| `-l`, `--list` | Lists templates. |
| `-t`, `--template` | Template to use. |
| `-y`, `--yes` | Skip all prompts and confirm everything automatically. |

---

## Adding a Template

1. Create a folder under `Templates/` with your template name.
2. Add a `scaffold.json` manifest (see below).
3. Optionally add an `instructions.py` for setup logic.
4. Put your actual template files in there.

### scaffold.json

Every template requires a `scaffold.json` manifest:

```json
{
  "name": "next-base",
  "description": "Next.js template using Tailwind, JS, ESLint, and src/ directory.",
  "actions": [
    "Modifies package.json",
    "Runs npm install"
  ],
  "dependencies": {
    "system": ["node", "npm"],
    "python": []
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name shown when listing templates. |
| `description` | Yes | One-line description shown when listing templates. |
| `actions` | No | List of things `instructions.py` will do, shown to the user before execution. |
| `dependencies.system` | No | System binaries required (checked via `which`). |
| `dependencies.python` | No | Python packages required (checked via import name, e.g. `PIL` not `pillow`). |

Scaffold checks all dependencies before copying anything. If something is missing it exits early and tells you what's needed.

### instructions.py

Optional. If present, runs after the template is copied. Receives these variables automatically:

```python
project_name  # the name entered by the user
project_path  # path to the newly created project
yes           # bool, True if -y flag was passed
```

The user is warned and prompted before `instructions.py` executes. `-y` skips the prompt.

---

## Dependencies

- Python 3.x
- [`rich`](https://github.com/Textualize/rich) — `pip install rich`

Everything else is standard library.

---

## Notes

- Running from a different directory is preferred — the script always resolves template paths relative to itself.
- If a folder with the project name already exists, the project is scaffolded as `<name>-YYYYMD-HMS` instead.
- Works on Windows and Linux.
