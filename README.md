# Abaqus-Plugins
A collection of my Abaqus/CAE GUI plugins for Abaqus 6.14

Some plugins were made during learning how to code.
Some plugins were made to solve specific tasks in my work.

Each plugin has two Python files: one ending on ...DB.py and one ending on ..._plugin.py
During start of Abaqus/CAE these get compiled to .pyc files.

The actual plugins functions can be found in myPluginFunctions.py.
All plugins files depend on this file in the same directory to work properly.
The file myPluginFunctions.py also explains in the comments what actions are performed.

Load all necessary files into a folder "abaqus_plugins" in your Abqus Work directory to test them.
The plugins will then be accessible under "Plug-ins" in the toolbar.

Please comment and help me improve!

/Johannes
