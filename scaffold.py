import os
import shutil
import rich
import argparse
import runpy
import sys
import json
from datetime import datetime
import importlib.util


def main():
    parser = argparse.ArgumentParser(description="Simple scalable scaffolder that creates and executes setups of predefined templates from its Templates/ directory.")
    parser.add_argument("name", nargs="?", help="Project name. Prompted if not provided.")
    parser.add_argument("-t", "--template", help="Template to use. Run with -t alone to list available templates.")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip all prompts and confirm everything automatically.")
    args = parser.parse_args()
    template_dir = f"{os.path.dirname(os.path.abspath(__file__))}/Templates/"
    
    if args.template is None:
        list_templates(template_dir=template_dir)
        sys.exit(0)
    
    template_path = os.path.join(template_dir, args.template)
    
    if not os.path.isdir(template_path):
        rich.print(f"[red]Template '{args.template}' not found.[/red]")
        sys.exit(1)
    
    manifest = load_selected_manifest(template_path=template_path)
    list_actions(manifest=manifest)
    
    if args.name:
        project_name = args.name
    else:
        rich.print("[gold1]Project name > [/gold1]", end="")
        project_name: str = input("")
        
    sou  = template_path #SOUrce
    des = resolve_des(project_name=project_name) #DEStination
    
    check_dependencies(manifest=manifest)
    copy_template(des=des, sou=sou, project_name=project_name)
    run_instructions(template_path=template_path, des=des, project_name=project_name, yes=args.yes)


def abort(msg, des):
    rich.print(f"[red]{msg}[/red]")
    if os.path.isdir(des):
        rich.print("[red]Reverting changes[/red]")
        shutil.rmtree(des)
    sys.exit(1)
    
    
def list_templates(template_dir):
    
    rich.print("> [light_sky_blue1]No template selected. Use the -t or --template flag to select.[/light_sky_blue1]")
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
        with open(f"{template_path}/scaffold.json") as f:
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


def run_instructions(template_path, des, project_name, yes):
    
    if not os.path.exists(f"{template_path}/instructions.py"):
        rich.print(f"[red]Template is missing instructions.py.[/red]")
        sys.exit(0)
        
    rich.print("> [red]WARNING: instructions.py will now execute. Only proceed if you trust this template.[/red]")
    
    if not yes:
        rich.print("[gold1]Continue? (y/N) > [/gold1]", end="")
        
    if yes or input("").lower() == "y":
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
        sys.exit(0)


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

if __name__ == '__main__':
    main()