export function defineProps(definition = {}) { return definition; }
export function validateProps(props, definition = {}) {
  for (const [name, rule] of Object.entries(definition)) {
    if (rule?.required && !(name in props)) throw new Error(`Missing required prop: ${name}`);
  }
  return props;
}
