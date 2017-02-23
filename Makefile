all:
	zip -9 Coq.sublime-package \
		coq.py \
		coqtop.py \
		Main.sublime-menu \
		Coq.sublime-commands \
		"Coq Keywords.sublime-completions" \
		"Coq Tactics.sublime-completions" \
		"Default (Linux).sublime-keymap" \
		"Default (OSX).sublime-keymap" \
		"Default (Windows).sublime-keymap" \
		Miscellaneous.tmPreferences \
		Coq.tmLanguage \
		Coq.sublime-settings \
		LICENSE

clean:
	rm -f Coq.sublime-package

install:
	cp Coq.sublime-package ~/.config/sublime-text-3/Installed\ Packages/

uninstall:
	rm -f ~/.config/sublime-text-3/Installed\ Packages/Coq.sublime-package
