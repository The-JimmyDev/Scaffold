import subprocess
import rich
import json

package_json_path = f"{project_path}/package.json"

rich.print("> [light_sky_blue1]Modifying package name in package.json[/light_sky_blue1]")

with open(package_json_path, "r") as f:
    data = json.load(f)

data["name"] = project_name

with open(package_json_path, "w") as f:
    json.dump(data, f, indent=2)
    
rich.print("[grey50]-------[/grey50] [green1]Modification successful[/green1] [grey50]-------[/grey50]")


rich.print("> [light_sky_blue1]Running npm install[/light_sky_blue1]")
subprocess.run(["npm", "install"], cwd=project_path, shell=True)
rich.print("[grey50]-------[/grey50] [green1]Installation successful[/green1] [grey50]-------[/grey50]")
if not yes:
    rich.print("[gold1]Run npm update? (y/n) > [/gold1]", end="")

if yes or input("").lower == "y":
    subprocess.run(["npm", "update"], cwd=project_path, shell=True)
    rich.print("[grey50]-------[/grey50] [green1]Update successful[/green1] [grey50]-------[/grey50]")

