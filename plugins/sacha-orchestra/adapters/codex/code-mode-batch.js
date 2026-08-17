const CODE_MODE_CALLS = globalThis.CODE_MODE_CALLS;
const CODE_MODE_OUTPUT_LIMIT = globalThis.CODE_MODE_OUTPUT_LIMIT;
const CODE_MODE_SCHEMA_VERSION = 1;

if (!Array.isArray(CODE_MODE_CALLS) || CODE_MODE_CALLS.length < 2) {
  throw new Error("code_mode_calls_too_few");
}
if (!Number.isInteger(CODE_MODE_OUTPUT_LIMIT) || CODE_MODE_OUTPUT_LIMIT <= 0) {
  throw new Error("code_mode_output_limit_invalid");
}

const seenUnitIds = new Set();
const projectionFieldNames = ["result_fields", "reference_fields"];
for (const call of CODE_MODE_CALLS) {
  if (!call || typeof call.unit_id !== "string" || call.unit_id.length === 0) {
    throw new Error("code_mode_unit_id_invalid");
  }
  if (seenUnitIds.has(call.unit_id)) {
    throw new Error(`code_mode_unit_id_duplicate:${call.unit_id}`);
  }
  seenUnitIds.add(call.unit_id);
  if (typeof call.normalized_name !== "string" || call.normalized_name.length === 0) {
    throw new Error(`code_mode_tool_name_invalid:${call.unit_id}`);
  }
  for (const fieldName of projectionFieldNames) {
    const fields = call[fieldName];
    if (!Array.isArray(fields)
        || fields.some((field) => typeof field !== "string" || field.length === 0)) {
      throw new Error(`code_mode_projection_fields_invalid:${call.unit_id}:${fieldName}`);
    }
  }
}

const outcomeEnvelopeUpperBound = JSON.stringify({
  schema_version: CODE_MODE_SCHEMA_VERSION,
  status: "outcome_unknown",
  reason: "compact_output_limit_exceeded",
  units: CODE_MODE_CALLS.map((call) => ({
    unit_id: call.unit_id,
    status: "fulfilled",
  })),
});
if (outcomeEnvelopeUpperBound.length > CODE_MODE_OUTPUT_LIMIT) {
  throw new Error(`code_mode_output_limit_too_small:${outcomeEnvelopeUpperBound.length}`);
}

const prepared = CODE_MODE_CALLS.map((call) => {
  const matches = ALL_TOOLS.filter((tool) => tool.name === call.normalized_name);
  const callable = matches.length === 1 && typeof tools[call.normalized_name] === "function";
  return {
    call,
    resolution_error: callable
      ? null
      : `code_mode_tool_resolution_failed:${call.unit_id}:${call.normalized_name}:${matches.length}`,
  };
});
const resolutionErrors = prepared
  .map(({ resolution_error }) => resolution_error)
  .filter((error) => error !== null);
if (resolutionErrors.length > 0) {
  throw new Error(resolutionErrors.join("|"));
}

const tasks = prepared.map(({ call }) => tools[call.normalized_name](call.args));
const settled = await Promise.allSettled(tasks);

const pickFields = (value, fields) => {
  const selected = {};
  for (const field of fields) {
    if (value !== null && typeof value === "object"
        && Object.prototype.hasOwnProperty.call(value, field)) {
      selected[field] = value[field];
    }
  }
  return selected;
};

const results = settled.map((entry, index) => {
  const call = CODE_MODE_CALLS[index];
  if (entry.status === "fulfilled") {
    return {
      unit_id: call.unit_id,
      status: "fulfilled",
      value: pickFields(entry.value, call.result_fields),
      references: pickFields(entry.value, call.reference_fields),
    };
  }
  return {
    unit_id: call.unit_id,
    status: "rejected",
    error: String(entry.reason),
  };
});

let payload = {
  schema_version: CODE_MODE_SCHEMA_VERSION,
  status: "settled",
  results,
};
let encoded = JSON.stringify(payload);

if (encoded.length > CODE_MODE_OUTPUT_LIMIT) {
  payload = {
    schema_version: CODE_MODE_SCHEMA_VERSION,
    status: "output_limit_exceeded",
    results: results.map((result) => result.status === "fulfilled"
      ? {
          unit_id: result.unit_id,
          status: result.status,
          references: result.references,
          value_omitted: true,
        }
      : result),
  };
  encoded = JSON.stringify(payload);
}

if (encoded.length > CODE_MODE_OUTPUT_LIMIT) {
  encoded = JSON.stringify({
    schema_version: CODE_MODE_SCHEMA_VERSION,
    status: "outcome_unknown",
    reason: "compact_output_limit_exceeded",
    units: results.map((result) => ({
      unit_id: result.unit_id,
      status: result.status,
    })),
  });
}

if (encoded.length > CODE_MODE_OUTPUT_LIMIT) {
  throw new Error("code_mode_output_limit_invariant_failed");
}

text(encoded);
