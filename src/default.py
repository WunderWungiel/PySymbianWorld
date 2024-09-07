# -*- coding: utf-8 -*-
"""Copyright 2023 Wunder Wungiel"""
import appuifw2 as appuifw
import e32
import urllib
import os
import simplejson as json

# Use e32.drive_list() to retrieve drives list
def get_drive():
    drives = e32.drive_list()
    # Remove Z and Y
    for letter in [u"Z:", u"Y:"]:
        if letter in drives:
            drives.remove(letter)
    return drives[-1] + "\\SymbianWorld"

dl_path = get_drive()

if not os.path.isdir(dl_path):
    os.mkdir(dl_path)

class API:
    def __init__(self):
        self.api_url = "http://wunderwungiel.pl/pysymbianworld/"

    def get_categories(self):
        r = urllib.urlopen(self.api_url + "get_categories/")
        return json.loads(r.read().decode("utf-8"))

    def get_files(self, category):
        r = urllib.urlopen(self.api_url + "get_files/?category=%s" % category)

        data = u""

        while True:
            chunk = r.read(1024)
            if not chunk:
                break
            data += chunk.decode("utf-8", 'ignore')

        r.close()

        return json.loads(data)

api = API()

class App1:
    def __init__(self):
        self.entries_names = api.get_categories()

    def handler(self):
        index = self.app1.current()
        title = self.entries_names[index]
        link = urllib.quote(title)
        folderview = self.FolderView(self, link, title)
        appuifw.app.view = folderview
    def run(self):
        self.app1 = appuifw.Listbox(self.entries_names, self.handler)
        return self.app1

    class FolderView(appuifw.View):
        def __init__(self, app1, link, title):
            appuifw.View.__init__(self)
            self.app1 = app1
            self.title = title
            self.exit_key_text = u"Back"
            self.files_names = api.get_files(title)
            self.menu = [(u"Search", self.search), (u"About", app2.run_body), (u"Exit", exit_key_handler)]
            self.body = self.run()

        def handler(self):
            index = self.folder_app.current()
            filename = self.files_names[index]
            title = self.title
            self.download(filename, title)

        def run(self):
            self.folder_app = appuifw.Listbox(self.files_names, self.handler)
            return self.folder_app

        def download(self, filename, title):
            link = urllib.quote(title) + "/" + urllib.quote(filename)
            try:
                response = urllib.urlopen("http://wunderwungiel.pl/Symbian/SymbianWorldMegaRepo/%s" % link)
            except urllib.HTTPError:
                appuifw.note(u"Error while downloading %s!" % filename, "error")
                return
            except urllib.URLError:
                appuifw.note(u"Error while downloading %s!" % filename, "error")
                return
            path = os.path.join(dl_path, filename)

            appuifw.note(u"Wait... Downloading %s" % filename)
            f = open(path, "wb")
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                f.write(chunk)
            f.close()
            file_opener.open(path)

        def search(self):
            
            query = appuifw.query(u"Search query", "text")
            if not query:
                return

            results = []
            for file_name in self.files_names:
                if file_name.lower().find(query.lower()) != -1:
                    results.append(unicode(file_name))
            
            if not results:
                appuifw.note(u"No search results")
                return

            selected_choices = appuifw.multi_selection_list(results, style='checkbox', search_field=1)
            if not selected_choices:
                return
            for choice in selected_choices:
                filename = self.files_names[self.files_names.index(results[choice])]
                self.download(filename, self.title)

class App2:
    def __init__(self):
        pass
    def run(self):
        about = appuifw.Text(scrollbar=True, skinned=True)
        about.font = (u"Nokia Sans S60", 25)
        about.style = appuifw.STYLE_BOLD
        about.add(u"Symbian World")
        about.font = (u"Nokia Sans S60", 15)
        about.add(u"\n\nBrowse Symbian World Mega Repo easier.")
        about.add(u"\n\n----------------------------\n\n")
        about.add(u"Join our Telegram group:")
        about.style = appuifw.STYLE_UNDERLINE
        about.add(u"\n\nhttps://t.me/symbian_world")
        return about
    def run_body(self):
        appuifw.app.set_tabs([u"Browse", u"About"], handle_tab)
        appuifw.app.exit_key_handler = exit_key_handler
        about_app = self.run()
        appuifw.app.activate_tab(1)
        appuifw.app.title = u"About"
        appuifw.app.body = about_app

app1 = App1()
app2 = App2()

def handle_tab(index):
    appuifw.app.exit_key_handler = exit_key_handler
    if index == 0:
        appuifw.app.title = u"Symbian World"
        appuifw.app.body = app1.run()
    if index == 1:
        appuifw.app.title = u"About"
        appuifw.app.body = app2.run()

class ReturnKeyHandler:
    def __init__(self):
        pass
    def folder_to_app1(self):
        appuifw.app.activate_tab(0)
        appuifw.app.title = u'Symbian World'
        appuifw.app.menu = [(u"About", app2.run_body), (u"Exit", exit_key_handler)]
        appuifw.app.body = app1.run()
        appuifw.app.exit_key_text = u"Exit"
        appuifw.app.exit_key_handler = exit_key_handler

def exit_key_handler():
    app_lock.signal()
    appuifw.app.set_exit()

app_lock = e32.Ao_lock()
file_opener = appuifw.Content_handler()
appuifw.app.menu = [(u"About", app2.run_body), (u"Exit", exit_key_handler)]
appuifw.app.set_tabs([u"Browse", u"About"], handle_tab)
appuifw.app.title = u'Symbian World'
appuifw.app.screen = "normal"
appuifw.app.body = app1.run()
appuifw.app.exit_key_handler = exit_key_handler
app_lock.wait()
