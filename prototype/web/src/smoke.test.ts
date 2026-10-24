import { expect, test } from "vitest";
import { APP_TITLE } from "./title";

test("app title", () => {
  expect(APP_TITLE).toBe("The Writing Room");
});
