export function renderSlot(slots, name = 'default', fallback = []) {
  const slot = slots?.[name];
  return typeof slot === 'function' ? slot() : fallback;
}
