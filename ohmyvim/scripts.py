from os.path import join
from os.path import isdir
from os.path import isfile
from os.path import basename
from os.path import expanduser
from urllib import urlretrieve
from subprocess import Popen
from subprocess import PIPE
import webbrowser
import subprocess
import argparse
import shutil
import sys
import os



class Manager(object):

    runtime = expanduser('~/.vim/bundle')
    autoload = expanduser('~/.vim/autoload')
    ohmyvim = expanduser('~/.vim/ohmyvim')

    dependencies = {
        'vim-pathogen': 'https://github.com/tpope/vim-pathogen.git',
        'oh-my-vim': 'https://github.com/gawel/oh-my-vim.git',
      }

    def __init__(self):
        for dirname in (self.runtime, self.autoload, self.ohmyvim):
            if not isdir(dirname):
                os.makedirs(dirname)
        for name, url in self.dependencies.items():
            if not isdir(join(self.runtime, name)):
                Popen(['git', 'clone', url, join(self.runtime, name)]).wait()
        if not isfile(join(self.ohmyvim, 'theme.vim')):
            with open(join(self.ohmyvim, 'theme.vim'), 'w') as fd:
                fd.write('')
        if not isfile(join(self.ohmyvim, 'ohmyvim.vim')):
            with open(join(self.ohmyvim, 'ohmyvim.vim'), 'w') as fd:
                fd.write(':source %s\n' % join(self.runtime, 'vim-pathogen', 'autoload', 'pathogen.vim'))            
                fd.write(':call pathogen#runtime_append_all_bundles()\n')
                fd.write(':source %s\n' % join(self.ohmyvim, 'theme.vim'))
        source = ':source %s\n' % join(self.ohmyvim, 'ohmyvim.vim')
        if not isfile(expanduser('~/.vimrc')):
            with open(expanduser('~/.vimrc'), 'w') as fd:
                fd.write('\n" added by oh-my-zsh\n')
                fd.write('let g:ohmyvim="%s"\n' % os.path.abspath(sys.argv[0]))
                fd.write(source)
        else:
            with open(expanduser('~/.vimrc')) as fd:
                if source not in fd.read():
                    with open(expanduser('~/.vimrc'), 'a') as fd:
                        fd.write('\n" added by oh-my-zsh\n')
                        fd.write('let g:ohmyvim="%s"\n' % os.path.abspath(sys.argv[0]))
                        fd.write(source)

    

    def search(self, args):
        webbrowser.open_new(("https://github.com/search?"
                            "langOverride=&q=language%3Aviml&repo=&start_value=1&type=Repositories"))

    def get_plugins(self):
        plugins = []
        for plugin in os.listdir(self.runtime):
            dirname = join(self.runtime, plugin)
            if isdir(join(dirname, '.git')):
                themes = []
                if isdir(join(dirname, 'colors')):
                    themes = os.listdir(join(dirname, 'colors'))        
                    themes = [t[:-4] for t in themes]
                plugins.append((plugin, dirname, themes))
        return plugins

    def list(self, args):
        for plugin, dirname, themes in self.get_plugins():
            os.chdir(dirname)
            p = Popen(['git', 'remote', '-v'], stdout=PIPE)
            p.wait()
            remote = p.stdout.read().split('\n')[0]
            print '* %s (%s)' % (plugin, remote.split('\t')[1].split(' ')[0])

    def install(self, args):
        for url in args.url:
            if url.endswith('.git'):
                name = basename(url)[:-4]
                dirname = join(self.runtime, name)
                if os.path.isdir(dirname):
                    print '%s already installed. Upgrading...' % name
                    os.chdir(dirname)
                    Popen(['git', 'pull']).wait()
                else:
                    print 'Installing bundle %s...' % name
                    Popen(['git', 'clone', url, dirname]).wait()
            else:
                print '%s is not a git url' % url

    def upgrade(self, args):
        for plugin, dirname, themes in self.get_plugins():
            print 'Upgrading %s...' % plugin
            os.chdir(dirname)
            Popen(['git', 'pull']).wait()
           

    def remove(self, args):
        for plugin, dirname, themes in self.get_plugins():
            if plugin in args.bundle:
                if plugin in ('vim-pathogen',):
                    print "Don't remove %s!" % plugin
                print 'Removing %s...' % name
                dirname = join(self.runtime, name)
                if isdir(join(dirname, '.git')):
                    shutil.rmtree(dirname)

    def theme(self, args):
        theme = args.theme
        if theme:
            for plugin, dirname, themes in self.get_plugins():
                if theme in themes:
                    print 'Activating %s theme...' % theme
                    with open(join(self.ohmyvim, 'theme.vim'), 'w') as fd:
                        fd.write(':colo %s\n' % theme)
            return
        for plugin, dirname, themes in self.get_plugins():
            if isdir(join(dirname, '.git')):
                os.chdir(dirname)
                p = Popen(['git', 'remote', '-v'], stdout=PIPE)
                p.wait()
                remote = p.stdout.read().split('\n')[0]
            if themes:
                print '* %s (%s)' % (plugin, remote.split('\t')[1].split(' ')[0])
                print '\t- %s' % ', '.join(themes)


def main(*args):
    manager = Manager()

    parser = argparse.ArgumentParser(description='Oh my Vim!')
    subparsers = parser.add_subparsers(help='sub-command help')

    p = subparsers.add_parser('list')
    p.add_argument('-t', '--theme-only', action='store_true', default=False)
    p.set_defaults(action=manager.list)

    p = subparsers.add_parser('search')
    p.set_defaults(action=manager.search)

    p = subparsers.add_parser('install', help='install a script or bundle')
    p.add_argument('url', nargs='*', default='')
    p.set_defaults(action=manager.install)

    p = subparsers.add_parser('upgrade', help='upgrade bundles')
    p.set_defaults(action=manager.upgrade)

    p = subparsers.add_parser('remove', help='remove a bundle')
    p.add_argument('bundle', nargs='*', default='')
    p.set_defaults(action=manager.remove)

    p = subparsers.add_parser('theme', help='list or activate a theme')
    p.add_argument('theme', nargs='?', default='')
    p.set_defaults(action=manager.theme)

    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()
    args.action(args)


