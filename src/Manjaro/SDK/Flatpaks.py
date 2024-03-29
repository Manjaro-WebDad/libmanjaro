import gi
from gi.repository import GLib
from Manjaro.SDK import Utils

class Flatpak():
    def __init__(self, pm_instance):
        self.pm = pm_instance
        self.pm.config.set_enable_flatpak(True)
        self.install = []
        self.remove = []


    def is_plugin_installed(self):
        return self.pm.config.get_support_flatpak()

    
    def search(self, pkg):
        pkgs = []
        def callback(source_object, result):
            try:
                flatpaks = source_object.search_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for p in flatpaks:
                    pkgs.append(p)
            finally:
                self.pm.loop.quit()

        self.pm.db.search_flatpaks_async(pkg, callback)
        self.pm.loop.run()
        return tuple(pkgs)

    
    def get_details(self, pkg):
        info = {}      
        info["format"] = "flatpak"  
        info["app_id"] = pkg.get_app_id()
        info["title"] = pkg.get_app_name()
        info["description"] = pkg.get_desc()
        info["download_size"] = Utils.convert_bytes_to_human(pkg.get_download_size())
        info["icon"] = pkg.get_icon()
        info["id"] = pkg.get_id()
        info["install_date"] = Utils.glib_date_to_string(pkg.get_install_date())
        info["installed_size"] = Utils.convert_bytes_to_human(pkg.get_installed_size())
        info["installed_version"] = pkg.get_installed_version()
        info["launchable"] = pkg.get_launchable()
        info["license"] = pkg.get_license()
        info["long_description"] = pkg.get_long_desc()
        info["name"] = pkg.get_name()
        info["repository"] = pkg.get_repo()
        info["screenshots"] = pkg.get_screenshots()
        info["url"] = pkg.get_url()
        info["version"] = pkg.get_version()            
        return info


    def get_available(self, db=[]):
        def on_category_ready(source_object, result):
            try:
                pkgs = source_object.get_category_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in pkgs:
                    if pkg.get_name() not in (p.get_name() for p in db):
                        db.append(pkg)
            finally:
                self.pm.loop.quit()

        for category in self.pm.get_categories():
            if category !="Featured":
                self.pm.db.get_category_flatpaks_async(category, on_category_ready)
                self.pm.loop.run()

        return tuple(db)