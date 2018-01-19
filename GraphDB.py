import json
import bibtexparser as btx
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

class AMSRefsWriter(BibTexWriter):
    def _entry_to_bibtex(self, entry):
        bibtex = ''
        # Write BibTeX key
        bibtex += '\\bib{' + entry['ID'] + '}{' + entry['ENTRYTYPE'] + '}{'

        # create display_order of fields for this entry
        # first those keys which are both in self.display_order and in entry.keys
        display_order = [i for i in self.display_order if i in entry]
        # then all the other fields sorted alphabetically
        more_fields = [i for i in sorted(entry) if i not in self.display_order]
        display_order += [i for i in sorted(entry) if i not in self.display_order]

        # Write field = value lines
        for field in [i for i in display_order if i not in ['ENTRYTYPE', 'ID']]:
            try:
                if self.comma_first:
                    bibtex += "\n" + self.indent + ", " + "{0:<{1}}".format(field, self._max_field_width) + " = {" + entry[field] + "}"
                else:
                    bibtex += "\n" + self.indent + "{0:<{1}}".format(field, self._max_field_width) + " = {" + entry[field] + "},"
            except TypeError:
                raise TypeError(u"The field %s in entry %s must be a string"
                                % (field, entry['ID']))
        bibtex += "\n}\n" + self.entry_separator
        return bibtex

class GraphDB:
    _writer = AMSRefsWriter()
    _begin_minipage_left = "\\begin{minipage}[t][.9\\textheight]{.5\\textwidth}\n" + "\\vspace*{\\fill}"
    _begin_minipage_right = "\\begin{minipage}[t]{.5\\textwidth}\n" + "\\vspace{0pt}"
    _end_minipage = "\\end{minipage}"
    _begin_itemize = "\\begin{itemize}\n"
    _end_itemize = "\\end{itemize}"
    _item = "\\item[] "
    _begin_biblist = "\\begin{biblist}"
    _end_biblist = "\\end{biblist}"
    _latex_preamble = """ % THIS IS AN AUTOGENERATED DOCUMENT. DO NOT EDIT
\\documentclass[10pt]{book}
\\usepackage[margin=1cm, a5paper,verbose]{geometry}
\\usepackage{amsrefs}
\\usepackage{amsmath}
\\usepackage{mathpazo}
\\usepackage{eulervm}
\\usepackage{url}
\\usepackage{enumitem}
\\usepackage{graphicx}
\\graphicspath{ {Graphlopedia_2017-12-05-193532/figs/} }

\\renewcommand{\\refname}[1]{#1}
\\renewcommand\\bibsection[1]{\\subsubsection*{\\refname{#1}}}
\\renewcommand{\\bibdiv}[1]{\\bibsection{#1}}
\\makeatletter
\\newcommand\\psubsubsection{\\@startsection{subsubsection}{3}{\z@}
                                     {-3.25ex\\@plus -1ex \\@minus -.2ex}
                                     {-1.5ex \\@plus -.2ex}
                                     {\\normalfont\\normalsize\\bfseries}}
                                     
\\BibSpec{link}{
+{}{\\url} {url}
}
\\setlist[itemize]{leftmargin=*}
\\let\\olditemize\\itemize
\\let\\endolditemize\\enditemize
\\renewenvironment{itemize}{
    \\footnotesize
    \\olditemize
}{
    \\endolditemize
}\n
"""

    def __init__(self, graph_json):
        self._graph_json = graph_json
        self.graphs = graph_json["graphs"]
        self.description = graph_json["description"]

    def get_pyjson(self):
        return self._graph_json

    def _gen_tex(self, graph):
        ID = "\\section*{{\\sc {}}}".format(graph["id"])
        NAME = "\\subsection*{{\\sc {}}}".format(graph["name"])
        #minipage
        DEG_SEQ = "\\psubsubsection*{degree sequence}\n" + self._begin_itemize + self._item + "{}\n".format(graph["deg_seq"]) + self._end_itemize
        VERT = "\\psubsubsection*{vertices}\n" + "{{\\footnotesize {}}}\n".format(graph["num_vert"]) + "\\newline"
        EDGES = "\\psubsubsection*{edges}\n" + self._begin_itemize + self._item + "{}\n".format(graph["edges"]) + self._end_itemize
        lnk_num = 0
        if graph["links"]:
            for link in graph["links"]:
                lnk_num += 1
                link["ENTRYTYPE"] = "link"
                link["ID"] = graph["id"] + "L" + str(lnk_num)
            links_bib = BibDatabase()
            links_bib.entries = graph["links"]
            LINKS = "\\bibdiv{links}\n \\vspace{-1.5ex \\@plus -.2ex}\n" + self._begin_biblist + btx.dumps(links_bib,self._writer) + self._end_biblist
        else:
            LINKS = "\\bibdiv{links}\n \\vspace{-1.5ex \\@plus -.2ex}\n"
        if graph["refs"]:
            refs_bib = BibDatabase()
            refs_bib.entries = graph["refs"]
            REFS = "\\bibdiv{references}\n \\vspace{-1.5ex \\@plus -.2ex}\n" + self._begin_biblist + btx.dumps(refs_bib,self._writer) + self._end_biblist
        else:
            REFS = "\\bibdiv{references}\n \\vspace{-1.5ex \\@plus -.2ex}\n"
        if graph["comments"]:
            COMMENTS = "\\psubsubsection*{comments}\n" + self._begin_itemize + '\n'.join([self._item + comment for comment in graph["comments"]]) + self._end_itemize
        else:
            COMMENTS = "\\psubsubsection*{comments}\n"
        CONTRIB = "\\psubsubsection*{contributors}\n" + self._begin_itemize + '\n'.join([self._item + contrib["fi"] + " " + contrib["lname"] for contrib in graph["contrib"]]) + self._end_itemize
        #end minipage

        #minipage
        IMAGE = "\\centering\n" + "\\includegraphics[width=\\textwidth, height=6cm,keepaspectratio]{{{}}}".format(graph["images"][0]["src"])
        #end minipage

        return "\n".join([ID, NAME, self._begin_minipage_left, DEG_SEQ, VERT, EDGES, LINKS, REFS, COMMENTS, CONTRIB, self._end_minipage, self._begin_minipage_right, IMAGE, self._end_minipage, "\\newpage"])

    def build_latex(self, filename):
        with open(filename, 'w') as tfile:
            tfile.write(self._latex_preamble)
            tfile.write("\\begin{document}")
            for graph in self.graphs:
                tfile.write(self._gen_tex(graph))
            tfile.write("\\end{document}")


if __name__ == "__main__":
    with open('graphs.json') as sfile:
        graph_json = json.load(sfile)
        gdb = GraphDB(graph_json)

    gdb.build_latex('graphlopedia.tex')



