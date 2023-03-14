"""
This Plugin can Manage Python Plugins from oder communities

This is just a PoC - use at your own risk
"""

from albert import *
from git import Repo,GitCommandError
import os
import re


md_iid = "0.5"
md_version = "1.0"
md_id = "cem"
md_name = "Community Extension Manager"
md_description = "Install, Remove and update Python Plugins"
md_license = "MIT"
md_url = ""
md_maintainers = "@Bierchermuesli"
md_lib_dependencies = ["git-python"]


pluginroot=dataLocation()+"/python/plugins/"

class Plugin(QueryHandler):
    def id(self):
        return md_id

    def name(self):
        return md_name

    def description(self):
        return md_description

    def git_clone(self,uri,name):
        """ get name from GIT repo if no name is given """

        installdir = pluginroot+name
        info("GIT clone Plugin '{}' from '{}' to '{}'".format(name,uri,installdir))

        # try:
        #     git.Repo(installdir)
        #     sendTrayNotification("Install Error", installdir+"already exist")
        # except git.InvalidGitRepositoryError:
        #     g=git.Git(installdir)

        if not os.path.isdir(installdir):
            repo = Repo.clone_from(uri,installdir)
            debug(repo)
            sendTrayNotification("Install Status", str(repo.index))
        else:                           # otherwise, clone from remote
            # repo = Repo(installdir) 
            # repo.remotes.origin.pull()
            sendTrayNotification("Install Error", "skipped, plugin already exist")


    def git_pull(self,path):
        """ makes an git pull on a given folder"""
        try:
            repo = Repo(path)
        except:
            sendTrayNotification("Update Error", "Is this folder a GIT repo?")

        if repo.is_dirty():
            sendTrayNotification("Update skipped","this repo has local changes")
        else:
            try:
                repo.remotes.origin.pull()
                sendTrayNotification("Update Sucess",str(repo.git.status()))
            except GitCommandError as err:
                sendTrayNotification("Update Failed",str(err))



    def del_tree(self,path):
        """ deletes a folder tree, but it is disabled for safety reasons """
        try:
            #maybe unsafe?
            #from rmtree import shutil
            #rmtree(path)
            #sendTrayNotification("Deleted", path)
            sendTrayNotification("would deleted but i'm disabled", path)
        except OSError as e:
            sendTrayNotification("Delete Error", "{} - {}".format(e.filename, e.strerror))

    def list_dir(self,dir):
        """ simply lists a folder tree"""
        return os.listdir(dir)


    def handleQuery(self, query):
        

        # install from GIT URL action 
        # usage: install <git-uri> [optional name]
        if install := re.match("install\s+(?P<url>(?:git@|https:\/\/).*.git)?\s*(?P<name>\w+)?",query.string):    
            if url := install.group('url'):
                if (name := install.group('name')) is None:
                    name = url.rsplit('/', 1)[-1]
                    name = name.replace('albert-','').replace('.git','')

                query.add(Item(
                    id="install",
                    text="Install "+ name,
                    subtext="Install to"+ pluginroot + name,
                    icon=["xdg:folder-download"],
                    actions=[Action(
                            id="url",
                            text="Open GIT in Browser",
                            callable=lambda: openUrl(url)
                        ),
                        Action(
                            id="install "+name,
                            text="Yes, I trust this maintainer, clone this Repo",
                            callable = lambda: self.git_clone(url,name)
                            ),
                        # Action(
                        #     id="url",
                        #     text="Open Plugins root (via openUrl)",
                        #     callable=lambda: openUrl(pluginroot)),
                        Action(
                            id="url",
                            text="Open plugins root dir",
                            callable=lambda: runDetachedProcess(cmdln=["xdg-open", pluginroot]))                        
                        ]
                      ))
            else:
                return(query.add(Item(
                id = "unknown",
                icon = ["xdg:folder-recent"],
                text = "Invalid URL Source",
                subtext = "usage: install <https://example.com/git.git> [name]")))


        # list installed plugins handler
        # usage: list [optional search string]
        elif list := re.match("list\s*(?P<filter>\w+)?",query.string):
            for p in self.list_dir(pluginroot):
                if filter := list.group('filter'):
                    if filter not in p:
                        continue
                
                if os.path.isfile(pluginroot+p+"/icon.svg"):
                    icon =  pluginroot+p+"/icon.svg"
                elif os.path.isfile(pluginroot+p+"/icon.png"):
                    icon =  pluginroot+p+"/icon.png"                    
                else:
                    icon = 'xdg:albert'
                
                actions = [
                        Action(
                            id="copy"+p,
                            text="Copy Path",
                            callable=lambda p=pluginroot+p: setClipboardText(p)),
                        Action(
                            id="open"+p,
                            text="Open Folder",
                            callable=lambda p=pluginroot+p: runDetachedProcess(cmdln=["xdg-open", p])),
                        Action(
                            id="delete"+p,
                            text="Delete",
                            callable = lambda p=pluginroot+p: self.del_tree(p)),
                        ]


                if os.path.isdir(pluginroot+p+"/.git"):
                    actions.append(
                        Action(
                            id="update"+p,
                            text="Update",
                            callable = lambda p=pluginroot+p: self.git_pull(p))
                        )

                query.add(Item(
                    id=p,
                    text=p,
                    subtext="Installed at "+pluginroot+p,
                    icon= [icon],
                    actions=actions))

            
        #this is for only demo usage
        elif search := re.match("search\s*(?P<filter>.*)?",query.string):
            
            if filter := search.group('filter'):
                query.add(Item(
                    id = "search",
                    icon = ["xdg:search"],
                    text = filter,
                    subtext = "find extensions (not implemented, just a idea)"))
        else:
            return(query.add(Item(
                id = "unknown",
                icon = ["xdg:folder-recent"],
                text = "list|install|search",
                subtext = "usage: install <https://example.com/git.git> [name]")))