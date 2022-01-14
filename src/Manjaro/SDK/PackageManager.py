import gi
try:
    gi.require_version('Pamac', '11')
except Exception as e:
    print("WARNING: installed Libpamac version does not match SDK")
from gi.repository import GLib, Pamac as pamac
from Manjaro.SDK import Utils


class Pamac():
    def __init__(self, options={
        "config_path": "/etc/pamac.conf",
        "dry_run": False,
        "update": True
    }):
        self._packages = {
            "install": {
                "packages": [],
                "snaps": [],
                "flatpaks": []
            },
            "remove": {
                "packages": [],
                "snaps": [],
                "flatpaks": []
            }
        }
        self.config = pamac.Config(conf_path=options["config_path"])
        self.options = options
        self.db = pamac.Database(config=self.config)
        self.db.enable_appstream()
        self.data = None
        self.transaction = pamac.Transaction(database=self.db)
        self.transaction.connect(
            "emit-action", self.on_emit_action, self.data)
        self.transaction.connect(
            "emit-action-progress", self._on_emit_action_progress, self.data)
        self.transaction.connect("emit-hook-progress",
                                 self._on_emit_hook_progress, self.data)
        self.transaction.connect(
            "emit-error", self.on_emit_error, self.data)
        self.transaction.connect(
            "emit-warning", self.on_emit_warning, self.data)
        self.loop = GLib.MainLoop()

    def search_flatpaks(self, pkg: str) -> list:
        pkgs = []

        def callback(source_object, result):
            try:
                flatpaks = source_object.search_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in flatpaks:
                    pkgs.append(pkg)
            finally:
                self.loop.quit()

        self.config.set_enable_flatpak(True)
        self.db.search_flatpaks_async(pkg, callback)
        self.loop.run()
        return pkgs

    def search_snaps(self, pkg: str) -> list:
        pkgs = []

        def callback(source_object, result):
            try:
                snaps = source_object.search_snaps_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in snaps:
                    pkgs.append(pkg)
            finally:
                self.loop.quit()

        self.config.set_enable_snap(True)
        self.db.search_snaps_async(pkg, callback)
        self.loop.run()
        return pkgs

    def search_pkgs(self, pkg: str) -> list:
        pkgs = []
        pkd_db = self.db.search_pkgs(pkg)
        for p in pkd_db:
            pkgs.append(p)
        return pkgs

    def get_app_name(self, pkg: str) -> str:
        """
        return application name if available otherwise returns pkg name.
        """
        name = self.db.get_pkg(pkg).get_app_name()
        if not name:
            name = self.db.get_pkg(pkg).get_name()
        return name

    def get_pkg_details(self, pkg):
        p = self.db.get_pkg(pkg)
        info = {}
        info["app_id"] = p.get_app_id()
        info["title"] = p.get_app_name()
        info["backups"] = p.get_backups()
        info["build_date"] = Utils.glib_date_to_string(p.get_build_date())
        info["check_depends"] = p.get_checkdepends()
        info["conflits"] = p.get_conflicts()
        info["depends"] = p.get_depends()
        info["description"] = p.get_desc()
        info["download_size"] = p.get_download_size()
        info["groups"] = p.get_groups()
        info["ha_signature"] = p.get_has_signature()
        info["icon"] = p.get_icon()
        info["pkg_id"] = p.get_id()
        info["install_date"] = Utils.glib_date_to_string(p.get_install_date())
        info["installed_size"] = p.get_installed_size()
        info["installed_version"] = p.get_installed_version()
        info["launchable"] = p.get_launchable()
        info["license"] = p.get_license()
        info["long_description"] = p.get_long_desc()
        info["makedepends"] = p.get_makedepends()
        info["name"] = p.get_name()
        info["optdepends"] = p.get_optdepends()
        info["optionalfor"] = p.get_optionalfor()
        info["packager"] = p.get_packager()
        info["provides"] = p.get_provides()
        info["reason"] = None
        if p.get_reason():
            info["reason"] = p.get_reason()
        info["replaces"] = p.get_replaces()
        info["repository"] = p.get_repo()
        info["required_by"] = p.get_requiredby()
        info["screenshots"] = p.get_screenshots()
        info["url"] = p.get_url()
        info["version"] = p.get_version()
        return info

    def get_snap_details(self, pkg):
        info = {}

        def callback(source_object, result):
            try:
                p = source_object.get_snap_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                info["app_id"] = p.get_app_id()
                info["title"] = p.get_app_name()
                info["channel"] = p.get_channel()
                info["channels"] = p.get_channels()
                info["confined"] = p.get_confined()
                info["description"] = p.get_desc()
                info["download_size"] = p.get_download_size()
                info["icon"] = p.get_icon()
                info["id"] = p.get_id()
                info["install_date"] = Utils.glib_date_to_string(p.get_install_date())
                info["installed_size"] = p.get_installed_size()
                info["installed_version"] = p.get_installed_version()
                info["launchable"] = p.get_launchable()
                info["license"] = p.get_license()
                info["long_description"] = p.get_long_desc()
                info["name"] = p.get_name()
                info["publisher"] = p.get_publisher()
                info["repository"] = p.get_repo()
                info["screenshots"] = p.get_screenshots()
                info["url"] = p.get_url()
                info["version"] = p.get_version()
            finally:
                self.loop.quit()

        self.db.get_snap_async(pkg, callback)
        self.loop.run()
        return info

    def get_flatpak_details(self, pkg):
        info = {}        
        info["app_id"] = pkg.get_app_id()
        info["title"] = pkg.get_app_name()
        info["description"] = pkg.get_desc()
        info["download_size"] = pkg.get_download_size()
        info["icon"] = pkg.get_icon()
        info["id"] = pkg.get_id()
        info["install_date"] = Utils.glib_date_to_string(pkg.get_install_date())
        info["installed_size"] = pkg.get_installed_size()
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

    def get_repos(self) -> list:
        """
        return repositories names
        """
        return self.db.get_repos_names()

    def get_categories(self) -> list:
        """
        return categories names
        """
        return self.db.get_categories_names()

    def get_all_pkgs(self, db=[]) -> list:
        """
        return all available native packages
        """
        for repo in self.get_repos():
            repository = self.db.get_repo_pkgs(repo)
            for pkg in repository:
                db.append(pkg)

        return tuple(db)

    def get_all_snaps(self, db=[]) -> list:
        """
        return all available snaps
        """
        def callback(source_object, result):
            try:
                snaps = source_object.get_category_snaps_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in snaps:
                    db.append(pkg)
            finally:
                self.loop.quit()

        for cat in self.get_categories():
            self.db.get_category_snaps_async(cat, callback)
            self.loop.run()

        return tuple(db)

    def get_all_flatpaks(self, db=[]) -> list:
        """
        return all available flatpaks
        """
        def on_category_flatpaks_ready_callback(source_object, result):
            try:
                flatpaks = source_object.get_category_flatpaks_finish(result)
            except GLib.GError as e:
                print("Error: ", e.message)
            else:
                for pkg in flatpaks:
                    db.append(pkg)
            finally:
                self.loop.quit()

        for cat in self.get_categories():
            self.db.get_category_flatpaks_async(
                cat, on_category_flatpaks_ready_callback)
            self.loop.run()

        return tuple(db)

    def add_pkgs_to_install(self, pkgs: list, pkg_format="packages"):
        """
        add packages to installation list
        :param pkg_format: packages/snaps/flatpaks
        """
        def add(pkg):
            self._packages["install"][pkg_format].append(pkg)
            
        for pkg in pkgs:
            add(pkg)

    def remove_pkgs_from_install(self, pkgs: list, pkg_format="packages"):
        """
        remove packages from installation list
        :param pkg_format: packages/snaps/flatpaks
        """
        def remove(pkg):
            if pkg in self._packages["install"][pkg_format]:
                self._packages["install"][pkg_format].remove(pkg)

        for pkg in pkgs:
            remove(pkg)

    def add_pkgs_to_remove(self, pkgs: list, pkg_format="packages"):
        """
        check if packages are installed and
        add packages to remove list
        :param pkg_format: packages/snaps/flatpaks
        """
        def remove(pkg):
            self._packages["remove"][pkg_format].append(pkg)

        for pkg in pkgs:
            remove(pkg)

    def sanitize_packages(self, packages: list) -> list:
        """
        removes packages from the list if they do not exist
        or are not installed
        """
        pkgs = []

        def check_pkg(pkg):
            error = f"package not existent: {pkg}"
            try:
                if self.db.get_pkg(pkg).get_name() == pkg:
                    if pkg not in self.get_installed_pkgs():
                        pkgs.append(pkg)
                else:
                    print(error)
            except AttributeError:
                print(error)

        for pkg in packages:
            check_pkg(pkg)
        return pkgs

    def get_installed_pkgs(self) -> list:
        """
        return a list of all installed packages
        """
        pkgs = []
        for pkg in self.db.get_installed_pkgs():
            pkgs.append(pkg.get_name())
        return pkgs

    def on_emit_action(self, transaction, action, data):
        print(action)

    def _on_emit_action_progress(self, transaction, action, status, progress, data):
        print(f"{action} {status} {progress}")

    def _on_emit_hook_progress(self, transaction, action, details, status, progress, data):
        print(f"{action} {details} {status}")

    def on_emit_warning(self, transaction, message, data):
        print(message)

    def on_emit_error(self, *args):
        print(args[2][0])

    def on_transaction_finish(self):
        """
        to be reimplemented if we need to do something after transaction finishes
        """
        print("Transaction successful")
        
    def on_transaction_finished_callback(self, source_object, result, user_data):
        try:
            success = source_object.run_finish(result)
        except GLib.GError as e:
            print("Error: ", e.message)
        else:
            if success:
                pass
        finally:
            self.loop.quit()
            self.transaction.quit_daemon()
            self.on_transaction_finish()

    def _run_transaction(self):
        self.transaction.set_dry_run(self.options["dry_run"])
        install_pkgs = self._packages["install"]["packages"]
        install_snaps = self._packages["install"]["snaps"]
        install_flatpaks = self._packages["install"]["flatpaks"]
        remove_pkgs = self._packages["remove"]["packages"]
        remove_snaps = self._packages["remove"]["snaps"]
        remove_flatpaks = self._packages["remove"]["flatpaks"]

        if install_pkgs:
            if self.options["update"]:
                self.transaction.add_pkgs_to_upgrade(self.get_installed_pkgs())
            for pkg in install_pkgs:
                self.transaction.add_pkg_to_install(pkg)

        if install_snaps:
            self.config.set_enable_snap(True)
            for pkg in install_snaps:
                self.transaction.add_snap_to_install(pkg)

        if install_flatpaks:
            self.config.set_enable_flatpak(True)
            for pkg in install_flatpaks:
                self.transaction.add_flatpak_to_install(pkg)

        if remove_pkgs:
            for pkg in remove_pkgs:
                self.transaction.add_pkg_to_remove(pkg)

        if remove_snaps:
            self.config.set_enable_snap(True)
            for pkg in remove_snaps:
                self.transaction.add_snap_to_remove(pkg)

        if remove_flatpaks:
            self.config.set_enable_flatpak(True)
            for pkg in remove_flatpaks:
                self.transaction.add_flatpak_to_remove(pkg)

        self.transaction.run_async(self.on_transaction_finished_callback, None)
        self.loop.run()

    def on_before_transaction(self):
        """
        to be reimplemented if we need to do something before transaction starts
        """
        pass

    def run(self):
        self.on_before_transaction()
        self._run_transaction()
