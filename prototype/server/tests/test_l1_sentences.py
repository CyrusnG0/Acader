"""L1 sentence split rules (provenance.md section 3)."""
from engine.provenance import split_sentences, words


def sp(text):
    return [text[a:b] for a, b in split_sentences(text)]


def test_eg_and_ie_do_not_break():
    assert sp("Some tools, e.g. a hammer, help.") == ["Some tools, e.g. a hammer, help."]
    assert sp("A tool, i.e. The hammer, helps.") == ["A tool, i.e. The hammer, helps."]


def test_et_al_never_breaks():
    assert sp("Smith et al. (2019) found X. Next one.") == ["Smith et al. (2019) found X.",
                                                           "Next one."]
    assert len(sp("Smith et al. Found")) == 1


def test_decimals():
    assert sp("It rose 3.5 points. Then fell.") == ["It rose 3.5 points.", "Then fell."]


def test_initials_and_abbreviations():
    assert len(sp("U.S. policy changed.")) == 1
    assert len(sp("J. Smith wrote it.")) == 1
    assert len(sp("Dr. Smith came.")) == 1
    assert len(sp("See example.com for more.")) == 1


def test_closing_quote_stays_with_first_sentence():
    assert sp('He said "Stop." Then left.') == ['He said "Stop."', "Then left."]


def test_question_inside_quote_then_lowercase():
    assert sp('"Is it?" she asked.') == ['"Is it?" she asked.']


def test_ellipsis_capital_vs_lowercase():
    assert len(sp("Wait... Then")) == 2
    assert len(sp("wait... then")) == 1


def test_etc_boundary():
    assert len(sp("Apples, pears, etc. The rest.")) == 2
    assert len(sp("Apples, pears, etc. and more.")) == 1


def test_numbered_item_first_token_only():
    assert len(sp("1. First item")) == 1
    assert len(sp("Item 1. Second thing")) == 2


def test_hard_break_splits():
    assert sp("One line\nAnother line") == ["One line", "Another line"]


def test_trailing_sentence_without_terminator():
    assert sp("Done. And then more") == ["Done.", "And then more"]


def test_whitespace_trimmed():
    t = "  Leading.   Double  spaces here.  "
    assert sp(t) == ["Leading.", "Double  spaces here."]
    spans = split_sentences(t)
    assert spans[0] == (2, 10)


def test_whitespace_only_gives_nothing():
    assert split_sentences("   \n  ") == []
    assert split_sentences("") == []


def test_terminator_run():
    assert sp("Really?! Yes.") == ["Really?!", "Yes."]


def test_ellipsis_char():
    assert sp("Hmm… Maybe so.") == ["Hmm…", "Maybe so."]


def test_text_ending_in_dot_paren():
    assert sp("(See above.) Then more.") == ["(See above.)", "Then more."]
    assert sp("It ends (here.)") == ["It ends (here.)"]


def test_words():
    assert words("  a  b\tc ") == 3
    assert words("") == 0
