import sublime, sublime_plugin
import os, string, re

class DetectFileTypeCommand(sublime_plugin.EventListener):
    """ Attempts to choose the correct syntax when more than one could apply. """


    def __init__(self):
        super(DetectFileTypeCommand, self).__init__()
        self.path = None
        self.name = None
        self.ext = None
        self.first_line = None
        self.view = None


    def on_load(self, view):
        self.check_syntax(view)


    # As of build 2150, on_activated is no longer necessary as the on_post_save works as
    # expected (meaning the syntax set in on_post_save does not get overwritten by something
    # after the callback finishes).
    # def on_activated(self, view):
    #   self.check_syntax(view)


    def on_post_save(self, view):
        self.check_syntax(view)


    def check_syntax(self, view):
        file_name = view.file_name()

        if not file_name: # buffer has never been saved
            return

        self.reset_cache_variables(view, file_name)

        if self.is_xml():
            return

        if self.is_rspec():
            return

        if self.is_cucumber():
            return

        if self.is_rails():
            return

        if self.is_ruby():
            return

        if self.is_php():
            return

        if self.is_apache():
            return


    def is_rspec(self):
        if self.name.find('_spec') > -1:
            self.set_syntax('RSpec')
            return True

        return False


    def is_cucumber(self):
        if re.search('steps$', self.name):
            self.set_syntax('Cucumber Steps', 'Cucumber')
            return True
        elif re.search('.feature', self.name):
            self.set_syntax('Cucumber Plain Text Feature', 'Cucumber')
            return True

        return False


    def is_rails(self):
        if self.name.find('gemfile') == 0:
            self.set_syntax('Ruby on Rails', 'Rails')
            return True

        if self.ext == '.html':
            self.set_syntax('HTML (Rails)', 'Rails')
            return True

        if self.ext == '.haml':
            self.set_syntax('Ruby Haml', 'Rails')
            return True

        # start at the deepest level and look for <current_dir>/config/routes.rb, working
        # backward until it is found or we run out of directories.

        in_rails_dir = False

        path = self.path
        while path != '':
            if os.path.exists(path + '/config/routes.rb'):
                in_rails_dir = True
                break
            else:
                dirs = path.split('/')
                dirs.pop()
                path = '/'.join(dirs)

        if self.ext in ['.rb', '.rake'] and in_rails_dir:
            self.set_syntax('Ruby on Rails', 'Rails')
            return True

        return False


    def is_ruby(self):
        if self.ext == '.rb':
            self.set_syntax(view, 'Ruby')
            return True

        self.set_first_line()

        if self.first_line.find('#!') == 0 and self.first_line.find('ruby') > -1:
            self.set_syntax('Ruby')
            return True

        return False


    def is_xml(self):
        if self.ext == '.xml':
            self.set_syntax('XML')
            return True

        self.set_first_line()

        if self.first_line.find('<?xml') == 0:
            self.set_syntax('XML')
            return True

        return False


    def is_apache(self):
        if self.name in ['.htaccess', '.htpasswd', '.htgroups', 'httpd.conf']:
            self.set_syntax('Apache')
            return True

        return False


    def is_php(self):
        if self.ext == '.tpl':
            self.set_syntax('Smarty', 'PHP')
            return True

        return False


    def reset_cache_variables(self, view, file_name):
        self.view = view
        self.file_name = file_name

        self.path = os.path.dirname(file_name)
        self.name = os.path.basename(file_name).lower()
        self.name, self.ext = os.path.splitext(self.name)

        self.first_line = None


    def set_first_line(self):
        with open(self.file_name, 'r') as f:
            self.first_line = f.readline()


    def set_syntax(self, syntax, path = None):
        if path is None:
            path = syntax

        new_syntax = 'Packages/' + path + '/' + syntax + '.tmLanguage'
        current_syntax = self.view.settings().get('syntax')

        if current_syntax != new_syntax:
            self.view.settings().set('syntax', new_syntax)
            print "Switched syntax to: " + syntax
