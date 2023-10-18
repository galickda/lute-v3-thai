from lute.models.language import Language
from lute.models.term import Term, Status
from lute.read.render.text_token import TextToken

class RenderableCalculator:

    def _assert_texttokens_are_contiguous(self, texttokens):
        prevtok = None
        for tok in texttokens:
            if prevtok is not None and prevtok.order != (tok.order - 1):
                mparts = [prevtok.tok_text, prevtok.order, tok.tok_text, tok.order]
                msg = '; '.join(map(str, mparts))
                raise Exception(f"bad token ordering: {msg}")
            prevtok = tok


    def _get_renderable(self, language, terms, texttokens):
        texttokens.sort(key=lambda x: x.order)
        self._assert_texttokens_are_contiguous(texttokens)

        candidateID = 0
        candidates = {}

        rendered = {}

        for tok in texttokens:
            rc = RenderableCandidate()
            candidateID += 1
            rc.id = candidateID
            rc.term = None
            rc.displaytext = tok.tok_text
            rc.text = tok.tok_text
            rc.pos = tok.order
            rc.length = 1
            rc.isword = tok.is_word
            candidates[candidateID] = rc
            rendered[rc.pos] = candidateID

        termcandidates = []
        firstorder = texttokens[0].order
        toktext = [tok.tok_text for tok in texttokens]
        subject = TokenLocator.make_string(toktext)
        tocloc = TokenLocator(language, subject)

        for term in terms:
            tlc = term.getTextLC()
            wtokencount = term.token_count
            locations = tocloc.locate_string(tlc)

            for loc in locations:
                rc = RenderableCandidate()
                candidateID += 1
                rc.id = candidateID

                matchtext, index = loc
                rc.term = term
                rc.displaytext = matchtext
                rc.text = matchtext
                rc.pos = firstorder + index
                rc.length = wtokencount
                rc.isword = 1

                termcandidates.append(rc)
                candidates[candidateID] = rc

        termcandidates.sort(key=lambda x: (-x.length, x.pos))

        for tc in termcandidates:
            for i in range(tc.length):
                rendered[tc.pos + i] = tc.id

        rcids = list(set(rendered))
        print('rcids = ')
        ret = [candidates[rcid] for rcid in rcids]
        return ret

    def _sort_by_order_and_tokencount(self, items):
        items.sort(key=lambda x: (x.pos, -x.length))
        return items

    def _calc_overlaps(self, items):
        for i in range(1, len(items)):
            prev = items[i - 1]
            curr = items[i]

            prevterm_last_token_pos = prev.pos + prev.length - 1
            overlap = prevterm_last_token_pos - curr.pos + 1

            if overlap > 0:
                zws = chr(0x200B)
                curr_tokens = curr.text.split(zws)
                show = curr_tokens[overlap:]
                curr.displaytext = zws.join(show)

        return items

    def main(self, language, words, texttokens):
        renderable = self._get_renderable(language, words, texttokens)
        items = self._sort_by_order_and_tokencount(renderable)
        items = self._calc_overlaps(items)
        return items

    @staticmethod
    def get_renderable(lang, words, texttokens):
        rc = RenderableCalculator()
        return rc.main(lang, words, texttokens)


class RenderableCandidate:
    def __init__(self):
        self.id: int
        self.term: Term = None
        self.display_text: str  # Text to show, if there is any overlap
        self.text: str  # Actual text of the term
        self.pos: int
        self.length: int
        self.is_word: int
        self.hides: list = []
        self.render: bool = True

    @property
    def term_id(self) -> int:
        if self.term is None:
            return None
        return self.term.id

    @property
    def order_end(self) -> int:
        return self.pos + self.length - 1

    def to_string(self) -> str:
        render_str = 'true' if self.render else 'false'
        term_id = self.term.id if self.term is not None else '-'
        return f"{term_id}; {self.text}; {self.pos}; {self.length}; render = {render_str}"

    def make_text_item(self, p_num: int, se_id: int, text_id: int, lang: Language):
        t = TextItem()
        t.order = self.pos
        t.text_id = text_id
        t.lang_id = lang.get_lg_id()
        t.display_text = self.display_text
        t.text = self.text
        t.token_count = self.length
        t.text_lc = lang.get_lowercase(self.text)
        t.para_id = p_num
        t.se_id = se_id
        t.is_word = self.is_word
        t.text_length = len(self.text)

        if self.term is None:
            return t

        t.wo_id = self.term.get_id()
        t.wo_status = self.term.get_status()
        t.flash_message = self.term.get_flash_message()

        def has_extra(cterm):
            if cterm is None:
                return False
            no_extra = (
                cterm.get_translation() is None and
                cterm.get_romanization() is None and
                cterm.get_current_image() is None
            )
            return not no_extra

        show_tooltip = has_extra(self.term)
        for p in self.term.get_parents():
            show_tooltip = show_tooltip or has_extra(p)
        t.show_tooltip = show_tooltip

        return t


class TokenLocator:
    @staticmethod
    def make_string(text):
        return "".join(text)

    def __init__(self, language, subject):
        pass


class TextItem:
    def __init__(self):
        self.text_id: int
        self.lang_id: int
        self.order: int
        self.text: str  # The original, un-overlapped text.
        self.display_text: str  # The actual text to display on screen.
        # If part of the text has been overlapped by a
        # prior token, this will be different from Text.
        self.token_count: int
        self.text_lc: str
        self.para_id: int
        self.se_id: int
        self.is_word: int
        self.text_length: int
        # The tooltip should be shown for well-known/ignored TextItems
        # that merit a tooltip. e.g., if there isn't any actual Term
        # entity associated with this TextItem, nothing more is needed.
        # Also, if there is a Term entity but it's mostly empty, a
        # tooltip isn't useful.
        self.show_tooltip: bool = False
        self.wo_id: int = None
        self.wo_status: int = None
        self.flash_message: str = None

    def get_html_display_text(self) -> str:
        zws = chr(0x200B)
        return self.display_text.replace(zws, '').replace(' ', '&nbsp;')

    def get_span_id(self) -> str:
        parts = [
            'ID',
            str(self.order),
            str(max(1, self.token_count))
        ]
        return '-'.join(parts)

    def get_html_class_string(self) -> str:
        if self.is_word == 0:
            return "textitem"

        if self.wo_id is None:
            classes = ['textitem', 'click', 'word', 'status0']
            return ' '.join(classes)

        st = self.wo_status
        classes = [
            'textitem', 'click', 'word',
            'word' + str(self.wo_id), 'status' + str(st)
        ]

        tooltip = (
            st != Status.WELLKNOWN and st != Status.IGNORED or
            self.show_tooltip or
            self.flash_message is not None
        )
        if tooltip:
            classes.append('showtooltip')

        if self.flash_message is not None:
            classes.append('hasflash')

        if self.display_text != self.text:
            classes.append('overlapped')

        return ' '.join(classes)
