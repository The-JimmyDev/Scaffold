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
This template will:
    - Modify package name in package.json
    - Run npm install
    - Run npm update (prompted)
> Docker is available
> Running instructions safely.
> Spinning up sandbox environment (nikolaik/python-nodejs:latest)...
------- "my-project" Created successfully -------
```

---

## Why

Every Next.js project starts the same way. Run `create-next-app`, delete half of what it generates, recreate the same folder structure, install the same packages. Every time.

This fixes that. One command, your templates, ready to go.

---

## Structure

```
Scaffold/
├── scaffold.py
└── Templates/
    └── next-base/
        ├── public/
        ├── src/
        ...
        ├── instructions.py   ← template-specific setup, never copied (optional)
        └── scaffold.json     ← template manifest, never copied
```

`instructions.py` and `scaffold.json` are internal to each template and are never copied into your project.

---

## Usage

```bash
# List available templates
python scaffold.py
# OR
python scaffold.py -l

# Scaffold a project
python scaffold.py -t <template> <name>

# Skip all prompts, confirm everything automatically
python scaffold.py -t <template> <name> -y

# Run instructions unsafely (no Docker sandbox)
python scaffold.py -t <template> <name> -us
```

### Flags

| Flag | Description |
|------|-------------|
| `name` | Project name. Prompted if not provided. |
| `-l`, `--list` | List available templates. |
| `-t`, `--template` | Template to use. |
| `-y`, `--yes` | Skip all prompts and confirm everything safe automatically.|
| `-us`, `--unsafe` | Run `instructions.py` outside of Docker. Only use with templates you trust! |

---

## Safety

When Docker is available, `instructions.py` runs inside a container — your system stays untouched. When Docker isn't found, Scaffold warns you and asks you to explicitly type `proceed` before running anything. The `--unsafe` flag skips that prompt; only use it with templates you wrote or trust.

---

## Adding a Template

1. Create a folder under `Templates/` with your template name.
2. Add a `scaffold.json` manifest (required).
3. Optionally add an `instructions.py` for post-copy setup logic.
4. Put your actual template files in the folder.

### scaffold.json

```json
{
  "name": "next-base",
  "description": "Next.js template using Tailwind, JS, ESLint, and src/ directory.",
  "actions": [
    "Modifies package.json",
    "Runs npm install"
  ],
  "docker": {
    "image": "nikolaik/python-nodejs:latest"
  },
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
| `actions` | No | What `instructions.py` will do, shown to the user before execution. |
| `docker.image` | No | Docker image to use for safe execution. Defaults to `python:3-slim`. |
| `dependencies.system` | No | System binaries required (checked via `which`). |
| `dependencies.python` | No | Python packages required (checked via import name, e.g. `PIL` not `pillow`). |

Dependencies are checked before anything is copied. If something is missing, Scaffold exits early and tells you what's needed.

### instructions.py

Optional. Runs after the template is copied. Receives these globals automatically:

```python
project_name  # str  — the name entered by the user
project_path  # str  — path to the newly created project directory
yes           # bool — True if -y flag was passed
```

When running safely via Docker, `project_path` maps to `/workspace` inside the container and `instructions.py` is mounted at `/scripts/instructions.py`. Any files you write to `project_path` will appear in the real output directory on the host.

---

## Dependencies

- Python 3.x
- [`rich`](https://github.com/Textualize/rich) — `pip install rich`
- Docker (optional, but recommended — enables safe sandboxed execution)

Everything else is standard library.

---

## Notes

- Run Scaffold from any directory — template paths are always resolved relative to `scaffold.py` itself.
- If a folder with the chosen name already exists, the project is created as `<name>-YYYYMMDD-HHMMSS` instead.
- Works on Windows and Linux.