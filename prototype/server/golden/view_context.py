"""Synthetic receipt display context. Recorded relationships only; no new provenance rules.

Document positions are ProseMirror UTF-16 positions. Historical spans are mapped
back through actual steps; paragraph ordinal IDs never establish correspondence.
"""
from __future__ import annotations

from difflib import SequenceMatcher

from prosemirror.model import Node
from prosemirror.transform import Step

from engine.provenance.bands import NOTE_TEXT, walk_textblocks
from engine.provenance.trail import build_trail
from engine.receipt.wording import WordingFilter
from engine.replay import EMPTY_DOC, load_schema

from .script import load_blocks

_FALLBACK = 'Text omitted by the wording policy.'
_BREAKS = {
    'no_link': 'No card links here.',
    'claim_not_found': 'The recorded claim is unavailable.',
    'claim_has_no_cards': 'No card links here.',
    'card_not_found': 'The recorded card is unavailable.',
    'card_pasted': 'Pasted into a card; its source link is not checked.',
    'card_not_anchored': 'This card has no source anchor.',
}


def _clean(text):
    return WordingFilter().apply(str(text), _FALLBACK)


def _ref(event):
    # Display precision is date + hour, never fine-grained input timing.
    return {'seq': event['seq'], 'type': event['type'], 'at': event['ts'][:13] + ':00Z'}


def _text_between(doc, start, end):
    return '\n'.join(''.join(ch for ch, pos in zip(b.text, b.pos) if start <= pos < end)
                     for b in walk_textblocks(doc) if b.start < end and b.end > start)


def _events(events, types, key, value):
    return [_ref(e) for e in events
            if e['type'] in types and e['payload'].get(key) == value]


def _contains_claim(value, claim_id):
    if isinstance(value, dict):
        return value.get('claim_id') == claim_id or any(
            _contains_claim(v, claim_id) for v in value.values())
    return isinstance(value, list) and any(_contains_claim(v, claim_id) for v in value)


def _history(events, sentences, final_doc):
    schema = load_schema()
    doc = Node.from_json(schema, EMPTY_DOC)
    batches = []
    for event in events:
        if event['type'] != 'editor.batch':
            continue
        maps = []
        for raw in event['payload']['steps']:
            step = Step.from_json(schema, raw)
            result = step.apply(doc)
            if result.failed or result.doc is None:
                return {s['id']: ([], 'Recorded draft spans could not be replayed.') for s in sentences}
            maps.append(step.get_map())
            doc = result.doc
        batches.append((event, doc, maps))
    # A mismatch browser copy has no reliable positional correspondence to replay.
    if doc.to_json() != final_doc:
        return {s['id']: ([], 'Recorded positions do not match the submitted browser copy.')
                for s in sentences}
    out = {}
    for sentence in sentences:
        start, end = sentence['from'], sentence['to']
        versions = []
        lost = False
        for event, snapshot, maps in reversed(batches):
            if not lost:
                text = _text_between(snapshot, start, end)
                if text:
                    versions.append({'doc_rev': event['doc_rev'], 'text': text,
                                     'events': [_ref(event)], 'added': '', 'removed': ''})
            for mapping in reversed(maps):
                a = mapping.invert().map_result(start, 1)
                b = mapping.invert().map_result(end, -1)
                if a.deleted_across or b.deleted_across or a.pos >= b.pos:
                    lost = True
                start, end = a.pos, b.pos
        versions.reverse()
        # Keep the earliest recorded revision for each changed wording, so a later
        # unrelated batch cannot be presented as the event that introduced it.
        versions = [v for i, v in enumerate(versions)
                    if i == 0 or v['text'] != versions[i - 1]['text']]
        for previous, current in zip(versions, versions[1:]):
            added, removed = [], []
            for tag, i, j, k, l in SequenceMatcher(None, previous['text'], current['text']).get_opcodes():
                if tag in ('insert', 'replace'):
                    added.append(current['text'][k:l])
                if tag in ('delete', 'replace'):
                    removed.append(previous['text'][i:j])
            current['added'], current['removed'] = ''.join(added), ''.join(removed)
        for v in versions:
            v['text'], v['added'], v['removed'] = map(_clean, (v['text'], v['added'], v['removed']))
        note = ('Only spans supported by recorded position mapping are shown. Earlier wording is unavailable.'
                if lost else 'Draft spans are mapped through recorded steps; no earlier wording is inferred.')
        out[sentence['id']] = (versions, note)
    return out


def build_view_context(result, script, index):
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError('synthetic index must be a nonnegative integer')
    events = [e for e in result.events if e['seq'] <= result.seal_seq]
    trail = build_trail(events)
    blocks = load_blocks()
    textblocks = {b.id: b for b in walk_textblocks(result.doc)}
    histories = _history(events, result.l1['sentences'], result.doc)
    source_titles = {e['payload']['source_id']: e['payload']['title'] for e in events
                     if e['type'] == 'source.add'}
    submit = next(e for e in events if e['type'] == 'submit' and e['hash'] == result.seal)
    sentences = []
    for sentence in result.l1['sentences']:
        text = _text_between(result.doc, sentence['from'], sentence['to'])
        steps, notes, seen = [], [], set()

        def add(kind, identifier, label, body, refs, relationship):
            key = (kind, identifier, relationship)
            if key in seen:
                return
            seen.add(key)
            steps.append({'kind': kind, 'id': identifier, 'label': _clean(label),
                          'text': _clean(body), 'events': refs,
                          'relationship': relationship})

        def source(bid, relationship):
            block = blocks.get(bid)
            if block is None:
                notes.append('The referenced passage is unavailable.')
                return
            sid = block['source_id']
            refs = _events(events, {'source.add'}, 'source_id', sid)
            refs += _events(events, {'card.anchor', 'editor.insert_quote'}, 'block_id', bid)
            add('source', bid, source_titles.get(sid, sid), block['text'], refs, relationship)

        for mark in sentence['marks']:
            kind, ref = mark['kind'], mark['ref']
            if not mark['confirmed']:
                notes.append("This label couldn't be confirmed against its source.")
                continue
            if kind == 'quote':
                source(ref, 'Text label confirmed against this source passage.')
            elif kind == 'coach':
                asks = [e for e in events if e['type'] == 'coach.ask' and e['payload'].get('q_id') == ref]
                answers = [e for e in events if e['type'] == 'coach.outcome' and e['payload'].get('q_id') == ref]
                body = ('Question: ' + asks[-1]['payload']['question'] + '\n') if asks else ''
                if answers:
                    answer = answers[-1]['payload']
                    raw = answer.get('answer_text') or ''
                    typed_parts = [raw[r['from']:r['to']] for r in answer.get('origin_runs', [])
                                   if r.get('kind') == 'typed']
                    body += 'Recorded typed answer portions: ' + '\n'.join(typed_parts)
                add('coach', ref, 'Coach exchange', body, [_ref(e) for e in asks + answers],
                    'Text label confirmed against a typed portion of the recorded answer.')
            elif kind == 'import':
                raw = (script.get('imports') or {}).get(ref)
                if raw:
                    add('import', ref, 'Declared outside help', raw['text'],
                        _events(events, {'import.declared'}, 'import_id', ref),
                        'The student declared this outside text.')
            elif kind == 'helper':
                output = (script.get('helper_outputs') or {}).get(ref)
                if output is not None:
                    add('helper', ref, 'References and formatting', output,
                        _events(events, {'helper.serve'}, 'helper_serve_id', ref),
                        'Confirmed Helper text; counted apart as mechanics.')

        for chain in sentence['chains']:
            claim = trail.claim(chain['claim_id'])
            if chain.get('break'):
                notes.append(_BREAKS.get(chain['break'], 'A recorded link is unavailable.'))
            for card_info in chain['cards']:
                card = trail.card(card_info['card_id'])
                if card is None or card.deleted:
                    notes.append('The recorded card is unavailable.')
                    continue
                for sid, bid in sorted(card.anchors):
                    source(bid, 'Card anchor recorded; this sentence link is not checked against the source.')
                add('card', card.card_id, 'Idea card', card.text,
                    _events(events, {'card.create', 'card.edit', 'card.anchor'}, 'card_id', card.card_id),
                    'Recorded card linked to this claim; it does not establish sentence support.')
                if card_info.get('break'):
                    notes.append(_BREAKS.get(card_info['break'], 'A recorded link is unavailable.'))
            if claim:
                if claim.kind == 'declared' and claim.import_id:
                    raw = (script.get('imports') or {}).get(claim.import_id)
                    if raw:
                        add('import', claim.import_id, 'Declared outside help', raw['text'],
                            _events(events, {'import.declared'}, 'import_id', claim.import_id),
                            'The student declared this outside text.')
                claim_refs = _events(events, {'claim.create', 'claim.edit', 'claim.extracted'}, 'claim_id', claim.claim_id)
                claim_refs += [_ref(e) for e in events if e['type'] == 'editor.batch'
                               and _contains_claim(e['payload']['steps'], claim.claim_id)]
                relationship = ('Linked by the student from a map suggestion; not checked.'
                                if chain.get('suggestion_id') else
                                'Linked by the student, not checked.' if chain['by'] == 'student' else
                                'Recorded paragraph link; no sentence support is inferred.')
                add('claim', claim.claim_id, 'Claim', claim.text, claim_refs, relationship)
        if sentence.get('chain_break'):
            notes.append(_BREAKS.get(sentence['chain_break'], 'A recorded link is unavailable.'))
        notes += [NOTE_TEXT[n] for n in sentence['notes'] if n in NOTE_TEXT]
        block = textblocks[sentence['paragraph_id']]
        paste_refs = {ref for pos, kind, ref in zip(block.pos, block.kinds, block.refs)
                      if sentence['from'] <= pos < sentence['to'] and kind == 'paste_ext' and ref}
        paste_events = [e for e in events if e['type'] == 'editor.paste'
                        and e['payload'].get('paste_id') in paste_refs]
        if sentence['mix']['paste_ext']:
            notes.append('Came in by paste; linked text is not checked.' if sentence['chains']
                         else 'Came in by paste; no source link is recorded.')
        final_refs = [_ref(submit)] + [_ref(e) for e in paste_events]
        add('final', sentence['id'], 'Final sentence', text, final_refs,
            'Submitted text as recorded.')
        versions, history_note = histories[sentence['id']]
        sentences.append({'id': sentence['id'], 'paragraph_id': sentence['paragraph_id'],
                          'from': sentence['from'], 'to': sentence['to'], 'text': _clean(text),
                          'band': sentence['band'], 'chain': {'steps': steps,
                          'notes': list(dict.fromkeys(notes)), 'history': versions,
                          'history_note': history_note}})
    return {'synthetic': True, 'header': {
                'student_name': f'Sample writer {index + 1:02d}',
                'assignment_title': 'Synthetic writing assignment',
                'submitted_at': submit['ts'], 'source_count': len(source_titles)},
            'paragraphs': [{'id': p['id'], 'text': _clean(textblocks[p['id']].text),
                            'sentence_ids': list(p['sentence_ids'])} for p in result.l1['paragraphs']],
            'sentences': sentences}
