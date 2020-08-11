import asyncio
import subprocess
import toga
from toga.style.pack import Pack, ROW, CENTER, COLUMN
import time
import sys
import os
from pathlib import Path
from urllib.parse import quote


def install_dependencies(*args, **kwargs):
    print("Command called")
    import subprocess

    subprocess.call("pip install numpy", shell=True)
    print("Success")
    # stdout, stderr = await proc.communicate()

    # print(f'[{cmd!r} exited with {proc.returncode}]')
    # if stdout:
    #     print(f'[stdout]\n{stdout.decode()}')
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')


class Database(toga.Document):
    def __init__(self, filename, app):
        super().__init__(filename=filename, document_type="SQLite3 Database", app=app)

        self.window = toga.Window(title=filename, size=(768, 768))
        self.window.on_close = self.close_window
        self.webview = toga.WebView(style=Pack(flex=1))
        self.window.content = self.webview

    def close_window(self):
        self.proc.kill()

    def read(self):
        asyncio.ensure_future(self.start_datasette(self.filename))

    def show(self):
        self.window.show()

    async def start_datasette(self, filename):
        filename = Path(filename)
        print(filename)
        command = "datasette serve {}".format(filename)
        print(command)
        self.proc = await asyncio.create_subprocess_shell(
            command,
            stdin=None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        line = await self.proc.stderr.readline()
        while line:
            print(line)
            line = line.strip().decode("utf-8")
            if "http" in line:

                parts = line.split()
                for part in parts:
                    if part.startswith("http"):
                        self.webview.url = part

                # url = "{}notebooks/{}".format(url, quote(filename.name))
                # self.webview.url = url
            line = await self.proc.stderr.readline()


class Walkman(toga.DocumentApp):
    def __init__(self):
        resource_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        super().__init__(
            "Walkman", document_types={"sqlite3": Database},
        )
        os.environ["PIP_TARGET"] = str(self.paths.data / "pkgs")
        sys.path.append(str(self.paths.data / "pkgs"))
        os.environ["PYTHONPATH"] += ":" + str(self.paths.data / "pkgs")
        print(os.environ["PYTHONPATH"])

        cmd1 = toga.Command(
            install_dependencies,
            label="Install packages",
            tooltip="Installs some helpful packages",
            shortcut=toga.Key.MOD_1 + "i",
            icon="icons/pretty.png",
            group=toga.Group.FILE,
            section=0,
        )

        self.commands.add(cmd1)

    def startup(self):
        pass


def main():
    Walkman().main_loop()


if __name__ == "__main__":
    main()
