import os
import shutil
import rich
import argparse
import runpy
import sys

def main():
    parser = argparse.ArgumentParser(description="Simple scalable scaffolder that creates and executes setups of predefined templates from its Templates/ directory.")
    parser.add_argument("name", nargs="?", help="Project name. Prompted if not provided.")
    parser.add_argument("-t", "--template", help="Template to use. Run with -t alone to list available templates.")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip all prompts and confirm everything automatically.")
    args = parser.parse_args()
    template_dir = f"{os.path.dirname(os.path.abspath(__file__))}/Templates/"
    
    if args.template is None:
        rich.print("> [light_sky_blue1]No template selected. Use the -t or --template flag to select.[/light_sky_blue1]")
        rich.print("Available templates:")
        for templ in os.scandir(template_dir):
            if templ.is_dir and os.path.exists(f"{templ.path}/scaffold.txt"):
                with open(f"{templ.path}/scaffold.txt") as f:
                    rich.print(f"    - [gold1]{templ.name}[/gold1] : {f.read()}")
        sys.exit(0)
    
    template_path = os.path.join(template_dir, args.template)
    
    
    if not os.path.isdir(template_path):
        rich.print(f"[red]Template '{args.template}' not found.[/red]")
        sys.exit(1)
    
    if args.name:
        project_name = args.name
    else:
        rich.print("[gold1]Project name > [/gold1]", end="")
        project_name: str = input("")
        
    sou  = template_path #SOUrce
    des = f"./{project_name}-scaffold" if os.path.isdir(f"./{project_name}") else f"./{project_name}" #DEStination
    

    if not os.path.exists(f"{template_path}/instructions.py"):
        rich.print(f"[red]Template is missing instructions.py.[/red]")
        sys.exit(1)
    
    try:
        shutil.copytree(src=sou, dst=des, ignore=shutil.ignore_patterns("instructions.py", "scaffold.txt"))
    except Exception as e:
        abort(msg=f"Something went wrong: {e}", des=des)
    
    rich.print(f'[grey50]-------[/grey50] [green1]"{project_name}" Created successfully[/green1] [grey50]-------[/grey50]')
    rich.print("> [red]WARNING: instructions.py will now execute. Only proceed if you trust this template.[/red]")
    if not args.yes:
        rich.print("[gold1]Continue? (y/N) > [/gold1]", end="")
    if args.yes or input("").lower() == "y":

        try:
            runpy.run_path(f"{template_path}/instructions.py", init_globals={
                "project_path": des,
                "project_name": project_name,
                "yes": args.yes
            })
        except Exception as e:
            abort(msg=f"Something went wrong: {e}", des=des)
    else:
        rich.print("> [light_sky_blue1]Instructions not executed. Copying complete.[/light_sky_blue1]")
        sys.exit(0)


def abort(msg, des):
    rich.print(f"[red]{msg}[/red]")
    if os.path.isdir(des):
        rich.print("[red]Reverting changes[/red]")
        shutil.rmtree(des)
    sys.exit(1)
    


if __name__ == '__main__':
    main()