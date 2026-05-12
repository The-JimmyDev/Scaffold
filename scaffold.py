import os
import shutil
import rich
import argparse
import runpy
import sys
import json
from datetime import datetime
import importlib.util
import subprocess
import re


def main():
    parser = argparse.ArgumentParser(description="Simple scalable scaffolder that creates and executes setups of predefined templates from its Templates/ directory.")
    parser.add_argument("name", nargs="?", help="Project name. Prompted if not provided.")
    parser.add_argument("-t", "--template", help="Selects template to use.")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip all prompts and confirm everything safe automatically. (Doesn't run instructions unsafely!)")
    parser.add_argument("-l", "--list", action="store_true", help="Lists available templates.")
    parser.add_argument("-us", "--unsafe", action="store_true", help="Runs instructions unsafely. (only do this with templates you trust!)")
    args = parser.parse_args()
    template_dir = f"{os.path.dirname(os.path.abspath(__file__))}/Templates/"
    
    if args.list or args.template is None:
        list_templates(template_dir=template_dir)
        sys.exit(0)
    
    template_path = os.path.join(template_dir, args.template)
    
    if not os.path.isdir(template_path):
        rich.print(f"[red]Template '{args.template}' not found.[/red]")
        sys.exit(1)
    
    project_name = validate_project_name(project_name=args.name if args.name else "")
    
    manifest = load_selected_manifest(template_path=template_path)
    list_actions(manifest=manifest)
    

        
    sou  = template_path #SOUrce
    des = resolve_des(project_name=project_name) #DEStination
    
    check_dependencies(manifest=manifest)
    copy_template(des=des, sou=sou, project_name=project_name)
    if not os.path.exists(f"{template_path}/instructions.py"):
        rich.print(f"[gold1]Template is missing instructions.py.[/gold1]")
        sys.exit(0)
    elif args.unsafe:
        run_instructions(template_path=template_path, des=des, project_name=project_name, unsafe=args.unsafe, yes=args.yes)
    elif check_docker():
        rich.print("> [bright_green]Docker is available[/bright_green]")
        rich.print("> [light_sky_blue1]Running instructions safely.[/light_sky_blue1]")
        run_safely(template_path=template_path, des=des, project_name=project_name, yes=args.yes, manifest=manifest)
    else:
        run_instructions(template_path=template_path, des=des, project_name=project_name, unsafe=args.unsafe, yes=args.yes)


def validate_project_name(project_name):
    while not re.match(r"^[A-Za-z0-9_-]+$", project_name):
        if project_name != "":
            rich.print("[red]Invalid name. Use only letters, numbers, dashes, or underscores.[/red]")
        rich.print("[gold1]Project name > [/gold1]", end="")
        project_name = input("").strip()
    return project_name   


def abort(msg, des):
    rich.print(f"[red]{msg}[/red]")
    if os.path.isdir(des):
        rich.print("[red]Reverting changes[/red]")
        shutil.rmtree(des)
    sys.exit(1)
    
    
def list_templates(template_dir):
    
    rich.print("> [light_sky_blue1]Use the -t or --template flag to select a template.[/light_sky_blue1]")
    rich.print("Available templates:")
    
    for templ in os.scandir(template_dir):
        if templ.is_dir() and os.path.exists(f"{templ.path}/scaffold.json"):
            with open(f"{templ.path}/scaffold.json") as f:
                try:
                    manifest = json.load(f)
                    rich.print(f"    - [gold1]{manifest['name']}[/gold1]: {manifest['description']}")
                    
                except json.JSONDecodeError:
                    rich.print(f"    - [gold1]{templ.name}[/gold1] : [red]Invalid scaffold.json[/red]")
                    
    
def list_actions(manifest):
    if manifest.get("actions"):
        rich.print("> [light_sky_blue1]This template will:[/light_sky_blue1]")
        for action in manifest["actions"]:
            rich.print(f"    [grey50]-[/grey50] {action}")
            
            
def load_selected_manifest(template_path):
    try:
        with open(os.path.join(template_path, "scaffold.json")) as f:
            return json.load(f)
    except json.JSONDecodeError:
        rich.print("[red]Invalid scaffold.json[/red]")
        sys.exit(1)
    except FileNotFoundError:
        rich.print("[red]Missing scaffold.json[/red]")
        sys.exit(1)
    
    
def resolve_des(project_name):
    des = f"./{project_name}"
    if not os.path.isdir(des):
        return des
    return f"{des}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def copy_template(sou, des, project_name):
    try:
        shutil.copytree(src=sou, dst=des, ignore=shutil.ignore_patterns("instructions.py", "scaffold.json"))
    except Exception as e:
        abort(msg=f"Something went wrong: {e}", des=des)
    
    rich.print(f'[grey50]-------[/grey50] [green1]"{project_name}" Created successfully[/green1] [grey50]-------[/grey50]')


def run_instructions(template_path, des, project_name, unsafe, yes):
        
    rich.print("> [[red]WARNING[/red]]: [red]DOCKER NOT FOUND[/red]")
    rich.print("> [[red]WARNING[/red]]: [red]Instructions will be ran unsafely, only do this if you trust this template![/red]")
    
    if not unsafe:
        rich.print("[red]To continue, type 'proceed' [/red]> ", end="")
        
    if unsafe or input("").lower() == "proceed":
        try:
            runpy.run_path(f"{template_path}/instructions.py", init_globals={
                "project_path": des,
                "project_name": project_name,
                "yes": yes
            })
        except Exception as e:
            abort(msg=f"Something went wrong: {e}", des=des)
            
    else:
        rich.print("> [light_sky_blue1]Instructions not executed. Copying complete.[/light_sky_blue1]")
        sys.exit(1)


def check_dependencies(manifest):
    system_deps = manifest.get("dependencies", {}).get("system", [])
    python_deps = manifest.get("dependencies", {}).get("python", [])
    
    missing_system = [dep for dep in system_deps if not shutil.which(dep)]
    missing_python = [dep for dep in python_deps if not importlib.util.find_spec(dep)]
    
    for dep in missing_system:
        rich.print(f"[red]Missing system dependency: {dep}[/red]")
    for dep in missing_python:
        rich.print(f"[red]Missing python dependency: {dep}[/red]")
        
    if missing_system or missing_python:
        sys.exit(1)

def check_docker():
    return shutil.which("docker") is not None

def run_safely(template_path, des, project_name, yes, manifest):
    script_path = os.path.abspath(f"{template_path}/instructions.py")

    abs_des = os.path.abspath(des).replace('\\', '/')
    abs_script = script_path.replace('\\', '/')

    docker_image = manifest.get("docker", {}).get("image", "python:3-slim")

    python_deps = manifest.get("dependencies", {}).get("python", [])
    
    pip_setup = ""
    if python_deps:
        deps_string = " ".join(python_deps)
        pip_setup = f"pip install {deps_string} --quiet && "

    runpy_cmd = (
        f"import runpy; "
        f"runpy.run_path('/scripts/instructions.py', init_globals={{"
        f"'project_path': '/workspace', "
        f"'project_name': '{project_name}', "
        f"'yes': {yes}"
        f"}})"
    )

    cmd = [
        "docker", "run", "--rm", "-it",
        "-v", f"{abs_des}:/workspace",
        "-v", f"{abs_script}:/scripts/instructions.py",
        "-w", "/workspace",
        docker_image, "sh", "-c", f"{pip_setup}python3 -c \"{runpy_cmd}\""
    ]

    try:
        rich.print(f"> [grey50]Spinning up sandbox environment ({docker_image})...[/grey50]")
        if python_deps:
            rich.print("> [grey50]Installing template dependencies inside container...[/grey50]")
            
        subprocess.run(cmd, check=True)
        rich.print("> [light_sky_blue1]Instructions executed safely inside Docker.[/light_sky_blue1]")
    except subprocess.CalledProcessError as e:
        abort(msg=f"Docker execution failed with exit code: {e.returncode}", des=des)
    except Exception as e:
        abort(msg=f"Something went wrong while running Docker: {e}", des=des)
        
        
if __name__ == '__main__':
    main()