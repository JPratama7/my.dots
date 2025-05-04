import os
import subprocess
import tempfile
import traceback
import pathlib

from loguru import logger
from packages import CUSTOM


class PostInstallation:
    @staticmethod
    def apply():
        logger.info("The post-installation configuration is starting...")
        PostInstallation._set_fish_shell()
        PostInstallation._add_to_gamemode_group()
        PostInstallation._set_default_term()
        PostInstallation._ensure_en_us_locale()
        PostInstallation._set_gpg_gui_agent()
        logger.info("The post-installation configuration is complete!")

    @staticmethod
    def _set_gpg_gui_agent():
        data = ""
        try:
            current = os.read(pathlib.Path.home() / ".gnupg/gpg-agent.conf")
            if current:
                data = current.decode("utf-8")
        except Exception:
            logger.error(
                f"Error reading gpg-agent.conf: {traceback.format_exc()}"
            )
        if data.find("pinentry-program") == -1:
            data += "pinentry-program /usr/bin/pinentry-gnome3\n"
        if data.find("allow-loopback-pinentry") == -1:
            data += "allow-loopback-pinentry\n"
        if data.find("default-cache-ttl") == -1:
            data += "default-cache-ttl 600\n"
        if data.find("max-cache-ttl") == -1:
            data += "max-cache-ttl 7200\n"

        try:
            with open(pathlib.Path.home() / ".gnupg/gpg-agent.conf", "w") as f:
                f.write(data)
            subprocess.run(["gpg-connect-agent", "reloadagent"], check=True)
            logger.success("GPG GUI agent is set!")
        except Exception:
            logger.error(
                f"Error writing gpg-agent.conf: {traceback.format_exc()}"
            )
        
    @staticmethod
    def _ensure_en_us_locale():
        locale_file = "/etc/locale.gen"
        target_line = "en_US.UTF-8 UTF-8"
        commented_line = f"#{target_line}"
        found = False
        modified = False

        if not os.path.exists(locale_file):
            logger.warning(
                f'Failed to add a locale. Error: file "{locale_file}" not found!'
            )
            return False

        with open(locale_file) as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped == commented_line:
                new_lines.append(target_line + "\n")
                modified = True
                found = True
            elif stripped == target_line:
                new_lines.append(line)
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(target_line + "\n")
            modified = True

        if modified:
            try:
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
                    tmp_file.writelines(new_lines)
                    tmp_path = tmp_file.name

                subprocess.run(["sudo", "cp", tmp_path, locale_file], check=True)
                os.unlink(tmp_path)

                logger.info("Applying locale-gen....")
                subprocess.run(["sudo", "locale-gen"], check=True)
                logger.success(f'Locale "{target_line}" successfully added!')
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to add a locale. Error: {e}")
                return False
            except Exception:
                logger.warning(f"Failed to add a locale. Error: {traceback.format_exc()}")
        else:
            logger.success(f'Locale "{target_line}" successfully added!')
            return True

    @staticmethod
    def _set_fish_shell() -> None:
        try:
            subprocess.run(["chsh", "-s", "/usr/bin/fish"], check=True)
            logger.success("The shell is changed to fish!")
        except Exception:
            logger.error(f"Error changing shell: {traceback.format_exc()}")

    @staticmethod
    def _add_to_gamemode_group() -> bool:
        if (
            "games" in CUSTOM
            and "gamemode" in CUSTOM["games"]
            and CUSTOM["games"]["gamemode"].selected
        ):
            try:
                username = os.getenv("USER") or os.getenv("LOGNAME")
                subprocess.run(
                    ["sudo", "usermod", "-a", username, "-G", "gamemode"], check=True
                )
                logger.success("The user is added to the gamemode group!")
            except Exception:
                logger.error(
                    f"Error adding user to group for gamemode: {traceback.format_exc()}"
                )

    @staticmethod
    def _set_default_term() -> bool:
        try:
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.cinnamon.desktop.default-applications.terminal",
                    "exec",
                    "kitty",
                ],
                check=True,
            )
            logger.success("The default terminal is set to kitty!")
            return True
        except Exception:
            logger.error(f"Error setting default terminal: {traceback.format_exc()}")
            return False