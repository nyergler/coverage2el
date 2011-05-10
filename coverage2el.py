
import os.path
from coverage import coverage, summary, misc

class ElispReporter(summary.SummaryReporter):
    def report(self):
        try:
            # coverage-3.4 has both omit= and include= . include= is applied
            # first, then omit= removes items from what's left. These are
            # tested with fnmatch, against fully-qualified filenames.
            self.find_code_units(None,
                                 omit=[os.path.abspath("src/allmydata/test/*")],
                                 include=[os.path.abspath("src/allmydata/*")])
        except TypeError:
            # coverage-3.3 only had omit=
            self.find_code_units(None, ["/System", "/Library", "/usr/lib",
                                        "support/lib", "src/allmydata/test"])

        out = open(".coverage.el", "w")
        out.write("""
;; This is an elisp-readable form of the figleaf coverage data. It defines a
;; single top-level hash table in which the key is an asolute pathname, and
;; the value is a three-element list. The first element of this list is a
;; list of line numbers that represent actual code statements. The second is
;; a list of line numbers for lines which got used during the unit test. The
;; third is a list of line numbers for code lines that were not covered
;; (since 'code' and 'covered' start as sets, this last list is equal to
;; 'code - covered').

    """)
        out.write("(let ((results (make-hash-table :test 'equal)))\n")
        for cu in self.code_units:
            f = cu.filename
            try:
                (fn, executable, missing, mf) = self.coverage.analysis(cu)
            except misc.NoSource:
                continue
            code_linenumbers = executable
            uncovered_code = missing
            covered_linenumbers = sorted(set(executable) - set(missing))
            out.write(" (puthash \"%s\" '((%s) (%s) (%s)) results)\n"
                      % (f,
                         " ".join([str(ln) for ln in sorted(code_linenumbers)]),
                         " ".join([str(ln) for ln in sorted(covered_linenumbers)]),
                         " ".join([str(ln) for ln in sorted(uncovered_code)]),
                         ))
        out.write(" results)\n")
        out.close()

def main():
    c = coverage()
    c.load()
    ElispReporter(c).report()

if __name__ == '__main__':
    main()


