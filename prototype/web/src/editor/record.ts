// Step recording and replay (design/event-log.md §5). The editor records every
// step of every doc-changing transaction, appended ones included, in order.
// Replaying those steps from the start document must give the same document in
// the browser and in the Python replay (engine/replay, D6, D33).
import { Plugin, PluginKey } from "@tiptap/pm/state";
import { Step } from "@tiptap/pm/transform";
import { Node as PMNode, type Schema } from "@tiptap/pm/model";

export type JsonObject = { [key: string]: unknown };

export interface StepLog {
  start: JsonObject;
  steps: JsonObject[];
}

export const recordKey = new PluginKey<StepLog>("wr-record");

/**
 * prosemirror-transform 1.12 inverts an addMark that replaced an excluded mark
 * (our origin marks exclude each other) into a `markSet` step, and redo can nest
 * one markSet in another. Nested markSet JSON does not load back
 * (MarkSetStep.fromJSON accepts only addMark/removeMark children), and
 * prosemirror-py has no markSet at all. Its children are mark steps applied in
 * order and never move positions, so the log stores them flat: the log only
 * holds step types both replays know.
 */
export function flattenStepJson(json: JsonObject): JsonObject[] {
  if (json.stepType !== "markSet") return [json];
  return (json.steps as JsonObject[]).flatMap(flattenStepJson);
}

/** Records { start, steps }. The log object is mutated in place (spike; M1 batches it to the server). */
export function recordPlugin(): Plugin<StepLog> {
  return new Plugin<StepLog>({
    key: recordKey,
    state: {
      init: (_config, state) => ({ start: state.doc.toJSON() as JsonObject, steps: [] }),
      apply(tr, log) {
        for (const step of tr.steps) log.steps.push(...flattenStepJson(step.toJSON() as JsonObject));
        return log;
      },
    },
  });
}

export class ReplayError extends Error {}

export function replaySteps(schema: Schema, start: JsonObject, steps: readonly JsonObject[]): PMNode {
  let doc = PMNode.fromJSON(schema, start);
  steps.forEach((json, i) => {
    const result = Step.fromJSON(schema, json).apply(doc);
    if (result.failed || !result.doc) throw new ReplayError(`step ${i}: ${result.failed}`);
    doc = result.doc;
  });
  doc.check();
  return doc;
}
