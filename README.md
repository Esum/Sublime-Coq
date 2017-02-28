Sublime Coq
===========

Extensions to the Sublime Text 3 editor for use with the Coq Proof Assistant.


Getting Started
---------------
Currently, Coq plugin is not as flexible as you might hope, but it is still working well. First, open your coq script in a window, then select `Coq: Run` in the command palette. Now you should see another pane jumping out, showing the welcome message from `coqtop`.

All your editing operations should be done at the script pane, while all commands should be issued only at the `==COQTOP==` pane.

There are several commands available now:

* **Next statement** (OS X: `super+ctrl+n`, Win/Linux: `ctrl+down`): Prove the current line and go to next statement
* **Undo statement** (OS X: `super+ctrl+u`, Win/Linux: `ctrl+up`): Undo the current proven statement and go back to the last line. *NOTE: it seems not working as smoothly as CoqIDE now, but you can try it several times and see how it behaves.*


`coqtop` Path
-------------

You might need to modify the user settings file for Coq, change `coqtop_path` to a proper value (usually from `which coqtop` or similar way), so the `coqtop` program can be correctly found.

The default value will simply be `coqtop`, but during initialization, `$PATH` will also be searched.


Pretty output
-------------

The pretty output can be toggled with the user settings file through the option `prettify`.

The default value is `true`.


Highlighting
------------

In order to get nice background highlighting for the proven parts of the file,
add this to your theme (for light backgrounds):

```xml
<dict>
  <key>name</key>
  <string>Proven by Coq</string>
  <key>scope</key>
  <string>meta.coq.proven</string>
  <key>settings</key>
  <dict>
    <key>background</key>
    <string>#dcffcc</string>
  </dict>
</dict>
```

TODOs
-----
* Enrich the language spec
* The `undo` seems not working well sometimes


