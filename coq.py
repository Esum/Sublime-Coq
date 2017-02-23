import re
import sublime, sublime_plugin
from .coqtop import Coqtop


pretty_symbols = {
    "|-": '⊢', "||": '‖', "/\\": '∧', "\\/": '∨',
    "->": '→', "<-": '←', "<->": '↔', "=>": '⇒',
    "<=": '≤', ">=": '≥', "<>": '≠',
    ">->": '↣',
    "-->": '⟶', "<--": '⟵', "<-->": '⟷',
    "==>": '⟹', "<==": '⟸', "~~>": '⟿', "<~~": "⬳"
}

pretty_names = {
    "True": '⊤', "False": '⊥',
    "fun": 'λ', "forall": '∀', "exists": '∃',
    "nat": 'ℕ', "Prop": 'ℙ', "Real": 'ℝ', "bool": '𝔹',
}

def prettify(output):
    for symbol in sorted(pretty_symbols, key=len, reverse=True):
        output = output.replace(symbol, pretty_symbols[symbol])
    for name in pretty_names:
        output = re.sub(r"(?<![a-zA-Z0-9_])"+name+r"(?![a-zA-Z0-9_'])", pretty_names[name], output)
    return output


class CoqtopManager:

    def __init__(self):
        try:
            if self.coqtop is not None:
                self.coqtop.kill()
        except AttributeError:
            pass
        self.coqtop = None
        self.proof = False
        self.statements = []
        self.position = 0

    def start(self):
        self.coqtop = Coqtop(self, sublime.load_settings('Coq.sublime-settings').get("coqtop_path"))

    def send(self, statement, undo=False, region=None):
        if not undo:
            self.statements.append((str(self.position), statement, region))
        self.coqtop.send(statement)

    def receive(self, output, prompt):
        output = prettify(output)
        if output:
            self.output_view.run_command('coqtop_output', {'output': output})
        if re.search(r'(^Error:|^Syntax [eE]rror:)', output, re.M) is None:
            self.output_view.run_command('coqtop_success')
        else:
            self.statements.pop()
manager = CoqtopManager()


class RunCoqtopCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coq_syntax = self.view.settings().get('syntax')
        window = self.view.window()
        editor_group = window.active_group()
        self.view.settings().set('coqtop_running', True)
        window.run_command('new_pane', {"move": False})
        window.focus_group(editor_group)
        coq_group = window.num_groups() - 1
        coqtop_view = window.active_view_in_group(coq_group)
        coqtop_view.set_syntax_file(coq_syntax)
        coqtop_view.set_name('==COQTOP==')
        coqtop_view.set_read_only(True)
        coqtop_view.set_scratch(True)
        coqtop_view.settings().set('coqtop_running', True)
        manager.file_view = self.view
        manager.output_view = coqtop_view
        manager.start()


class CoqtopOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output):
        entire_region = sublime.Region(0, self.view.size())
        self.view.set_read_only(False)
        self.view.erase(edit, entire_region)
        self.view.insert(edit, 0, output)
        self.view.set_read_only(True)


class CoqNextStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view
        manager.position = coqfile_view.find(r'(\s|\n)*', manager.position).end()
        while coqfile_view.substr(manager.position) == '(' and coqfile_view.substr(manager.position + 1) == '*':
            comment = 1
            manager.position += 2
            while comment:
                if coqfile_view.substr(manager.position) == '(' and coqfile_view.substr(manager.position+1) == '*':
                    comment += 1
                elif coqfile_view.substr(manager.position) == ')' and coqfile_view.substr(manager.position-1) == '*' and coqfile_view.substr(manager.position-2) != '(':
                    comment -= 1
                manager.position += 1
            manager.position = coqfile_view.find(r'(\s|\n)*', manager.position).end()
        r = coqfile_view.find(r'(.|\n)*?\.(?=\s|\n|$)', manager.position)
        statement = coqfile_view.substr(r)
        if statement == 'Proof.':
            manager.proof = True
        if statement =='Qed.' or statement == 'Admitted.' or statement == 'Save.' or statement == 'Defined.' or statement == 'Abort.':
            manager.proof = False
        print("sending:", statement)
        manager.send(statement, region=r)


class CoqtopSuccessCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view
        key, _, r = manager.statements[-1]
        coqfile_view.add_regions(key, [r], 'meta.coq.proven')
        manager.position = r.end() + 1


class CoqUndoStatementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        coqfile_view = manager.file_view
        if manager.proof:
            key, statement, _ = manager.statements.pop()
            if statement == 'Proof.':
                print(str(statement))
                coqfile_view.erase_regions(key)
                manager.position = int(key)
                key, statement, _ = manager.statements.pop()
                manager.send('Abort.', undo=True)
                print("sending: Abort.")
                manager.proof = False
            elif statement[0].islower():
                print("sending: Undo.")
                manager.send('Undo.', undo=True)
            print(str(statement))
            coqfile_view.erase_regions(key)
            manager.position = int(key)


class CoqContext(sublime_plugin.EventListener):
    def on_close(self, view):
        if view == manager.output_view:
            for key, _, _ in manager.statements:
                manager.file_view.erase_regions(key)
            manager.__init__()

    def on_selection_modified(self, view):
        if view.settings().get('coqtop_running') == True:
            regions = []
            for key, _, _ in manager.statements:
                regions += view.get_regions(key)
            selection = view.sel()
            view.set_read_only(False)
            for region in regions:
                for selected in selection:
                    if region.intersects(selected):
                        view.set_read_only(True)
                        break