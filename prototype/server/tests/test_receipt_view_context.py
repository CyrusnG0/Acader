"""Receipt evidence adapters preserve actual sentence/relationship semantics."""
import copy

from golden.build import build_session
from golden.script import load_script
from golden.view_context import build_view_context


def view(sid):
    result = build_session(sid)
    return result, build_view_context(result, load_script(sid), 0)


def sentence(context, sid):
    return next(s for s in context['sentences'] if s['id'] == sid)


def test_source_path_is_confirmed_only_for_checked_quote():
    result, context = view('honest-nursing')
    traced = sentence(context, 's1')
    linked = sentence(context, 's2')
    assert traced['text'] == 'Fukuda and colleagues report that a CNS head nurse was associated with lower ICU mortality in their ICU.'
    assert {s['kind'] for s in traced['chain']['steps']} >= {'source', 'card', 'claim', 'final'}
    assert any('Text label confirmed' in s['relationship'] for s in traced['chain']['steps'])
    assert not any('Text label confirmed' in s['relationship'] for s in linked['chain']['steps'])
    assert any(s['relationship'] == 'Linked by the student, not checked.' for s in linked['chain']['steps'])
    seqs = {e['seq'] for e in result.events}
    assert all(ref['seq'] in seqs for s in context['sentences'] for st in s['chain']['steps'] for ref in st['events'])
    assert all(ref['at'].endswith(':00Z') for s in context['sentences'] for st in s['chain']['steps'] for ref in st['events'])


def test_coach_path_uses_recorded_answer_and_question():
    _, context = view('honest-nursing')
    coach = next(s for s in sentence(context, 's4')['chain']['steps'] if s['kind'] == 'coach')
    assert coach['id'] == 'q1'
    assert 'similar open ICU without intensivists running care' in coach['text']
    assert {r['type'] for r in coach['events']} == {'coach.ask', 'coach.outcome'}


def test_failed_marks_do_not_become_confirmed_paths():
    _, context = view('forged-marks')
    for sid in ('s1', 's3'):
        target = sentence(context, sid)
        assert any("couldn't be confirmed" in n for n in target['chain']['notes'])
        assert not any('Text label confirmed' in step['relationship'] for step in target['chain']['steps'])


def test_declared_help_is_explicit_and_suggestion_remains_unchecked():
    _, declared = view('declared-outside')
    imported = next(s for s in sentence(declared, 's1')['chain']['steps'] if s['kind'] == 'import')
    assert imported['id'] == 'imp1'
    assert any(r['type'] == 'import.declared' for r in imported['events'])
    _, suggested = view('accepted-suggestion-paste')
    first = sentence(suggested, 's1')
    assert first['band'] == 'untraced'
    assert any('map suggestion; not checked' in s['relationship'] for s in first['chain']['steps'])
    assert not any('map.suggestion' == ref['type'] for s in first['chain']['steps'] for ref in s['events'])


def test_edit_above_maps_positions_instead_of_paragraph_identity():
    _, context = view('edit-above-linked')
    last = context['sentences'][-1]
    assert last['paragraph_id'] == 'p2'
    assert last['text'] == 'The study was based in a single institution and limits generalization.'
    assert last['chain']['history']
    assert all(h['text'] == last['text'] for h in last['chain']['history'])
    assert any(s['id'] == 'nursing.p7.limitation' for s in last['chain']['steps'])


def test_browser_copy_mismatch_does_not_invent_history():
    result = build_session('honest-nursing')
    result = copy.copy(result)
    result.doc = {'type':'doc','content':[{'type':'paragraph','attrs':{'links':[]},'content':[{'type':'text','text':'Changed browser copy.'}]}]}
    # Restrict the derived display fixture to its corresponding actual span.
    result.l1 = copy.deepcopy(result.l1)
    result.l1['paragraphs'] = [{'id':'p1','sentence_ids':['s1']}]
    result.l1['sentences'] = [dict(result.l1['sentences'][0], **{'from':1,'to':22,'paragraph_id':'p1'})]
    context = build_view_context(result, load_script('honest-nursing'), 0)
    assert context['sentences'][0]['chain']['history'] == []
    assert 'do not match' in context['sentences'][0]['chain']['history_note']


def test_helper_mechanics_references_its_real_output():
    _, context = view('reference-list')
    mechanics = next(s for s in context['sentences'] if s['band'] == 'mechanics')
    assert any(s['kind'] == 'helper' and s['id'] == 'h1' for s in mechanics['chain']['steps'])


def test_mixed_coach_answer_never_labels_pasted_parts_as_typed():
    result, context = view('coach-paste-moved')
    answer = next(e['payload'] for e in result.events if e['type'] == 'coach.outcome')
    pasted = [answer['answer_text'][r['from']:r['to']] for r in answer['origin_runs'] if r['kind'] == 'paste_ext']
    coach = next(step for s in context['sentences'] for step in s['chain']['steps'] if step['kind'] == 'coach')
    assert all(part not in coach['text'] for part in pasted)
    assert 'typed portion' in coach['relationship']


def test_changed_draft_span_cites_first_revision_that_contains_the_edit():
    result, context = view('elaborating-honest')
    versions = sentence(context, 's1')['chain']['history']
    assert [v['doc_rev'] for v in versions] == [2, 20]
    assert versions[-1]['added'] == ', in this one ICU'
    assert versions[-1]['removed'] == ''
    assert versions[-1]['events'][0]['seq'] == next(e['seq'] for e in result.events if e['type']=='editor.batch' and e['doc_rev']==20)
