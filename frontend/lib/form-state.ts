export type SubmittedValues = Record<string, string>;

export function submittedValues(formData: FormData): SubmittedValues {
  return Object.fromEntries(
    [...formData.entries()]
      .filter((entry): entry is [string, string] => typeof entry[1] === "string"),
  );
}

export function restoredValue(values: SubmittedValues, name: string, fallback: string): string {
  return values[name] ?? fallback;
}
